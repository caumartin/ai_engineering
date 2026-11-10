"""
Agente de Investigación con LLM real de Gemini.
Usa herramientas y razonamiento del modelo.
"""

import os
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any


def get_llm(temperature: float = 0.3):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Falta GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        #temperature=temperature,
        google_api_key=api_key,
    )


@tool
def search_web(query: str) -> str:
    """
    Busca información relevante en fuentes externas.
    En esta versión simulada retorna datos mock. 
    Puedes reemplazarla por TavilySearchResults cuando tengas la API key.
    """
    mock_results = {
        "ia": "El mercado de IA creció un 35% en 2025. Principales jugadores: OpenAI, Google DeepMind, Anthropic. Tendencia fuerte hacia agentes autónomos y multimodalidad.",
        "mercado": "El mercado de inteligencia artificial alcanzó los 200 mil millones de dólares en 2025, con crecimiento anual del 35%.",
        "default": f"Resultados de búsqueda para '{query}': Se encontraron fuentes relevantes con datos actualizados sobre el tema.",
    }
    query_lower = query.lower()
    for key in mock_results:
        if key in query_lower:
            return mock_results[key]
    return mock_results["default"]


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


def research_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo del Agente de Investigación usando Gemini.
    """
    user_query = state.get("user_query", "")
    iteration = state.get("iteration_count", 0)

    llm = get_llm()

    # Bind tools
    llm_with_tools = llm.bind_tools([search_web])

    system = """Eres un agente de investigación experto.
Tu tarea es buscar información relevante sobre la consulta del usuario.
Usa la herramienta search_web cuando necesites datos.
Luego resume los hallazgos de forma clara y concisa."""

    messages = [
        SystemMessage(content=system),
        HumanMessage(content=f"Investiga y resume: {user_query}"),
    ]

    # Primera llamada (puede pedir tool)
    response = llm_with_tools.invoke(messages)

    # Si pide herramienta, ejecutarla y continuar
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call["name"] == "search_web":
            result = search_web.invoke(tool_call["args"])
            messages.append(response)
            messages.append(HumanMessage(content=f"Resultado de la herramienta: {result}"))
            final_response = llm.invoke(messages)
            research_output = extract_text(final_response.content)
        else:
            research_output = extract_text(response.content)
    else:
        research_output = extract_text(response.content)

    research_output = f"""
[INVESTIGACIÓN - Iteración {iteration}]
{research_output}

Fuentes: search_web (simulada)
"""

    contribution = {
        "agent": "research",
        "iteration": iteration,
        "output": research_output,
        "tool_used": "search_web",
    }

    return {
        "messages": [AIMessage(content=research_output[:300] + "...")],
        "research_data": research_output,
        "contributions": [contribution],
        "next_agent": "supervisor",
    }