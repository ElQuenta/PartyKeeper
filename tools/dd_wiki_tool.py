from __future__ import annotations
import requests
import urllib.parse
import re
from html import unescape
from typing import Dict
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://darkestdungeon.wiki.gg"


def _fetch_url(path: str, params: Dict | None = None, timeout: int = 10):
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": "PartyKeeperBot/1.0 (+https://example.local)"}
    resp = session.get(url, timeout=timeout, headers=headers)
    resp.raise_for_status()
    return resp.text, resp.url


def extract_main_content(html_text: str, max_chars: int = 20000) -> str:
    soup = BeautifulSoup(html_text, "lxml") if html_text else None
    if not soup:
        return ""

    content = soup.select_one(".mw-parser-output")
    if content is None:
        content = soup.find("main") or soup.body
        if content is None:
            return ""

    for tag in content.find_all(["script", "style", "noscript", "table", "aside", "nav"]):
        tag.decompose()

    text = content.get_text(separator="\n\n", strip=True)
    text = unescape(text)
    text = re.sub(r"\r?\n\s*\n", "\n\n", text)
    text = re.sub(r"\s+", " ", text)
    return text[:max_chars].strip()


def search_page(title: str) -> Dict[str, str]:
    safe = title.replace(' ', '_')
    
    try:
        html_text, final_url = _fetch_url('/wiki/' + urllib.parse.quote(safe))
    except requests.HTTPError:
        html_text, final_url = _fetch_url('/wiki/Special:Search', {'search': title})

    text = extract_main_content(html_text)
    return {"title": title, "url": final_url, "text": text}


if __name__ == '__main__':
    res = search_page('Crate')
    print('URL:', res['url'])
    print('\n--- excerpt (first 2000 chars) ---\n')
    print(res['text'][:2000])
