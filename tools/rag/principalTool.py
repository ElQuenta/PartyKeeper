from pathlib import Path
import argparse
from .file_loader import load_corpus
from .retriever import retrieve
from .qa_tool import answer_from_snippets
from typing import Dict, Any


def rag_tool(query: str, top: int = 3) -> Dict[str, Any]:
	print(f"   [BEGIN Tool Action] Executing RAG search: {query} [END Tool Action]")
	corpus = load_corpus()
	snippets = retrieve(corpus, query, top=top)
	answer = answer_from_snippets(snippets, query)

	results = []
	for p, snip, score in snippets:
		results.append({"path": str(p), "snippet": snip, "score": score})

	return {"query": query, "results": results, "answer": answer}
