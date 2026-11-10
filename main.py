"""
Orquestador Multi-Agente con modelos reales de Gemini.
Supervisor + Research Agent + Analyst Agent (todos con LLM).
"""

import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from state import AgentState
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent

import dotenv
dotenv.load_dotenv()  # Carga variables de entorno desde .env


# Límite de iteraciones para evitar bucles infinitos
MAX_ITERATIONS = 6

# Modelos Gemini (ajusta según tu API key y disponibilidad)
SUPERVISOR_MODEL = "gemini-3.5-flash-lite"
AGENT_MODEL = "gemini-3.5-flash-lite"


def get_llm(model_name: str = AGENT_MODEL, temperature: float = 0.2):
    """Crea instancia de ChatGoogleGenerativeAI. Requiere GOOGLE_API_KEY en el entorno."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Falta GOOGLE_API_KEY. Exporta la variable de entorno:\n"
            "export GOOGLE_API_KEY='tu-api-key'"
        )
    return ChatGoogleGenerativeAI(
        model=model_name,
        #temperature=temperature,
        google_api_key=api_key,
    )


def supervisor_node(state: AgentState) -> dict:
    """
    Nodo Supervisor con LLM real de Gemini.
    Analiza el estado y decide el siguiente agente o FINISH.
    """
    iteration = state.get("iteration_count", 0) + 1
    research = state.get("research_data")
    analysis = state.get("analysis_result")
    user_query = state.get("user_query", "")
    messages = state.get("messages", [])

    # Forzar parada por límite de iteraciones
    if iteration > MAX_ITERATIONS:
        return {
            "messages": [AIMessage(content="[SUPERVISOR] Límite de iteraciones alcanzado. Finalizando.")],
            "next_agent": "FINISH",
            "iteration_count": iteration,
            "task_completed": True,
            "validation_feedback": "Límite de iteraciones alcanzado.",
        }

    llm = get_llm(SUPERVISOR_MODEL, temperature=0.1)

    system_prompt = """Eres el Supervisor de un sistema multi-agente.
Tu única tarea es decidir el siguiente paso basándote en el estado actual.

Opciones válidas (responde EXACTAMENTE una de estas palabras):
- research
- analyst
- FINISH

Reglas:
- Si no hay datos de investigación (research_data vacío o None) → research
- Si hay investigación pero no hay análisis (analysis_result vacío) → analyst
- Si ambos existen y son de calidad suficiente para responder la consulta del usuario → FINISH
- Si el análisis es muy pobre o incompleto, puedes volver a pedir analyst (máximo 1 vez extra)
- Nunca inventes otras opciones.

Responde SOLO con una de las tres palabras: research, analyst o FINISH.
No des explicaciones adicionales."""

    human_content = f"""Consulta del usuario: {user_query}

Estado actual:
- research_data: {research[:500] if research else "VACÍO"}
- analysis_result: {analysis[:500] if analysis else "VACÍO"}
- Iteración actual: {iteration}

¿Cuál es el siguiente paso?"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content),
    ])

    # Gemini a veces devuelve content como lista de bloques
    raw_content = response.content
    if isinstance(raw_content, list):
        # Extraer el texto de los bloques
        text_parts = []
        for block in raw_content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])
        decision = " ".join(text_parts).strip().lower()
    else:
        decision = str(raw_content).strip().lower()

    # Normalizar respuesta del modelo
    if "finish" in decision:
        decision = "FINISH"
    elif "analyst" in decision:
        decision = "analyst"
    elif "research" in decision:
        decision = "research"
    else:
        # Fallback seguro
        if not research:
            decision = "research"
        elif not analysis:
            decision = "analyst"
        else:
            decision = "FINISH"

    validation = f"Supervisor (Gemini) decidió: {decision}"

    return {
        "messages": [AIMessage(content=f"[SUPERVISOR] Iteración {iteration}: {validation}")],
        "next_agent": decision,
        "iteration_count": iteration,
        "validation_feedback": validation,
        "task_completed": decision == "FINISH",
    }


def route_decision(state: AgentState) -> Literal["research", "analyst", "FINISH"]:
    """Arista condicional."""
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH" or state.get("task_completed"):
        return "FINISH"
    return next_agent


def build_graph():
    """Construye y compila el StateGraph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_agent)
    workflow.add_node("analyst", analyst_agent)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "research": "research",
            "analyst": "analyst",
            "FINISH": END,
        },
    )

    workflow.add_edge("research", "supervisor")
    workflow.add_edge("analyst", "supervisor")

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app, workflow


def run_orchestrator(user_query: str, thread_id: str = "demo-thread"):
    """Ejecuta el orquestador con modelos reales de Gemini."""
    app, _ = build_graph()

    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "iteration_count": 0,
        "task_completed": False,
        "contributions": [],
        "research_data": None,
        "analysis_result": None,
    }

    config = {"configurable": {"thread_id": thread_id}}

    print(f"\n{'='*60}")
    print(f"CONSULTA: {user_query}")
    print(f"{'='*60}\n")

    final_state = None
    for event in app.stream(initial_state, config, stream_mode="values"):
        final_state = event
        if event.get("messages"):
            last = event["messages"][-1]
            if hasattr(last, "content") and "[SUPERVISOR]" in last.content:
                print(last.content)

    print(f"\n{'='*60}")
    print("RESULTADO FINAL")
    print(f"{'='*60}")

    if final_state:
        print("\n--- Investigación ---")
        print(final_state.get("research_data", "N/A"))
        print("\n--- Análisis ---")
        print(final_state.get("analysis_result", "N/A"))
        print(f"\nTarea completada: {final_state.get('task_completed')}")
        print(f"Iteraciones: {final_state.get('iteration_count')}")

    return final_state


if __name__ == "__main__":
    query = "Analiza el estado actual del mercado de inteligencia artificial y da un sentimiento general."
    run_orchestrator(query)