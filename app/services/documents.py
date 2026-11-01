from pathlib import Path
from pypdf import PdfReader
from docx import Document

SUPPORTED = {".pdf", ".docx", ".txt", ".md"}

def extract(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    if ext == ".docx":
        return "\n".join(p.text for p in Document(str(path)).paragraphs)
    if ext in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"Unsupported format: {ext}")

def chunks(text: str, size: int = 180, overlap: int = 30) -> list[str]:
    words = " ".join(text.split()).split()
    out, start = [], 0
    while start < len(words):
        end = min(start + size, len(words))
        out.append(" ".join(words[start:end]))
        if end == len(words): break
        start = end - overlap
    return out

def load_file(path: Path) -> list[dict]:
    return [{"text": c, "source": path.name, "category": path.parent.name,
             "source_type": "internal"} for c in chunks(extract(path))]
