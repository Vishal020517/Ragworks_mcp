from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

PDF_DIR = RAW_DATA_DIR / "pdfs"
ARTICLE_DIR = RAW_DATA_DIR / "articles"

INDEX_DIR = BASE_DIR / "index"

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

TOP_K = 3