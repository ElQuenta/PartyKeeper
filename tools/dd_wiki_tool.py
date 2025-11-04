from __future__ import annotations
import requests
import urllib.parse
import re
from html import unescape
from typing import Dict
import os
import time
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://darkestdungeon.wiki.gg"
OUTPUT_DIR = "wiki_menu_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": "PartyKeeperBot/1.0 (+https://example.local)"})
    return session

session = get_session()

def fetch_page(title: str) -> Dict[str, str]:
    safe_title = urllib.parse.quote(title.replace(" ", "_"))
    url = f"{BASE}/wiki/{safe_title}"
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        return {"title": title, "url": resp.url, "html": resp.text}
    except requests.HTTPError as e:
        print(f"Error HTTP {e.response.status_code} en '{title}': {url}")
        return {"title": title, "url": url, "html": ""}
    except Exception as e:
        print(f"Error descargando '{title}': {e}")
        return {"title": title, "url": url, "html": ""}

def clean_text(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
def extract_tables(soup: BeautifulSoup) -> str:
    tables_text = []
    wikitable = soup.find_all("table", class_="wikitable")
    
    for idx, table in enumerate(wikitable):
        header_text = " ".join([th.get_text() for th in table.find_all("th")])
        if not any(kw in header_text for kw in ["Curio", "Trinket", "Item", "Chance", "Cleansing", "Effect"]):
            continue

        tables_text.append(f"\n=== TABLA {idx+1} ===\n")
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            if not cols:
                continue
            row_text = " | ".join(clean_text(col.get_text()) for col in cols)

            icons = []
            for img in row.find_all("img"):
                alt = img.get("alt", "")
                title = img.get("title", "")
                icon = alt.strip() or title.strip()
                if icon and icon not in ["", "Icon"]:
                    icons.append(icon)
            if icons:
                row_text = f"[Íconos: {', '.join(icons)}] " + row_text

            tables_text.append(row_text)
        tables_text.append("")

    return "\n".join(tables_text) if tables_text else ""

def extract_content_with_tables(html: str, page_title: str) -> str:
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")
    content = soup.select_one(".mw-parser-output")
    if not content:
        return ""

    table_text = extract_tables(soup)

    for table in content.find_all("table", class_="wikitable"):
        table.decompose()

    for tag in content.find_all(["script", "style", "noscript", "nav", "aside", "sup", "table"]):
        tag.decompose()

    text = content.get_text(separator="\n\n", strip=True)
    text = clean_text(text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    final = []
    if text:
        final.append(text)
    if table_text:
        final.append(table_text)
    return "\n\n".join(final)

def save_to_txt(game: str, section: str, data: Dict):
    safe_section = re.sub(r'[^\w\- ]', '', section).strip().replace(" ", "_")
    game_dir = os.path.join(OUTPUT_DIR, game.replace(" ", "_"))
    os.makedirs(game_dir, exist_ok=True)
    filepath = os.path.join(game_dir, f"{safe_section}.txt")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Título: {data['title']}\n")
        f.write(f"URL: {data['url']}\n")
        f.write(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("=" * 80 + "\n\n")
        f.write(data['text'])

    print(f"Guardado: {filepath}")

MENU_SECTIONS = {
    "Darkest Dungeon": [
        "Heroes",
        "Enemies",
        "Locations",
        "Curios",
        "Trinkets",
        "Quirks",
        "The Ancestor",
        "Patch notes"  
    ],
    "Darkest Dungeon II": [
        "Heroes",
        "Enemies",
        "Locations",
        "Items",
        "Quirks",
        "The Academic",
        "Patch notes (Darkest Dungeon II)"  
    ]
}

def main():
    print("Iniciando extracción mejorada (tablas + patch notes corregidos)...\n")
    for game, sections in MENU_SECTIONS.items():
        print(f"\n=== {game} ===")
        for section in sections:
            print(f"  {section}...", end=" ")
            data = fetch_page(section)
            if data["html"]:
                data["text"] = extract_content_with_tables(data["html"], section)
                save_to_txt(game, section, data)
            else:
                print("Falló")
            time.sleep(1.5)  
    print(f"\n¡Listo! Archivos en: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()