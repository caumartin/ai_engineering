import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.retriever import RAGSystem

def evaluate_rag():
    benchmark_path = os.path.join(os.path.dirname(__file__), "benchmark.json")
    if not os.path.exists(benchmark_path):
        print(f"No se encontró el archivo de benchmark en {benchmark_path}")
        return

    with open(benchmark_path, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    print("Inicializando sistema RAG para evaluación...")
    rag = RAGSystem()

    total_queries = len(benchmark)
    recall_hits = 0
    total_precision_score = 0.0

    print(f"\nEjecutando evaluación sobre {total_queries} consultas del Golden Set...\n")
    print("-" * 60)

    for idx, item in enumerate(benchmark, 1):
        query = item["pregunta"]
        expected_id = item["documento_id_esperado"]

        retrieved_docs = rag.retrieve(query, k=5)
        
        retrieved_ids = [doc.metadata.get("doc_id", "sin_id") for doc in retrieved_docs]
        retrieved_sources = [doc.metadata.get("source", "sin_source") for doc in retrieved_docs]

        expected_file = expected_id.split("_chunk_")[0]
        
        # Validar si el archivo fuente esperado aparece en las fuentes recuperadas
        hit = any(expected_file in src for src in retrieved_sources) or any(expected_id == rid for rid in retrieved_ids)
        
        if hit:
            recall_hits += 1

        relevant_count = sum(1 for rid, src in zip(retrieved_ids, retrieved_sources) if expected_id in rid or expected_file in src)
        precision = relevant_count / len(retrieved_ids) if retrieved_ids else 0.0
        total_precision_score += precision

        print(f"[{idx}] Pregunta: {query}")
        print(f"    Esperado : {expected_id}")
        print(f"    Fuentes Encontradas: {retrieved_sources}")
        print(f"    IDs Encontrados    : {retrieved_ids}")
        print(f"    Hit (Recall)       : {'✅ Sí' if hit else '❌ No'} | Precision@5: {precision:.2f}")
        print("-" * 60)

    final_recall = recall_hits / total_queries if total_queries > 0 else 0.0
    final_precision = total_precision_score / total_queries if total_queries > 0 else 0.0

    print("\n" + "=" * 30 + " REPORTE DE EVALUACIÓN RAG " + "=" * 30)
    print(f"Total de Consultas Evaluadas : {total_queries}")
    print(f"Recall@5                     : {final_recall * 100:.2f}% ({recall_hits}/{total_queries})")
    print(f"Precision@5 (Promedio)       : {final_precision * 100:.2f}%")
    print("=" * 87)

if __name__ == "__main__":
    evaluate_rag()