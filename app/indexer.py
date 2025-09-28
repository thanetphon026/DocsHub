from whoosh import index
from whoosh.fields import Schema, ID, TEXT, KEYWORD
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.analysis import StemmingAnalyzer
from whoosh.highlight import UppercaseFormatter
from pathlib import Path
import shutil

schema = Schema(
    id=ID(stored=True, unique=True),
    title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    filename=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    tags=KEYWORD(stored=True, commas=True, scorable=True, lowercase=True),
    content=TEXT(stored=False, analyzer=StemmingAnalyzer()),
)

def ensure_index(idx_dir: Path):
    idx_dir.mkdir(parents=True, exist_ok=True)
    if not index.exists_in(idx_dir):
        index.create_in(idx_dir, schema)
    return index.open_dir(idx_dir)

def add_or_update(idx_dir: Path, doc):
    ix = ensure_index(idx_dir)
    writer = ix.writer(limitmb=64, procs=1, multisegment=True)
    writer.update_document(
        id=doc['id'],
        title=doc.get('title',''),
        filename=doc.get('filename',''),
        tags=doc.get('tags',''),
        content=doc.get('content',''),
    )
    writer.commit()

def remove(idx_dir: Path, doc_id: str):
    ix = ensure_index(idx_dir)
    writer = ix.writer(); writer.delete_by_term('id', doc_id); writer.commit()

def clear(idx_dir: Path):
    if idx_dir.exists():
        for f in idx_dir.iterdir():
            if f.is_file(): f.unlink()
            elif f.is_dir(): shutil.rmtree(f)
    index.create_in(idx_dir, schema)
