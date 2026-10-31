import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "rag-hf-index")

settings = Settings()

if not settings.PINECONE_API_KEY:
    raise ValueError("Falta PINECONE_API_KEY en las variables de entorno (.env)")