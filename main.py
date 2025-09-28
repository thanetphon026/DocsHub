from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
DATA_DIR = BASE_DIR / "data"

for p in (STATIC_DIR, TEMPLATES_DIR, DATA_DIR / "docs", DATA_DIR / "index"):
    p.mkdir(parents=True, exist_ok=True)

from app.routes import router as app_router

app = FastAPI(title="Docs Hub", version="1.3.1")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(app_router)
