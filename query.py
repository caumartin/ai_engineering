import sys
import os
import random

# Asegurar visibilidad del módulo src
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.retriever import RAGSystem

# Banco de consultas aleatorias predeterminadas
SAMPLE_QUERIES = [
    "¿Cómo se configura el cliente de Pinecone para índices serverless?",
    "¿Qué tamaño de chunk se recomienda usar con RecursiveCharacterTextSplitter?",
    "¿Por qué es útil guardar el texto original en los metadatos de Pinecone?",
    "¿Qué ventajas aporta combinar búsqueda semántica con BM25 en un EnsembleRetriever?",
    "¿Qué mide exactamente la métrica Recall@k en la evaluación de un RAG?"
]

def main():
    print("Inicializando Sistema RAG Híbrido (Pinecone + BM25)...")
    rag = RAGSystem()
    
    # Si el usuario pasó argumentos por consola, los usamos como consulta. Si no, elegimos una aleatoria.
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n🔍 Consulta ingresada por el usuario:")
    else:
        query = random.choice(SAMPLE_QUERIES)
        print(f"\n🎲 Consulta aleatoria seleccionada automáticamente:")

    print(f"-> \"{query}\"\n")
    print("Buscando los Top-5 documentos más relevantes...\n" + "=" * 65)

    # Ejecutar recuperación híbrida
    results = rag.retrieve(query, k=5)

    if not results:
        print("⚠️ No se encontraron documentos relevantes para esta consulta.")
        return

    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "Desconocido")
        doc_id = doc.metadata.get("doc_id", "N/A")
        
        print(f"📄 Resultado [{i}]")
        print(f"   • Archivo Fuente : {source}")
        print(f"   • Chunk ID       : {doc_id}")
        print(f"   • Extracto       :")
        # Mostrar las primeras 300 letras del contenido con formato limpio
        content_snippet = doc.page_content.replace("\n", " ")
        print(f"     \"{content_snippet[:300]}...\"")
        print("-" * 65)

if __name__ == "__main__":
    main()