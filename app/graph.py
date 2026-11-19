"""
Orquestador multi-agente con RedisSaver y nodo HITL.
Basado en el sistema del Módulo 6.
"""
import os
import redis as redis_sync
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AgentState
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from app.hitl import hitl_node, is_critical_task

import dotenv
dotenv.load_dotenv()

import logging
logger = logging.getLogger(__name__)

MAX_ITERATIONS = 6
SUPERVISOR_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
AGENT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def get_llm(model_name: str = AGENT_MODEL, temperature: float = 0.2):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Falta GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key,
    )


def supervisor_node(state: AgentState) -> dict:
    iteration = state.get("iteration_count", 0) + 1
    research = state.get("research_data")
    analysis = state.get("analysis_result")
    user_query = state.get("user_query", "")
    human_approved = state.get("human_approved")

    if iteration > MAX_ITERATIONS:
        return {
            "messages": [AIMessage(content="[SUPERVISOR] Límite de iteraciones alcanzado.")],
            "next_agent": "FINISH",
            "iteration_count": iteration,
            "task_completed": True,
            "validation_feedback": "Límite de iteraciones alcanzado.",
        }

    # Si es crítica y no está aprobada, ir a HITL
    if is_critical_task(state) and human_approved is None:
        return {
            "messages": [AIMessage(content="[SUPERVISOR] Tarea crítica detectada. Requiere aprobación humana.")],
            "next_agent": "hitl",
            "iteration_count": iteration,
            "validation_feedback": "Redirigiendo a HITL",
        }

    llm = get_llm(SUPERVISOR_MODEL, temperature=0.1)

    system_prompt = """Eres el Supervisor de un sistema multi-agente.
Decide el siguiente paso basándote en el estado actual.

Opciones válidas (responde EXACTAMENTE una de estas palabras):
- research
- analyst
- FINISH

Reglas:
- Si no hay datos de investigación → research
- Si hay investigación pero no hay análisis → analyst
- Si ambos existen y son de calidad suficiente → FINISH
- Nunca inventes otras opciones.

Responde SOLO con: research, analyst o FINISH."""

    human_content = f"""Consulta del usuario: {user_query}

Estado actual:
- research_data: {research[:500] if research else "VACÍO"}
- analysis_result: {analysis[:500] if analysis else "VACÍO"}
- Iteración: {iteration}
- Aprobación humana: {human_approved}

¿Cuál es el siguiente paso?"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content),
    ])

    raw_content = response.content
    if isinstance(raw_content, list):
        text_parts = []
        for block in raw_content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
        decision = " ".join(text_parts).strip().lower()
    else:
        decision = str(raw_content).strip().lower()

    if "finish" in decision:
        decision = "FINISH"
    elif "analyst" in decision:
        decision = "analyst"
    elif "research" in decision:
        decision = "research"
    else:
        if not research:
            decision = "research"
        elif not analysis:
            decision = "analyst"
        else:
            decision = "FINISH"

    validation = f"Supervisor decidió: {decision}"

    return {
        "messages": [AIMessage(content=f"[SUPERVISOR] Iteración {iteration}: {validation}")],
        "next_agent": decision,
        "iteration_count": iteration,
        "validation_feedback": validation,
        "task_completed": decision == "FINISH",
    }


def route_decision(state: AgentState) -> Literal["research", "analyst", "hitl", "FINISH"]:
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH" or state.get("task_completed"):
        return "FINISH"
    if next_agent == "hitl":
        return "hitl"
    return next_agent


from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import redis.asyncio as redis_async

# Global checkpointer (kept alive for the process lifetime)
_checkpointer = None


async def get_checkpointer(redis_url: str = None):
    """Obtiene o crea el AsyncRedisSaver (singleton)."""
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
    # AsyncRedisSaver.from_conn_string es un async context manager
    # Para uso de larga duración creamos el cliente y el saver manualmente
    client = redis_async.from_url(redis_url, decode_responses=False)
    _checkpointer = AsyncRedisSaver(redis_client=client)
    await _checkpointer.asetup()  # Crear índices (solo necesario una vez)
    logger.info(f"AsyncRedisSaver initialized → {redis_url}")
    return _checkpointer


async def build_graph(redis_url: str = None):
    """Construye el grafo con AsyncRedisSaver como checkpointer."""
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("hitl", hitl_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "research": "research",
            "analyst": "analyst",
            "hitl": "hitl",
            "FINISH": END,
        },
    )

    workflow.add_edge("research", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("hitl", "supervisor")

    checkpointer = await get_checkpointer(redis_url)
    app = workflow.compile(checkpointer=checkpointer)
    return app
