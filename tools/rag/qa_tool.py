from typing import List, Tuple
from pathlib import Path


def answer_from_snippets(snippets: List[Tuple[Path, str, int]], query: str) -> str:

    if not snippets:
        return "No relevant information found in local knowledge files."

    parts = [f"Query: {query}\n"]
    parts.append("Top results:\n")
    for path, snip, score in snippets:
        parts.append(f"- {path.relative_to(path.parents[2])} (score={score})\n")
        preview = snip.replace("\n", " ")
        if len(preview) > 400:
            preview = preview[:400].rsplit(" ", 1)[0] + "..."
        parts.append(f"  {preview}\n")

    parts.append("\nAnswer (combined snippets):\n")
    combined = "\n\n".join(s for _, s, _ in snippets)
    if len(combined) > 3000:
        combined = combined[:3000] + "..."

    parts.append(combined)
    return "\n".join(parts)
