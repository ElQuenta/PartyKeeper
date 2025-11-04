from typing import List, Tuple
from pathlib import Path
import re


def _tokenize(s: str) -> List[str]:
    return re.findall(r"\w+", s.lower())


def score_text(query_tokens, text: str) -> int:
    t = _tokenize(text)
    s = 0
    for q in query_tokens:
        s += t.count(q)
    return s


def retrieve(corpus, query: str, top: int = 3) -> List[Tuple[Path, str, int]]:

    tokens = _tokenize(query)
    results = []
    for path, content in corpus.items():
        best_score = 0
        best_snip = ""
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [l.strip() for l in content.splitlines() if l.strip()]

        for p in paragraphs:
            sc = score_text(tokens, p)
            if sc > best_score:
                best_score = sc
                best_snip = p[:2000]

        if best_score > 0:
            results.append((path, best_snip, best_score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top]
