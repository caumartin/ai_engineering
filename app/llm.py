"""Utilidades compartidas para LLMs."""
import os
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(model_name: str = None, temperature: float = 0.2):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Falta GOOGLE_API_KEY en variables de entorno")
    model = model_name or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=api_key,
    )
