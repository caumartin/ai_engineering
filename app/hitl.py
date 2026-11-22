"""Nodo Human-in-the-Loop."""
from langgraph.types import interrupt
from langchain_core.messages import AIMessage
from agents.state import AgentState


def is_critical_task(state: AgentState) -> bool:
    return state.get("is_critical", False)


def hitl_node(state: AgentState) -> dict:
    """Pausa la ejecución hasta recibir aprobación externa."""
    payload = {
        "job_id": state.get("job_id"),
        "query": state.get("user_query"),
        "message": "Esta tarea fue marcada como crítica y requiere aprobación humana.",
    }
    decision = interrupt(payload)
    approved = decision.get("approved", False) if isinstance(decision, dict) else bool(decision)

    return {
        "messages": [AIMessage(content=f"[HITL] Aprobación recibida: {approved}")],
        "human_approved": approved,
        "contributions": state.get("contributions", []) + ["hitl"],
    }
