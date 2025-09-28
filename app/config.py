import os, json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
INDEX_DIR = DATA_DIR / "index"
TAGS_REG_PATH = DATA_DIR / "tags.json"
for p in (DATA_DIR, DOCS_DIR, INDEX_DIR):
    p.mkdir(parents=True, exist_ok=True)
if not TAGS_REG_PATH.exists():
    TAGS_REG_PATH.write_text("[]", encoding="utf-8")

LAN_ONLY = os.getenv("LAN_ONLY","1") == "1"
TRUST_PROXY = os.getenv("TRUST_PROXY","0") == "1"
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB","100"))
ALLOWED_EXT = {".pdf",".md",".txt"}
