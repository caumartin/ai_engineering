import json
from src.agent import grafo
from src.utils import extraer_texto, serializar_traza
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import HumanMessage


async def main():
    async with AsyncSqliteSaver.from_conn_string("checkpoints.sqlite") as checkpointer:
        app = grafo.compile(checkpointer=checkpointer)
        CONFIG = {"configurable": {"thread_id": "conversacion-demo-1"}, "recursion_limit": 10}

        print("=" * 80)
        print("🧑 Turno 1: '¿Cuántos pedidos tuvo Ana García y cuál fue el total?'")
        print("=" * 80)
        resultado1 = await app.ainvoke(
            {"messages": [HumanMessage(content="¿Cuántos pedidos tuvo Ana García y cuál fue el total?")]},
            config=CONFIG,
        )
        print("🤖", extraer_texto(resultado1["messages"][-1]))

        print("\n" + "=" * 80)
        print("🧑 Turno 2 (mismo thread_id): '¿Y Juan Pérez?'")
        print("=" * 80)
        resultado2 = await app.ainvoke(
            {"messages": [HumanMessage(content="¿Y Juan Pérez?")]},  # depende del contexto del turno 1
            config=CONFIG,
        )
        print("🤖", extraer_texto(resultado2["messages"][-1]))

        print("\n" + "=" * 80)
        print("🧑 Error forzado: '¿Cuántos pedidos tuvo el cliente Roberto Sánchez?'")
        print("=" * 80)

        config_error = {"configurable": {"thread_id": "conversacion-error-1"}, "recursion_limit": 10}

        resultado_error = await app.ainvoke(
            {"messages": [HumanMessage(content="¿Cuántos pedidos tuvo el cliente Roberto Sánchez?")]},
            config=config_error,
        )
        print("🤖", extraer_texto(resultado_error["messages"][-1]))

        return resultado1, resultado2, resultado_error


if __name__ == "__main__":
    import asyncio

    resultado1, resultado2, resultado_error = asyncio.run(main())
 
    traza_completa = {
        "turno_1_multi_paso": serializar_traza(resultado1["messages"]),
        "turno_2_memoria": serializar_traza(resultado2["messages"]),
        "prueba_error_y_aclaracion": serializar_traza(resultado_error["messages"]),
    }

    with open("traza_ejecucion.json", "w", encoding="utf-8") as f:
        json.dump(traza_completa, f, ensure_ascii=False, indent=2)


    print("\n✅ Traza guardada en traza_ejecucion.json")
    print("\nTraza del turno 1:\n" + json.dumps(traza_completa["turno_1_multi_paso"], ensure_ascii=False, indent=2))
    #print("\n\nTraza del turno 2:\n\n" + json.dumps(traza_completa["turno_2_memoria"], ensure_ascii=False, indent=2))
    #print("\n\nTraza de la prueba de error:\n\n" + json.dumps(traza_completa["prueba_error_y_aclaracion"], ensure_ascii=False, indent=2))
