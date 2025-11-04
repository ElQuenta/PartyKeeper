"""Main entry for the local RAG toolset.

This module exposes a `rag_tool(query, top=3)` function for programmatic use and a
`main()` CLI for simple testing. It uses the small local corpus under
`wiki_menu_data/` and performs a keyword-based retrieval plus a naive
composition of snippets into an answer.

Example (CLI):
	python -m tools.rag.principalTool "what are curios"

The implementation is intentionally dependency-free and suitable for demo/teaching.
"""

from pathlib import Path
import argparse
from .file_loader import load_corpus
from .retriever import retrieve
from .qa_tool import answer_from_snippets
from typing import Dict, Any


def rag_tool(query: str, top: int = 3) -> Dict[str, Any]:
	"""Programmatic tool function: run a query against the local corpus.

	Returns a dict with keys: 'query', 'results' (list of {path, snippet, score}),
	and 'answer' (composed string).
	"""
	print(f"   [BEGIN Tool Action] Executing RAG search: {query} [END Tool Action]")
	corpus = load_corpus()
	snippets = retrieve(corpus, query, top=top)
	answer = answer_from_snippets(snippets, query)

	results = []
	for p, snip, score in snippets:
		results.append({"path": str(p), "snippet": snip, "score": score})

	return {"query": query, "results": results, "answer": answer}
