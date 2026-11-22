"""
Sistema Intelligence - Entrega Final
Orquestador multi-agente con Supervisor + RAG + API asíncrona + Observabilidad
"""
import os
from typing import Literal, Optional, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
import redis.asyncio as redis_async
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.state import AgentState
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from agents.rag_agent import rag_agent
from app.hitl import hitl_node, is_critical_task

import dotenv
dotenv.load_dotenv()

import logging
logger = logging.getLogger(__name__)

MAX_ITERATIONS = 8
SUPERVISOR_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


from app.llm import get_llm


def supervisor_node(state: AgentState) -> dict:
    iteration = state.get("iteration_count", 0) + 1
    research = state.get("research_data")
    analysis = state.get("analysis_result")
    rag_context = state.get("rag_context")
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

    if is_critical_task(state) and human_approved is None:
        return {
            "messages": [AIMessage(content="[SUPERVISOR] Tarea crítica detectada. Requiere aprobación humana.")],
            "next_agent": "hitl",
            "iteration_count": iteration,
            "validation_feedback": "Redirigiendo a HITL",
        }

    llm = get_llm(SUPERVISOR_MODEL, temperature=0.1)

    system_prompt = """Eres el Supervisor de un sistema multi-agente de inteligencia.
Decide el siguiente paso basándote en el estado actual.

Opciones válidas (responde EXACTAMENTE una de estas palabras):
- rag
- research
- analyst
- FINISH

Reglas:
- Si la consulta requiere conocimiento específico de la base de documentos y no hay contexto RAG → rag
- Si no hay datos de investigación externa → research
- Si hay investigación o contexto RAG pero no hay análisis → analyst
- Si el análisis es suficiente y de calidad → FINISH
- Nunca inventes otras opciones.

Responde SOLO con: rag, research, analyst o FINISH."""

    human_content = f"""Consulta del usuario: {user_query}

Estado actual:
- rag_context: {"PRESENTE" if rag_context else "VACÍO"}
- research_data: {"PRESENTE" if research else "VACÍO"}
- analysis_result: {"PRESENTE" if analysis else "VACÍO"}
- Iteración: {iteration}
- Aprobación humana: {human_approved}

¿Cuál es el siguiente paso?"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content),
    ])

    raw = response.content
    if isinstance(raw, list):
        decision = " ".join(str(b) for b in raw).strip().lower()
    else:
        decision = str(raw).strip().lower()

    if "finish" in decision:
        decision = "FINISH"
    elif "analyst" in decision:
        decision = "analyst"
    elif "research" in decision:
        decision = "research"
    elif "rag" in decision:
        decision = "rag"
    else:
        if not rag_context and not research:
            decision = "rag"
        elif not analysis:
            decision = "analyst"
        else:
            decision = "FINISH"

    return {
        "messages": [AIMessage(content=f"[SUPERVISOR] Iteración {iteration}: {decision}")],
        "next_agent": decision,
        "iteration_count": iteration,
        "validation_feedback": f"Supervisor decidió: {decision}",
        "task_completed": decision == "FINISH",
    }


def route_decision(state: AgentState) -> Literal["rag", "research", "analyst", "hitl", "FINISH"]:
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH" or state.get("task_completed"):
        return "FINISH"
    if next_agent == "hitl":
        return "hitl"
    return next_agent


_checkpointer = None


async def get_checkpointer(redis_url: str = None):
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
    client = redis_async.from_url(redis_url, decode_responses=False)
    _checkpointer = AsyncRedisSaver(redis_client=client)
    await _checkpointer.asetup()
    logger.info(f"AsyncRedisSaver inicializado → {redis_url}")
    return _checkpointer


async def build_graph(redis_url: str = None):
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag", rag_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("hitl", hitl_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "rag": "rag",
            "research": "research",
            "analyst": "analyst",
            "hitl": "hitl",
            "FINISH": END,
        },
    )

    workflow.add_edge("rag", "supervisor")
    workflow.add_edge("research", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("hitl", "supervisor")

    checkpointer = await get_checkpointer(redis_url)
    return workflow.compile(checkpointer=checkpointer)
