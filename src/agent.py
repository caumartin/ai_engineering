from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from src.tools import herramientas
import dotenv

dotenv.load_dotenv()  # carga las variables de entorno del archivo .env, para que el LLM pueda leer la API key de Google

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
llm_con_herramientas = llm.bind_tools(herramientas)


async def nodo_modelo(state: MessagesState) -> dict:
    """Le pasa el historial completo al LLM y devuelve su respuesta (que puede
    incluir tool_calls o ser la respuesta final)."""
    respuesta = await llm_con_herramientas.ainvoke(state["messages"])
    return {"messages": [respuesta]}


grafo = StateGraph(MessagesState)  # hereda el reducer add_messages, como pide la consigna
grafo.add_node("modelo", nodo_modelo)
grafo.add_node("herramientas", ToolNode(herramientas, handle_tool_errors=True))

grafo.add_edge(START, "modelo")
grafo.add_conditional_edges(
    "modelo",
    tools_condition,  # mira si el último mensaje trae tool_calls
    {"tools": "herramientas", END: END},
)
grafo.add_edge("herramientas", "modelo")  # el ciclo: vuelve al modelo con el resultado de la tool
