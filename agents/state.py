"""Estado compartido del sistema multi-agente."""
from typing import TypedDict, Annotated, Optional, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str
    iteration_count: int
    next_agent: str
    task_completed: bool
    validation_feedback: Optional[str]
    contributions: List[str]
    research_data: Optional[str]
    analysis_result: Optional[str]
    rag_context: Optional[str]
    is_critical: bool
    human_approved: Optional[bool]
    job_id: Optional[str]
