from pathlib import Path
from typing import Dict, List


class Corpus:
    """Simple container for loaded documents.

    Attributes:
        docs: mapping path -> content (str)
    """

    def __init__(self, docs: Dict[Path, str]):
        self.docs = docs

    def items(self):
        return list(self.docs.items())


def load_corpus(root: Path = None) -> Corpus:
    """Load text files from the repository `wiki_menu_data` folder.

    Heuristics:
    - If root is None, we derive the project root from this file and
      look for `wiki_menu_data/` at the project root.
    - We load all .txt files recursively and store path->content.

    Returns a Corpus object.
    """

    if root is None:
        # package is at tools/rag; go up two levels to project root
        root = Path(__file__).resolve().parents[2]

    data_dir = root / "wiki_menu_data"
    docs = {}
    if not data_dir.exists():
        # return empty corpus but don't raise — caller can handle
        return Corpus(docs)

    for p in data_dir.rglob("*.txt"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            # fallback to default encoding
            text = p.read_text(errors="ignore")
        docs[p] = text

    return Corpus(docs)
