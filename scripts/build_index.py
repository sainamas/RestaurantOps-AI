from pathlib import Path
from app.rag.engine import Engine
from pydantic_settings import BaseSettings, SettingsConfigDict
class Config(BaseSettings):
    embedding_model:str="sentence-transformers/all-MiniLM-L6-v2"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
cfg=Config()
engine=Engine(cfg.embedding_model,"data/index")
print(f"Indexed {engine.rebuild('data/knowledge_base')} chunks.")
