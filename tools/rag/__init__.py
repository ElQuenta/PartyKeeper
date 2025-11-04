"""Tools package for simple local RAG (retrieval-augmented generation).

This package contains small utilities to load local knowledge files
from `wiki_menu_data/`, retrieve relevant snippets for a query, and
compose a short answer.

These are intentionally lightweight and dependency-free so they work
inside the classroom/project environment without external APIs.
"""

from .file_loader import load_corpus, Corpus
from .retriever import retrieve
from .qa_tool import answer_from_snippets

__all__ = ["load_corpus", "Corpus", "retrieve", "answer_from_snippets"]
