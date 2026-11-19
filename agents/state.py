"""
Estado compartido del Orquestador Multi-Agente.
Hereda de MessagesState de LangGraph para el historial de mensajes.
"""
from typing import Annotated, Optional, List, Dict, Any
from langgraph.graph.message import MessagesState
from operator import add


class AgentState(MessagesState):
    """
    Estado estructurado compartido entre Supervisor y Agentes Especialistas.
    """
    next_agent: str = "supervisor"
    research_data: Optional[str] = None
    analysis_result: Optional[str] = None
    task_completed: bool = False
    iteration_count: int = 0
    contributions: Annotated[List[Dict[str, Any]], add] = []
    validation_feedback: Optional[str] = None
    user_query: str = ""
    is_critical: bool = False
    human_approved: Optional[bool] = None
    job_id: Optional[str] = None
