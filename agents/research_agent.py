"""Agente de investigación (simulada / web)."""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from agents.state import AgentState
from app.llm import get_llm

import logging
logger = logging.getLogger(__name__)


def research_agent(state: AgentState) -> dict:
    query = state.get("user_query", "")
    logger.info(f"[RESEARCH] Investigando: {query[:80]}...")

    llm = get_llm(temperature=0.3)
    prompt = f"""Eres un agente de investigación. Genera un resumen informativo y actualizado sobre el siguiente tema.
Sé conciso pero completo. Incluye datos relevantes si los conoces.

Tema: {query}

Resumen de investigación:"""

    response = llm.invoke([
        SystemMessage(content="Eres un investigador experto. Responde de forma objetiva y estructurada."),
        HumanMessage(content=prompt),
    ])

    content = response.content if isinstance(response.content, str) else str(response.content)

    return {
        "messages": [AIMessage(content=f"[RESEARCH] Investigación completada.")],
        "research_data": content,
        "contributions": state.get("contributions", []) + ["research"],
    }
