"""Agente analista."""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from agents.state import AgentState
from app.llm import get_llm

import logging
logger = logging.getLogger(__name__)


def analyst_agent(state: AgentState) -> dict:
    query = state.get("user_query", "")
    research = state.get("research_data", "")
    rag = state.get("rag_context", "")
    logger.info("[ANALYST] Generando análisis...")

    llm = get_llm(temperature=0.2)
    prompt = f"""Eres un analista senior. Genera un análisis claro y accionable basado en la información disponible.

Consulta del usuario: {query}

Contexto RAG:
{rag[:1500] if rag else "No disponible"}

Datos de investigación:
{research[:1500] if research else "No disponible"}

Análisis final:"""

    response = llm.invoke([
        SystemMessage(content="Eres un analista experto. Produce conclusiones claras y bien fundamentadas."),
        HumanMessage(content=prompt),
    ])

    content = response.content if isinstance(response.content, str) else str(response.content)

    return {
        "messages": [AIMessage(content="[ANALYST] Análisis generado.")],
        "analysis_result": content,
        "contributions": state.get("contributions", []) + ["analyst"],
    }
