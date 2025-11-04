from pathlib import Path
from typing import Dict, List


class Corpus:

    def __init__(self, docs: Dict[Path, str]):
        self.docs = docs

    def items(self):
        return list(self.docs.items())

    def documents(self, data_root: Path):
        """Return a list of tuples (path, text, metadata)

        Metadata includes:
        - title: filename without extension
        - category: first-level folder under the data root (if any)
        - relative_path: path relative to the data root
        """
        docs = []
        for p, text in self.items():
            try:
                rel = p.relative_to(data_root)
            except Exception:
                rel = p
            parts = rel.parts
            category = parts[0] if len(parts) > 1 else ""
            meta = {"title": p.stem, "category": category, "relative_path": str(rel)}
            docs.append((p, text, meta))
        return docs


def load_corpus(root: Path = None) -> Corpus:

    if root is None:
        root = Path(__file__).resolve().parents[2]

    data_dir = root / "wiki_menu_data"
    docs = {}
    if not data_dir.exists():
        return Corpus(docs)

    for p in data_dir.rglob("*.txt"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            # fallback to default encoding
            text = p.read_text(errors="ignore")
        docs[p] = text

    return Corpus(docs)


def load_corpus_documents(root: Path = None):
    """Helper that returns a list of (path, text, metadata) for each file.

    This is useful when you want per-document metadata (category/title) for
    building a vector index or richer RAG pipelines. The original
    `load_corpus` and `Corpus.items()` behavior is preserved for backward
    compatibility.
    """
    if root is None:
        root = Path(__file__).resolve().parents[2]

    data_dir = root / "wiki_menu_data"
    corpus = load_corpus(root)
    return corpus.documents(data_dir)
