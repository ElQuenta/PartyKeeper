import sqlite3
import gradio as gr
import os

from agent import create_agent


try:
    priorities_env = os.getenv("RAG_PRIORITIES")
    priorities = priorities_env.split(",") if priorities_env else None
    _agent = create_agent(priorities=priorities)
except Exception as e:
    print("[gradio_app] Warning: failed to create agent at import time:", e)


def _extract_text_from_result(result) -> str:
    if result is None:
        return "(no response from agent)"
    if isinstance(result, str):
        return result
    # Common attribute names
    for attr in ("answer", "text", "output", "result"):
        if hasattr(result, attr):
            try:
                return str(getattr(result, attr))
            except Exception:
                pass
    # dict-like
    try:
        if isinstance(result, dict):
            for k in ("answer", "text", "output", "result"):
                if k in result:
                    return str(result[k])
    except Exception:
        pass
    return str(result)


def respond(message: str, history: list[tuple]) -> tuple[list[tuple], str]:
    """Handle a user message from the Gradio UI, call the agent and return
    an updated history plus an empty string to clear the input box.
    """
    if not message:
        return history, ""

    if _agent is None:
        bot_text = "Agent not available (failed to initialize). Check logs."
        history = history + [(message, bot_text)]
        return history, ""

    # Call the agent through the module callable (preferred over forward()).
    try:
        result = _agent(question=message, initial_schema="")
    except Exception as e:
        result = e

    bot_text = _extract_text_from_result(result)
    history = history + [(message, bot_text)]
    return history, ""


demo = gr.ChatInterface(respond, type="messages")
demo.launch()