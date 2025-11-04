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


def respond(message: str, history: list[tuple]):
    if not message:
        return ""
    print(f"[gradio_app] User: {message}")
    #TODO: add support for history in agent calls 
    if _agent is None:
        bot_text = "Agent not available (failed to initialize). Check logs."
        return bot_text

    try:
        result = _agent(question=message, initial_schema="")
    except Exception as e:
        result = e

    bot_text = _extract_text_from_result(result)
    print(f"[gradio_app] Bot: {bot_text}")
    return bot_text


demo = gr.ChatInterface(respond, type="messages")
demo.launch()