from langgraph.prebuilt import create_react_agent
from tools.custom_tools import analyze_metrics_data

def create_analyst_node(llm):
    tools = [analyze_metrics_data]
    prompt = (
        "Eres un Agente de Análisis y Cómputo. Tu objetivo es procesar los datos de investigación "
        "recibidos, calcular métricas de riesgo y estructurar un informe técnico claro."
    )
    return create_react_agent(llm, tools=tools, prompt=prompt)