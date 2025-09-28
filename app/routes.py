from __future__ import annotations
import os, time, tarfile, mimetypes
from typing import List
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .config import DATA_DIR, DOCS_DIR, INDEX_DIR, LAN_ONLY, TRUST_PROXY, MAX_UPLOAD_MB, ALLOWED_EXT
from .utils import safe_filename, sha256_file, is_private_ip, registry_list, registry_add, registry_del
from . import db
from .indexer import add_or_update, remove, clear as idx_clear
from pdfminer.high_level import extract_text as pdf_text
import markdown

router = APIRouter()
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
db.init_db()

def client_ip(request: Request) -> str:
    if TRUST_PROXY:
        xf = request.headers.get("x-forwarded-for", "")
        if xf: return xf.split(",")[0].strip()
    return request.client.host if request.client else "0.0.0.0"

def require_lan(request: Request):
    if LAN_ONLY and not is_private_ip(client_ip(request)):
        raise HTTPException(403, "LAN only")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    require_lan(request)
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/view/{doc_id}", response_class=HTMLResponse)
def view_doc(request: Request, doc_id: str):
    require_lan(request)
    rec = db.get_doc(doc_id)
    if not rec: raise HTTPException(404, "Not found")
    ext = rec["ext"].lower()
    if ext in (".md", ".txt"):
        p = DOCS_DIR / f"{doc_id}{rec['ext']}"
        text = p.read_text("utf-8", errors="ignore")
        body = (markdown.markdown(text, extensions=["extra","tables","fenced_code"])
                if ext == ".md" else
                "<pre>"+text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")+"</pre>")
        return templates.TemplateResponse("viewer_md.html",
                {"request": request, "title": rec["title"], "body": body, "doc": rec})
    return templates.TemplateResponse("viewer_pdf.html", {"request": request, "doc": rec})

@router.get("/raw/{doc_id}")
def file_inline(doc_id: str):
    rec = db.get_doc(doc_id)
    if not rec: raise HTTPException(404, "Not found")
    path = DOCS_DIR / f"{doc_id}{rec['ext']}"
    if not path.exists(): raise HTTPException(404, "File missing")
    media_type = mimetypes.guess_type(rec["filename"])[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type)

@router.get("/download/{doc_id}")
def file_download(doc_id: str):
    rec = db.get_doc(doc_id)
    if not rec: raise HTTPException(404, "Not found")
    path = DOCS_DIR / f"{doc_id}{rec['ext']}"
    if not path.exists(): raise HTTPException(404, "File missing")
    return FileResponse(path, filename=rec["filename"])

# Registry APIs
@router.get("/api/registry")
def api_registry_list(request: Request):
    require_lan(request)
    return {"tags": registry_list()}

@router.post("/api/registry/add")
def api_registry_add(request: Request, name: str = Form(...)):
    require_lan(request)
    if not name.strip():
        raise HTTPException(400, "Tag name required")
    registry_add(name.strip())
    return {"ok": True, "tags": registry_list()}

@router.post("/api/registry/delete")
def api_registry_delete(request: Request, name: str = Form(...)):
    require_lan(request)
    registry_del(name.strip())
    return {"ok": True, "tags": registry_list()}

# Docs APIs
@router.get("/api/docs")
def api_docs(request: Request, tag: str = ""):
    require_lan(request)
    rows = db.list_docs()
    if tag and tag.lower() != "all":
        rows = [r for r in rows if r["tags"].strip().lower() == tag.strip().lower()]
    return rows

@router.post("/api/doc/{doc_id}/tag")
def api_set_doc_tag(request: Request, doc_id: str, tag: str = Form("all")):
    require_lan(request)
    rec = db.get_doc(doc_id)
    if not rec: raise HTTPException(404, "Not found")
    value = "" if tag.lower()=="all" else tag.strip()
    db.set_single_tag(doc_id, value)
    try:
        add_or_update(INDEX_DIR, {"id": rec["id"], "title": rec["title"], "filename": rec["filename"],
                                  "tags": value, "content": ""})
    except Exception:
        pass
    return {"ok": True, "doc": db.get_doc(doc_id)}

@router.post("/api/upload")
async def api_upload(request: Request, files: List[UploadFile] = File(...)):
    require_lan(request)
    out = []
    for f in files:
        name = safe_filename(f.filename or "file")
        ext = os.path.splitext(name)[1].lower()
        if ext not in ALLOWED_EXT:
            raise HTTPException(400, f"Unsupported file type: {ext}")
        data = await f.read()
        if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
            raise HTTPException(400, "File too large")

        doc_id = os.urandom(9).hex()
        path = DOCS_DIR / f"{doc_id}{ext}"
        with open(path, "wb") as w: w.write(data)

        size = path.stat().st_size
        sha = sha256_file(path)
        title = os.path.splitext(name)[0]
        now = int(time.time())
        rec = {"id": doc_id, "filename": name, "title": title, "ext": ext,
               "size": size, "tags": "", "sha256": sha,
               "created_at": now, "updated_at": now}
        db.add_doc(rec)

        # minimal index
        try:
            add_or_update(INDEX_DIR, {"id": doc_id, "title": title, "filename": name,
                                      "tags": "", "content": ""})
        except Exception: pass

        out.append(rec)
    return {"ok": True, "items": out}

@router.post("/api/reindex")
def api_reindex(request: Request):
    require_lan(request)
    idx_clear(INDEX_DIR)
    rows = db.list_docs()
    for r in rows:
        add_or_update(INDEX_DIR, {"id": r["id"], "title": r["title"], "filename": r["filename"],
                                  "tags": r["tags"], "content": ""})
    return {"ok": True, "count": len(rows)}

@router.post("/api/delete/{doc_id}")
def api_delete(request: Request, doc_id: str):
    require_lan(request)
    rec = db.get_doc(doc_id)
    if not rec: raise HTTPException(404, "Not found")
    p = DOCS_DIR / f"{doc_id}{rec['ext']}"
    try:
        if p.exists(): p.unlink()
    except Exception: pass
    db.delete_doc(doc_id)
    try: remove(INDEX_DIR, doc_id)
    except Exception: pass
    return {"ok": True}

@router.get("/api/backup")
def api_backup(request: Request):
    require_lan(request)
    tarpath = DATA_DIR / "docs_backup.tar.gz"
    def _filter(ti):
        name = ti.name.rsplit("/",1)[-1]
        if name == "docs_backup.tar.gz":
            return None
        return ti
    with tarfile.open(tarpath, "w:gz") as tar:
        tar.add(DATA_DIR, arcname="data", filter=_filter)
    return FileResponse(tarpath, filename="docs_backup.tar.gz", media_type="application/gzip")

@router.post("/api/restore")
async def api_restore(request: Request, file: UploadFile = File(...)):
    require_lan(request)
    data = await file.read()
    tmp = DATA_DIR / "_restore.tar.gz"
    with open(tmp, "wb") as w: w.write(data)
    try:
        with tarfile.open(tmp, "r:gz") as tar:
            members = tar.getmembers()
            def _ok_name(n:str)->bool:
                return n == "data" or n == "data/" or n.startswith("data/") or n.startswith("./data")
            if any(not _ok_name(m.name) for m in members):
                raise HTTPException(400, "Invalid backup structure")
            tar.extractall(path=DATA_DIR.parent)
    finally:
        try: tmp.unlink()
        except Exception: pass
    return {"ok": True}
