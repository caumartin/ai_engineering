"""Agente de recuperación RAG."""
import os
from langchain_core.messages import AIMessage
from agents.state import AgentState
from rag.retriever import get_retriever

import logging
logger = logging.getLogger(__name__)


def rag_agent(state: AgentState) -> dict:
    query = state.get("user_query", "")
    logger.info(f"[RAG] Buscando contexto para: {query[:80]}...")

    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)
        context = "\n\n".join([d.page_content for d in docs]) if docs else "No se encontró contexto relevante."
    except Exception as e:
        logger.exception(f"[RAG] Error en recuperación: {e}")
        context = "Error al recuperar contexto. Continuando sin RAG."

    return {
        "messages": [AIMessage(content=f"[RAG] Contexto recuperado ({len(context)} caracteres).")],
        "rag_context": context,
        "contributions": state.get("contributions", []) + ["rag"],
    }
