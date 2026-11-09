from typing import Literal, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState

class AgentState(MessagesState):
    """
    Estado compartido estructurado para el orquestador multi-agente.
    Hereda el campo 'messages' de MessagesState.
    """
    next_agent: Literal["researcher", "analyst", "validator", "FINISH"]
    iteration_count: int
    research_data: Optional[str] = None
    analysis_result: Optional[str] = None
    validation_status: Optional[str] = None