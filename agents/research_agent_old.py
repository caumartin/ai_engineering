from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from tools.custom_tools import search_vector_db

def create_researcher_node(llm):
    tools = [search_vector_db]
    prompt = (
        "Eres un Agente de Búsqueda e Investigación técnica. Tu trabajo es utilizar la herramienta "
        "disponible para recopilar datos precisos y pasarlos al flujo para su análisis."
    )
    return create_react_agent(llm, tools=tools, prompt=prompt)