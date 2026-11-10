"""
Estado compartido del Orquestador Multi-Agente.
Hereda de MessagesState de LangGraph para el historial de mensajes.
Campos adicionales rastrean contribuciones, decisiones del supervisor y control de flujo.
"""

from typing import Annotated, Literal, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import MessagesState
from operator import add


class AgentState(MessagesState):
    """
    Estado estructurado compartido entre Supervisor y Agentes Especialistas.
    
    - messages: historial de conversación (heredado)
    - next_agent: siguiente nodo a ejecutar (decidido por el Supervisor)
    - research_data: datos crudos o resumidos del agente de investigación
    - analysis_result: resultado procesado por el agente de análisis
    - task_completed: flag de finalización
    - iteration_count: contador para evitar bucles infinitos
    - contributions: registro de qué agente aportó qué (para trazabilidad)
    - validation_feedback: feedback del supervisor o validador
    """
    next_agent: str = "supervisor"
    research_data: Optional[str] = None
    analysis_result: Optional[str] = None
    task_completed: bool = False
    iteration_count: int = 0
    contributions: Annotated[List[Dict[str, Any]], add] = []
    validation_feedback: Optional[str] = None
    user_query: str = ""