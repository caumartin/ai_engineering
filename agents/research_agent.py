# agents/research_agent.py
from langgraph.prebuilt import create_react_agent
from tools.custom_tools import query_sales_and_products_db

def create_researcher_node(llm):
    tools = [query_sales_and_products_db]
    prompt = (
        "Eres un Agente de Investigación Comercial. Tu objetivo es utilizar las herramientas "
        "para recopilar datos precisos sobre productos, stock disponible, historiales de clientes "
        "y reportes de ventas."
    )
    return create_react_agent(llm, tools=tools, prompt=prompt)