#RestoGuide AI- RAG based

A local-first RAG assistant for a fictional Continental + Italian bistro, The Oak & Thyme Bistro.

## Features
- FastAPI backend and responsive web interface
- PDF, DOCX, TXT and Markdown ingestion
- Sentence Transformers embeddings and FAISS semantic retrieval
- LangGraph conditional workflow: internal retrieval → evidence threshold → optional DuckDuckGo fallback
- SQLite question history and source citations
- Sample recipes, kitchen SOPs, policies and reference guides
- Pytest starter tests

## Important limitations
This portfolio prototype uses synthetic restaurant documents. It does not use a generative LLM: answers quote/extract retrieved passages, so no API key is needed. Web results are labelled external and are not approved restaurant procedures. Do not use this prototype for food-safety decisions without qualified review and approved procedures. The first launch downloads the embedding model; internet is required for that initial download and for DuckDuckGo fallback.

## Windows / PowerShell
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000. The first start builds the index and downloads the embedding model.

## Tests
```powershell
pytest -q
```

## Project structure
- `app/main.py`: FastAPI routes
- `app/rag/engine.py`: embeddings, FAISS retrieval and LangGraph workflow
- `app/services/documents.py`: file extraction and chunking
- `app/services/database.py`: SQLite history
- `app/templates`, `app/static`: UI
- `data/knowledge_base`: fictional internal documents
- `tests`: starter tests

Upload documents through the Documents page. Supported formats: PDF, DOCX, TXT and Markdown. Upload only documents you have permission to use.

Performance claims should only be made after creating a labelled benchmark and measuring retrieval quality, citation accuracy, abstention accuracy and latency.
## Query Routing

RestoGuide AI first searches the internal restaurant documents.

If sufficiently relevant internal evidence is not found, the system can use external web search as a fallback. External results are clearly labelled as unapproved web information and do not override internal restaurant procedures.
