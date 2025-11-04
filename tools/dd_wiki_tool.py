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
    session.headers.update({"User-Agent": "PartyKeeperBot/1.0"})
    return session

session = get_session()

def fetch_page(title: str) -> Dict:
    safe_title = urllib.parse.quote(title.replace(" ", "_"))
    url = f"{BASE}/wiki/{safe_title}"
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        return {"title": title, "url": resp.url, "html": resp.text, "success": True}
    except:
        return {"title": title, "url": url, "html": "", "success": False}

def extract_text(html: str) -> str:
    if not html:
        return "No se pudo cargar."
    
    soup = BeautifulSoup(html, "lxml")
    content = soup.select_one(".mw-parser-output")
    if not content:
        return "Contenido no encontrado."
    
    tables_text = []
    for table in content.find_all("table", class_="wikitable"):
        header = " ".join([th.get_text(strip=True) for th in table.find_all("th")])
        if any(kw in header for kw in ["Curio", "Trinket", "Quirk", "Chance", "Cleansing", "Effect"]):
            tables_text.append("\n=== TABLA DE INTERACCIONES ===\n")
            for row in table.find_all("tr"):
                cols = row.find_all(["td", "th"])
                if not cols:
                    continue
                row_parts = []
                for col in cols:
                    col_text = col.get_text(strip=True)
                    # Íconos
                    icons = [img.get("alt", "") or img.get("title", "") for img in col.find_all("img") if img.get("alt")]
                    if icons:
                        col_text = f"[Íconos: {', '.join(icons)}] {col_text}"
                    row_parts.append(col_text)
                tables_text.append(" | ".join(row_parts))
            tables_text.append("\n")
            table.decompose() 
    for tag in content.find_all(["script", "style", "nav", "aside", "sup"]):
        tag.decompose()
    
    text = content.get_text(separator="\n\n", strip=True)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+", " ", text).strip()
    
    final = [text[:40000]]  
    final.extend(tables_text)
    return "\n\n".join(final)

def save_file(category: str, title: str, text: str):
    safe_cat = re.sub(r'[^\w\-]', '_', category)
    safe_title = re.sub(r'[^\w\-]', '_', title)
    dir_path = os.path.join(OUTPUT_DIR, safe_cat)
    os.makedirs(dir_path, exist_ok=True)
    
    filename = f"{safe_title}.txt"
    filepath = os.path.join(dir_path, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"TÍTULO: {title}\n")
        f.write(f"URL: {BASE}/wiki/{urllib.parse.quote(title.replace(' ', '_'))}\n")
        f.write(f"CATEGORÍA: {category}\n")
        f.write(f"FECHA: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("=" * 80 + "\n\n")
        f.write(text)
    
    print(f"  ✅ {title} → {filepath}")
    return filepath

DD1_PAGES = {
    "general": [
        "Curios", "Trinkets", "Quirks", "The Ancestor", "Patch notes"
    ],

    "heroes": [
        "Crusader", "Highwayman", "Man-at-Arms", "Vestal", "Arbalest", "Flagellant", "Grave Robber", 
        "Hellion", "Jester", "Leper", "Occultist", "Plague Doctor", "Poet", "Bounty Hunter",
        "Duelist", "Houndmaster", "Ifrit", "Sapper"
    ],
    
    "enemies": [
        "Bone Soldier", "Bone Arbalist", "Bone Defender", "Bone Courtier", "Bone Captain", "Bone Rabble", 
        "Bone Spearman", "Bone Infantryman", "Bone Marksman", "Bone Squire", "Bone Warden", "Urchin",
        
        "Large Hyena", "Young Hyena", "Stress Hyena", "Brigand Fusebearer", "Brigand Cutthroat", 
        "Brigand Raider", "Brigand Hunter", "Brigand Matchman", "Brigand Bloodletter", "Brigand Musketeer",
        "Brigand Butcher", "Fungal Scratcher", "Fungal Grower", "Fungal Artillery", "Fungal Witch",
        "Ectoplasmic Husk", "Ectoplasmic Metal", "Ectoplasmic Flesh", "Ectoplasmic Horror",

        "Swine Wretch", "Swine Slasher", "Swine Chopper", "Swine Guard", "Swine Drummer", "Swine Alpha",
        "Swine Wailer", "Large Swine", "Madman", "Large Madman", "Vigilant Hound", "Mausoleum Cultist",
        
        "Fishman", "Thrashing Fishman", "Crab", "Crab Man", "Pelagic Grouper", "Pelagic Shaman",
        "Pelagic Siren", "Uptick Fishman", "Sea Maggot", "Adder", "Giant Adder", "Crystalline Carryall",
        
        "Cultist Acolyte", "Cultist Priestess", "Cultist Initiate", "Cultist Fanatic", "Cultist Brawler",
        
        "Shambler", "Collector", "Mammoth Censer", "Templar Impaler", "Templar Gladiator", "Templar Warlord",
        "Templar Torchbearer", "Swine Prince", "Flesh", "Visage", "Crops", "Rumour", "Summoner", "Seer",
        "Sycophant", "Courtier", "Sycophant 1", "Sycophant 2", "Thing From The Stars", "Baron",
        "Baron (Second Form)", "Shroud", "Miller", "Shroud 1", "Shroud 2", "Shroud 3", "Shroud 4",
        "Mammoth Censer Bearer", "Mammoth Censer Squire", "Mammoth Censer Templar"
    ],
    
    "locations": [
        "Ruins", "Weald", "Warrens", "Cove", "Darkest Dungeon", "Abbey"  
    ]
}

def main():
    print("🚀 EXTRAYENDO TODO DE DARKEST DUNGEON 1 (COMPLETO)\n")
    
    for category, pages in DD1_PAGES.items():
        print(f"\n📁 {category.upper()}: {len(pages)} páginas")
        
        for title in pages:
            print(f"  {title}...", end=" ")
            data = fetch_page(title)
            if data["success"]:
                text = extract_text(data["html"])
                save_file(category, title, text)
                print("✅")
            else:
                print("❌")
            time.sleep(0.8)  
    
    print(f"\n🎉 ¡TODO COMPLETADO! En: {OUTPUT_DIR}/")
    print("\n📁 Estructura final:")
    print("   general/          ← Curios.txt (con tablas), Quirks.txt, etc.")
    print("   heroes/           ← Crusader.txt (stats, skills), Highwayman.txt, ... (18)")
    print("   enemies/          ← Bone_Soldier.txt (ataques, loot), Swine_Wretch.txt, ... (~100)")
    print("   locations/        ← Ruins.txt (curios, enemigos), Weald.txt, ... (6)")

if __name__ == "__main__":
    main()