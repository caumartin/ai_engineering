# agents/analyst_agent.py
from langgraph.prebuilt import create_react_agent
from tools.custom_tools import analyze_sales_margins

def create_analyst_node(llm):
    tools = [analyze_sales_margins]
    prompt = (
        "Eres un Agente de Análisis Financiero y de Ventas. Tu objetivo es procesar los datos "
        "comerciales obtenidos, calcular márgenes, evaluar riesgos crediticios y estructurar "
        "recomendaciones de precios o descuentos."
    )
    return create_react_agent(llm, tools=tools, prompt=prompt)