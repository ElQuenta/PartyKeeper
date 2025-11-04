from pathlib import Path
import argparse
from .file_loader import load_corpus, load_corpus_documents
from .retriever import retrieve
from .qa_tool import answer_from_snippets
from typing import Dict, Any


def rag_tool(query: str, top: int = 3) -> Dict[str, Any]:
	print(f"   [BEGIN Tool Action] Executing RAG search: {query} [END Tool Action]")
	# load documents with metadata so we can enrich results
	docs_with_meta = load_corpus_documents()
	# build a lookup map by resolved path string
	meta_by_path = {str(p.resolve()): meta for p, _, meta in docs_with_meta}

	corpus = load_corpus()
	snippets = retrieve(corpus, query, top=top)
	answer = answer_from_snippets(snippets, query)

	results = []
	for p, snip, score in snippets:
		meta = meta_by_path.get(str(p.resolve()), {})
		results.append({"path": str(p), "snippet": snip, "score": score, "meta": meta})

	return {"query": query, "results": results, "answer": answer}
