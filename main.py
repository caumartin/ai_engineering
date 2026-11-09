# main.py
import os
from dotenv import load_dotenv
from graph import build_orchestrator_graph
from langchain_core.messages import HumanMessage

load_dotenv()

def main():
    print("Inicializando Orquestador Multi-Agente (Módulo Comercial)...")
    app = build_orchestrator_graph()

    # Consulta orientada a productos, clientes y ventas
    query = "Quiero verificar el stock del producto servidor y analizar si podemos otorgarle un descuento especial al cliente ACME S.A."
    
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "iteration_count": 0,
        "next_agent": "researcher"
    }

    print(f"\n[Usuario]: {query}\n" + "-"*50)

    for event in app.stream(initial_state, stream_mode="values"):
        if "messages" in event and event["messages"]:
            latest_msg = event["messages"][-1]
            if latest_msg.__class__.__name__ == "HumanMessage":
                print(f"[{latest_msg.__class__.__name__}]: {latest_msg.content[:250]}...\n")
            elif latest_msg.__class__.__name__ == "AIMessage":
                print(f"[{latest_msg.__class__.__name__}]: {latest_msg.content[0]['text'][:500]}...\n")
    
    print("Flujo comercial completado con éxito.")

if __name__ == "__main__":
    main()