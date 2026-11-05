from pathlib import Path
import shutil
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.rag.engine import Engine
from app.services.database import init_db, save, history
from app.services.documents import SUPPORTED

class Config(BaseSettings):
    restaurant_name:str="The Oak & Thyme Bistro"
    embedding_model:str="sentence-transformers/all-MiniLM-L6-v2"
    top_k:int=5
    evidence_threshold:float=.70
    enable_web_fallback:bool=True
    database_path:str="data/restaurantops.db"
    index_dir:str="data/index"
    upload_dir:str="data/uploads"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
cfg=Config()
app=FastAPI(title="RestaurantOps AI")
app.mount("/static",StaticFiles(directory="app/static"),name="static")
templates=Jinja2Templates(directory="app/templates")
Path(cfg.upload_dir).mkdir(parents=True,exist_ok=True)
init_db(cfg.database_path)
engine=Engine(cfg.embedding_model,cfg.index_dir,cfg.top_k,cfg.evidence_threshold,cfg.enable_web_fallback)
if engine.index is None: engine.rebuild("data/knowledge_base")
class Question(BaseModel): question:str
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request, "restaurant": cfg.restaurant_name}
    )

@app.get("/api/health")
def health(): return {"status":"ok","indexed_chunks":len(engine.docs)}
@app.post("/api/ask")
def ask(payload: Question):
    q = payload.question.strip()

    if not q:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = engine.ask(q)
    save(cfg.database_path, q, result["answer"])
    return result

@app.get("/api/history")
def get_history(): return {"items":history(cfg.database_path)}
@app.get("/api/documents")
def docs():
    unique={d["source"]:{"filename":d["source"],"category":d["category"]} for d in engine.docs}
    return {"items":list(unique.values())}
@app.post("/api/documents")
async def upload(file:UploadFile=File(...)):
    ext=Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED: raise HTTPException(400,"Supported: PDF, DOCX, TXT, MD")
    name=Path(file.filename).name; dest=Path(cfg.upload_dir)/name
    if dest.exists(): raise HTTPException(409,"A file with this name already exists.")
    with dest.open("wb") as f: shutil.copyfileobj(file.file,f)
    try:
        engine.rebuild("data/knowledge_base")
        engine.rebuild(cfg.upload_dir)
        # Re-index both internal sample documents and uploaded documents together.
        docs=[]
        from app.services.documents import load_file
        for folder in ["data/knowledge_base",cfg.upload_dir]:
            for p in Path(folder).rglob("*"):
                if p.is_file() and p.suffix.lower() in SUPPORTED: docs+=load_file(p)
        engine.docs=[]
        engine.rebuild_from_documents(docs)
    except Exception as e:
        dest.unlink(missing_ok=True);raise HTTPException(500,f"Indexing failed: {e}")
    return {"filename":name,"message":"Uploaded and indexed."}
