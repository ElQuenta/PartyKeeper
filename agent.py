import dspy
import sqlite3
from dotenv import load_dotenv

from tools.rag.principalTool import rag_tool
from tools.webSearch.principalTool import web_search_tool as web_search_tool_fn


# --- DSPy Agent Definition ---
class DDAgentSignature(dspy.Signature):
    """
    PRIMARY ROLE PROMPT (use as the agent's system role when a strict, role-based
    decision-support response is desired):

    You are an Expert Darkest Dungeon Advisor. Your role is to provide clear,
    actionable, and concise decision-support for players of Darkest Dungeon (and
    Darkest Dungeon II where relevant). Always act as an advisor to the player —
    do not act as the player. Focus on survival, stress management, resource
    preservation, and risk minimization. When possible, use available tools to
    fetch accurate game data (hero stats, item effects, enemy weaknesses) and
    explicitly cite the tool used (e.g. "fallback: local_search" or
    "fallback: web_search").

    Required response format (follow exactly when giving a primary answer):
    1) Short Recommendation (1-2 sentences): a direct action recommendation.
    2) Ordered Steps (3-6 items): numbered, prioritized actions to take now.
    3) Justification: concise reasoning referencing relevant game facts
       (HP, stress, quirks, resistances, environmental modifiers, known enemy
       mechanics). If facts are unknown, state which facts are missing.
    4) Risk Assessment: Low / Medium / High and expected consequences.
    5) Resource Guidance: which consumables or trinkets to use or conserve.
    6) Confidence (0-100): when <60, recommend verification steps or tools.

    INITIAL SCHEMA PROMPT (more open / permissive — use when the caller wants
    a looser, conversational assistant that can ask clarifying questions):

    You are a helpful Darkest Dungeon advisor. Offer suggestions, possible
    strategies, and alternatives. Ask follow-up questions when necessary to
    clarify missing information (e.g., exact HP, stress, quirks, inventory,
    or location). You may provide short lists of options and trade-offs without
    strictly enforcing the structured primary format. If confident, give a
    recommended action and reasons; otherwise propose multiple plausible
    options and request more details.
    """

    question = dspy.InputField(desc="The user's natural language question.")
    initial_schema = dspy.InputField(desc="Optional system/role prompt; if empty the caller may choose which prompt to apply.")
    answer = dspy.OutputField(
        desc="The final, natural language answer to the user's question."
    )


class DDAgent(dspy.Module):
    def __init__(self, tools: list[dspy.Tool], tool_funcs: dict | None = None, priorities: list[str] | None = None):
        super().__init__()
        # Initialize the ReAct agent.
        self.agent = dspy.ReAct(
            DDAgentSignature,
            tools=tools,
            max_iters=7,  # Set a max number of steps
        )
        # Map of tool name -> callable (e.g. 'local_search' -> rag_tool)
        self.tool_funcs = tool_funcs or {}
        # Order in which tools should be tried as fallbacks
        self.priorities = priorities or ["local_search", "web_search"]

    def _is_satisfactory(self, result) -> bool:
        """Very small heuristic to detect unsatisfactory answers.

        Returns False when the result is empty, too short, or contains
        common "I don't know" phrases.
        """
        if result is None:
            return False
        text = None
        # try to extract text from common structures
        if isinstance(result, str):
            text = result
        else:
            for attr in ("answer", "text", "output", "result"):
                if hasattr(result, attr):
                    try:
                        text = str(getattr(result, attr))
                        break
                    except Exception:
                        pass
            if text is None:
                try:
                    if isinstance(result, dict):
                        for k in ("answer", "text", "output", "result"):
                            if k in result:
                                text = str(result[k])
                                break
                except Exception:
                    pass

        if not text:
            return False
        txt = text.strip().lower()
        if len(txt) < 5:
            return False
        negative_phrases = ["i don't know", "i do not know", "don't know", "no idea", "can't", "cannot", "unable to", "i'm not sure", "i am not sure"]
        for p in negative_phrases:
            if p in txt:
                return False
        return True

    def forward(self, question: str, initial_schema: str) -> dspy.Prediction:
        """The forward pass of the module.

        Calls the underlying agent, and if the answer seems unsatisfactory,
        runs the configured tools directly in priority order and returns the
        first non-empty tool output (wrapped in a dict with a `fallback` flag).
        """
        result = self.agent(question=question, initial_schema=initial_schema)

        if self._is_satisfactory(result):
            return result

        # Agent result not satisfactory — try tools in priority order.
        for name in self.priorities:
            fn = self.tool_funcs.get(name)
            if not fn:
                continue
            try:
                tool_out = fn(question)
            except Exception as e:
                tool_out = e
            # simple acceptance check
            if tool_out is None:
                continue
            if isinstance(tool_out, str) and tool_out.strip() == "":
                continue
            # return a small structured result indicating a fallback was used
            return {"fallback": True, "tool": name, "answer": tool_out}

        # no useful fallback — return the original agent result
        return result


def configure_llm():
    """Configures the DSPy language model."""
    load_dotenv()
    llm = dspy.LM(model="openai/gpt-4o-mini", max_tokens=5000)
    dspy.settings.configure(lm=llm)

    print("[Agent] DSPy configured with gpt-4o-mini model.")
    return llm


def create_agent(priorities: list[str] | None = None) -> dspy.Module | None:
    """Create and return the DDAgent instance.

    priorities: optional list controlling fallback order (e.g. ["local_search", "web_search"]).
    """
    if not configure_llm():
        return

    web_search_tool = dspy.Tool(
        name="web_search",
        # ===> (1.1.2) YOUR web_search_tool TOOL DESCRIPTION HERE
        desc="Executes a web search using only the provided keywords, focusing on gathering broad, general information rather than precise or detailed results. Example: Instead of searching for 'Darkest Dungeon Crate interaction without cleansing effects details,' it simply searches for 'crate.'",
        func=lambda query: web_search_tool_fn(query),
    )

    local_search_tool = dspy.Tool(
        name="local_search",
        # ===> (1.1.2) YOUR local_search_tool TOOL DESCRIPTION HERE
        desc="Executes a local search based solely on the provided keywords, retrieving general contextual information instead of targeting specific data. Example: Instead of searching for 'Darkest Dungeon Crate interaction without cleansing effects details,' it simply searches for 'crate.'",
        func=lambda query: rag_tool(query),
    )

    all_tools = [web_search_tool, local_search_tool]

    # 2. Instantiate and run the agent. Provide the underlying callables and
    # a default priority order so DDAgent can run fallbacks when needed.
    tool_funcs = {"web_search": web_search_tool_fn, "local_search": rag_tool}
    priorities = priorities or ["local_search", "web_search"]

    agent = DDAgent(tools=all_tools, tool_funcs=tool_funcs, priorities=priorities)

    return agent