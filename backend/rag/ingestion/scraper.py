import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import random

from rag.config import ARTICLE_DIR


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing short/noisy lines
    """
    lines = text.split("\n")
    cleaned = [line.strip() for line in lines if len(line.strip()) > 40]
    return "\n".join(cleaned)


def extract_text_from_wikipedia(soup: BeautifulSoup) -> str:
    """
    Extract main content from Wikipedia pages
    """
    content = soup.find("div", {"id": "mw-content-text"})
    if content:
        paragraphs = content.find_all("p")
    else:
        paragraphs = soup.find_all("p")

    text = "\n".join(p.get_text() for p in paragraphs)
    return text


def scrape_article(url: str, filename: str):
    """
    Scrape a single article and save as text file
    """
    try:
        print(f"[SCRAPING] {url}")

        response = requests.get(url, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            print(f"[SKIPPED] {url} → Status: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Wikipedia-specific extraction
        text = extract_text_from_wikipedia(soup)

        cleaned = clean_text(text)

        if not cleaned:
            print(f"[EMPTY] {url}")
            return

        ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
        file_path = ARTICLE_DIR / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"[SAVED] {file_path}")

        # Avoid rate limiting
        time.sleep(random.uniform(1, 2))

    except Exception as e:
        print(f"[ERROR] {url} → {e}")


def run():
    """
    List of scrapeable, stable sources (Wikipedia)
    """
    urls = {
        "rsi.txt": "https://en.wikipedia.org/wiki/Relative_strength_index",
        "macd.txt": "https://en.wikipedia.org/wiki/MACD",
        "pe_ratio.txt": "https://en.wikipedia.org/wiki/Price%E2%80%93earnings_ratio",
        "fundamental.txt": "https://en.wikipedia.org/wiki/Fundamental_analysis",
    }

    for filename, url in urls.items():
        scrape_article(url, filename)


if __name__ == "__main__":
    run()