"""
Agente de Análisis con LLM real de Gemini.
Procesa los datos de investigación usando el modelo.
"""

import os
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any


def get_llm(temperature: float = 0.2):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Falta GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        #temperature=temperature,
        google_api_key=api_key,
    )


def extract_text(content) -> str:
    """Extrae texto de response.content (puede ser str o list)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return " ".join(parts)
    return str(content)


def analyst_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo del Agente de Análisis usando Gemini.
    """
    research_data = state.get("research_data", "")
    user_query = state.get("user_query", "")
    iteration = state.get("iteration_count", 0)

    if not research_data:
        analysis = "No hay datos de investigación disponibles para analizar."
    else:
        llm = get_llm()

        system = """Eres un agente de análisis experto.
Recibes datos de investigación y debes:
1. Hacer un análisis de sentimiento (positivo / negativo / neutral) con justificación.
2. Extraer métricas o números relevantes si existen.
3. Dar una síntesis clara y accionable relacionada con la consulta del usuario.

Sé preciso y estructurado."""

        prompt = f"""Consulta original del usuario: {user_query}

Datos de investigación:
{research_data}

Realiza el análisis completo."""

        response = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ])

        analysis = f"""
[ANÁLISIS - Iteración {iteration}]
{extract_text(response.content)}
"""

    contribution = {
        "agent": "analyst",
        "iteration": iteration,
        "output": analysis,
    }

    return {
        "messages": [AIMessage(content=analysis[:300] + "...")],
        "analysis_result": analysis,
        "contributions": [contribution],
        "next_agent": "supervisor",
    }