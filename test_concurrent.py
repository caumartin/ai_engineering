#!/usr/bin/env python3
"""
Script de prueba: envía 5 consultas distintas a la API en paralelo.
Uso: python test_concurrent.py
"""
import asyncio
import httpx
import json

API_URL = "http://localhost:8000/tasks"

QUERIES = [
    {"query": "Explica qué es RAG y por qué reduce alucinaciones", "is_critical": False},
    {"query": "Describe la arquitectura de un sistema multi-agente con supervisor", "is_critical": False},
    {"query": "Qué es Arize Phoenix y para qué se usa en observabilidad de LLMs", "is_critical": False},
    {"query": "Cómo funciona el checkpointer de LangGraph con Redis", "is_critical": False},
    {"query": "Ventajas de usar FastAPI para APIs asíncronas de IA", "is_critical": False},
]


async def send_task(client: httpx.AsyncClient, payload: dict, index: int):
    try:
        resp = await client.post(API_URL, json=payload, timeout=30.0)
        data = resp.json()
        print(f"[{index}] {payload['query'][:50]}... → {data.get('job_id')} ({data.get('status')})")
        return data
    except Exception as e:
        print(f"[{index}] ERROR: {e}")
        return None


async def main():
    print("Enviando 5 consultas distintas en paralelo...\n")
    async with httpx.AsyncClient() as client:
        tasks = [send_task(client, q, i + 1) for i, q in enumerate(QUERIES)]
        results = await asyncio.gather(*tasks)

    print("\n--- Resultados ---")
    for r in results:
        if r:
            print(f"  job_id: {r.get('job_id')} | status: {r.get('status')}")

    print("\nConsulta el estado con:")
    print("  curl http://localhost:8000/tasks/<job_id>")
    print("\nY revisa las trazas en Phoenix: http://localhost:6006")


if __name__ == "__main__":
    asyncio.run(main())
