"""
Nodo Human-in-the-Loop para aprobación en tareas críticas.
"""
from typing import Dict, Any
from langgraph.types import interrupt
from langchain_core.messages import AIMessage


def is_critical_task(state: Dict[str, Any]) -> bool:
    """Determina si la tarea requiere aprobación humana."""
    query = state.get("user_query", "").lower()
    critical_keywords = [
        "ejecutar", "borrar", "eliminar", "pagar", "transferir",
        "comprar", "vender", "deploy", "producción", "crítico",
        "urgente", "costo alto", "acción", "modificar"
    ]
    return any(kw in query for kw in critical_keywords) or state.get("is_critical", False)


def hitl_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo de aprobación humana.
    Pausa la ejecución hasta recibir aprobación externa vía interrupt().
    """
    if not is_critical_task(state):
        return {
            "messages": [AIMessage(content="[HITL] Tarea no crítica. Continuando.")],
            "human_approved": True,
        }

    # Interrumpir y esperar aprobación humana
    approval = interrupt({
        "type": "human_approval_required",
        "reason": "Tarea identificada como crítica",
        "query": state.get("user_query"),
        "research_summary": (state.get("research_data") or "")[:500],
        "message": "Esta tarea requiere aprobación humana antes de continuar.",
    })

    approved = False
    if isinstance(approval, dict):
        approved = approval.get("approved", False)
    elif isinstance(approval, bool):
        approved = approval
    elif isinstance(approval, str):
        approved = approval.lower() in ("true", "yes", "approved", "sí", "si")

    return {
        "messages": [AIMessage(content=f"[HITL] Aprobación humana: {'APROBADO' if approved else 'RECHAZADO'}")],
        "human_approved": approved,
    }
