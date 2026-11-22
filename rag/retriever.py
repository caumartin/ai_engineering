"""Retriever RAG simple con Chroma en memoria."""
import os
import logging
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)
_retriever = None


def _get_embeddings():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY no configurada")
    # Modelos de embedding válidos de Google
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key,
    )


def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    docs = [
        Document(page_content="La inteligencia artificial generativa ha revolucionado la creación de contenido en 2025-2026.", metadata={"source": "internal"}),
        Document(page_content="Los agentes multi-agente con supervisores permiten orquestar tareas complejas de forma autónoma.", metadata={"source": "internal"}),
        Document(page_content="RAG (Retrieval-Augmented Generation) reduce alucinaciones al anclar las respuestas en documentos reales.", metadata={"source": "internal"}),
        Document(page_content="Arize Phoenix es una plataforma de observabilidad open-source para sistemas LLM.", metadata={"source": "internal"}),
        Document(page_content="Redis se usa como checkpointer persistente en LangGraph para mantener estado entre reinicios.", metadata={"source": "internal"}),
        Document(page_content="FastAPI permite construir APIs asíncronas de alto rendimiento con validación Pydantic.", metadata={"source": "internal"}),
    ]

    try:
        embeddings = _get_embeddings()
        vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
        _retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        logger.info("RAG retriever inicializado correctamente")
        return _retriever
    except Exception as e:
        logger.error(f"Error inicializando RAG: {e}")
        raise