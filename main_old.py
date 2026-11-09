from graph import build_orchestrator_graph
from langchain_core.messages import HumanMessage

def main():
    print("Inicializando Orquestador Multi-Agente...")
    app = build_orchestrator_graph()

    # Consulta que exige investigación y análisis computacional
    query = "Necesito revisar el estado actual del sitio PBA y realizar un análisis de riesgo de sus métricas térmicas."
    
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "iteration_count": 0,
        "next_agent": "researcher"
    }

    print(f"\n[Usuario]: {query}\n" + "-"*50)

    for event in app.stream(initial_state, stream_mode="values"):
        if "messages" in event and event["messages"]:
            latest_msg = event["messages"][-1]
            print(f"[{latest_msg.__class__.__name__}]: {latest_msg.content[:200]}...\n")

    print("Flujo completado con éxito.")

if __name__ == "__main__":
    main()