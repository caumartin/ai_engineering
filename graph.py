# graph.py
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from state import AgentState
from agents.research_agent import create_researcher_node
from agents.analyst_agent import create_analyst_node
import dotenv

dotenv.load_dotenv()

def build_orchestrator_graph():
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

    researcher_agent = create_researcher_node(llm)
    analyst_agent = create_analyst_node(llm)

    def supervisor_node(state: AgentState):
        messages = state["messages"]
        iteration = state.get("iteration_count", 0)

        if iteration >= 4:
            return {"next_agent": "FINISH", "iteration_count": iteration + 1}

        system_prompt = (
            "Eres el nodo Supervisor de un Orquestador Comercial (Productos, Clientes y Ventas).\n"
            "Debes decidir quién debe actuar a continuación basándote en la conversación:\n"
            "1. Si necesitas consultar stock, historial del cliente o datos de ventas, enruta a 'researcher'.\n"
            "2. Si ya tienes los datos comerciales y necesitas calcular márgenes, descuentos o riesgos, enruta a 'analyst'.\n"
            "3. Si el análisis está completo y listo para entregar al usuario, responde 'FINISH'.\n"
            "Responde únicamente con una de estas palabras exactas: 'researcher', 'analyst', 'FINISH'."
        )
        
        prompt_input = [SystemMessage(content=system_prompt)] + messages
        if messages and isinstance(messages[-1], AIMessage):
            prompt_input.append(HumanMessage(content="Basado en lo anterior, ¿cuál es el siguiente paso ('researcher', 'analyst', 'FINISH')?"))
        print('\n[Supervisor Prompt]:', prompt_input[-1].content, '\n' + '-'*50)
        response = llm.invoke(prompt_input)
        content = response.content
        print('\n[Supervisor Decision]:', content[0]['text'], '\n' + '-'*50)
        decision = "".join([str(item) for item in content]).strip().lower() if isinstance(content, list) else str(content).strip().lower()

        if "researcher" in decision:
            next_step = "researcher"
        elif "analyst" in decision:
            next_step = "analyst"
        else:
            next_step = "FINISH"

        return {
            "next_agent": next_step,
            "iteration_count": iteration + 1
        }

    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("analyst", analyst_agent)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next_agent"],
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "FINISH": END
        }
    )

    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")

    return workflow.compile()