import sqlite3, time
from typing import List, Dict, Any, Optional
from .config import DATA_DIR

DB_PATH = DATA_DIR / "docs.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS docs(
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        title TEXT NOT NULL,
        ext TEXT NOT NULL,
        size INTEGER NOT NULL,
        tags TEXT NOT NULL DEFAULT '',
        sha256 TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL
    )""")
    conn.commit(); conn.close()

def add_doc(rec: Dict[str,Any]):
    conn = connect(); cur = conn.cursor()
    cur.execute("""INSERT INTO docs(id,filename,title,ext,size,tags,sha256,created_at,updated_at)
                  VALUES(?,?,?,?,?,?,?,?,?)""",(
        rec['id'], rec['filename'], rec['title'], rec['ext'], rec['size'],
        rec.get('tags',''), rec['sha256'], rec['created_at'], rec['updated_at']
    ))
    conn.commit(); conn.close()

def set_single_tag(doc_id: str, tag: str):
    conn = connect(); cur = conn.cursor()
    cur.execute("UPDATE docs SET tags=?, updated_at=? WHERE id=?",
                (tag.strip(), int(time.time()), doc_id))
    conn.commit(); conn.close()

def delete_doc(doc_id: str):
    conn = connect(); cur = conn.cursor()
    cur.execute("DELETE FROM docs WHERE id=?", (doc_id,))
    conn.commit(); conn.close()

def get_doc(doc_id: str) -> Optional[Dict[str,Any]]:
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM docs WHERE id=?", (doc_id,))
    row = cur.fetchone(); conn.close()
    return dict(row) if row else None

def list_docs() -> List[Dict[str,Any]]:
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM docs ORDER BY updated_at DESC")
    rows = [dict(r) for r in cur.fetchall()]; conn.close(); return rows
