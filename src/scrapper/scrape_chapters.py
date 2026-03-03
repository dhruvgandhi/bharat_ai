import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BASE_URL = "https://www.carakasamhitaonline.com/"
INDEX_URL = BASE_URL + "index.php?title=Adhyaya(chapters)"

def scrape_chapters():
    response = requests.get(INDEX_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    current_sthana = None

    # Iterate through page elements in order
    for tag in soup.find_all(["h2", "ol"]):

        # Capture Sthana from headings
        if tag.name == "h2":
            current_sthana = tag.get_text(strip=True)

        # If ordered list, extract chapters
        elif tag.name == "ol" and current_sthana:
            for index, li in enumerate(tag.find_all("li", recursive=False), start=1):

                link = li.find("a")
                if not link:
                    continue

                chapter_name = link.get_text(strip=True)
                chapter_url = urljoin(BASE_URL, link["href"])

                results.append({
                    "sthāna": current_sthana,
                    "chapter_number": index,  # Generated manually
                    "chapter_name": chapter_name,
                    "chapter_link": chapter_url
                })

    return results



BASE_URL = "https://www.carakasamhitaonline.com/"

import requests
from bs4 import BeautifulSoup
import re

DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')
VERSE_PATTERN = re.compile(r'\[.*?\]')

import requests
from bs4 import BeautifulSoup
import re

DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')
TRANSLIT_PATTERN = re.compile(r'[āīūṛṅñṭḍṇśṣ]')
VERSE_PATTERN = re.compile(r'\[(\d+(?:-\d+)?)\]')

def scrape_chapter(chapter_url):
    response = requests.get(chapter_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Chapter Title
    chapter_title = soup.find("h1", {"id": "firstHeading"}).get_text(strip=True)

    content_div = soup.find("div", {"id": "mw-content-text"})
    parser_output = content_div.find("div", {"class": "mw-parser-output"})

    # Remove TOC
    toc = parser_output.find("div", {"id": "toc"})
    if toc:
        toc.decompose()

    results = []

    # Hierarchy counters for numbering
    counters = {2: 0, 3: 0, 4: 0}

    current_section = None
    current_level = None
    sanskrit_lines = []
    translit_lines = []
    english_lines = []
    verse_refs = []

    def save_section():
        if current_section:
            results.append({
                "chapter_title": chapter_title,
                "section_number": current_section["number"],
                "section_title": current_section["title"],
                "level": current_level,
                "sanskrit_text": "\n".join(sanskrit_lines).strip(),
                #"transliteration": "\n".join(translit_lines).strip(),
                "english_translation": " ".join(english_lines).strip(),
                #"verse_reference": verse_refs if verse_refs else None
            })

    for element in parser_output.children:

        if not hasattr(element, "name"):
            continue

        # ---------------- HEADINGS ----------------
        if element.name in ["h2", "h3", "h4"]:

            # Save previous section
            save_section()

            level = int(element.name[1])
            counters[level] += 1

            # Reset lower levels
            for l in range(level + 1, 5):
                counters[l] = 0

            section_number = ".".join(
                str(counters[l]) for l in range(2, level + 1) if counters[l] > 0
            )

            current_section = {
                "number": section_number,
                "title": element.get_text(strip=True)
            }

            current_level = level
            sanskrit_lines = []
            translit_lines = []
            english_lines = []
            verse_refs = []

        # ---------------- CONTENT ----------------
        elif element.name in ["p", "div", "dl", "dd"] and current_section:

            # Handle poem blocks properly
            if element.name == "div" and "poem" in element.get("class", []):
                text = element.get_text("\n", strip=True)
            else:
                text = element.get_text(strip=True)

            if not text:
                continue

            # Capture verse references like [3], [4-5]
            # found_refs = VERSE_PATTERN.findall(text)
            # if found_refs:
            #     verse_refs.extend(found_refs)

            # Sanskrit detection
            if DEVANAGARI_PATTERN.search(text):
                sanskrit_lines.append(text)

            # Transliteration detection
            # elif TRANSLIT_PATTERN.search(text):
            #     translit_lines.append(text)

            else:
                english_lines.append(text)

    # Save last section
    save_section()

    return results
if __name__ == "__main__":
    chapters = scrape_chapters()

    for chap in chapters:  # show first 10
        print(f"Scraping {chap['chapter_name']}...  {chap['chapter_link']}")
        shlokas = scrape_chapter(chap['chapter_link'])
        if shlokas:
            with open(f"data/cleaned_text/{chap['chapter_name'].replace(' ', '_')}.json", "w", encoding="utf-8") as f:
                import json
                json.dump(shlokas, f, ensure_ascii=False, indent=2)
            print(f"  First section: {shlokas[0]['section_number']} - {shlokas[0]['section_title'][:30]}...")
            chap['shlokas'] = shlokas