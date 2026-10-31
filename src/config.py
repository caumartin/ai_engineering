import os
import unicodedata
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

def clean_spanish_text(text: str) -> str:
    """
    Normaliza el texto eliminando tildes, diacríticos y convirtiendo caracteres
    especiales del español (como la ñ) a su equivalente base (n).
    """
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

class Settings(BaseModel):
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "rag-hf-index")

settings = Settings()

if not settings.PINECONE_API_KEY:
    raise ValueError("Falta PINECONE_API_KEY en las variables de entorno (.env)")