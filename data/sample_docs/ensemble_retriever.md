# EnsembleRetriever en LangChain

## Propósito

`EnsembleRetriever` fusiona los resultados de varios recuperadores independientes y
los reordena según pesos configurables.

## Configuración típica

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_pinecone import PineconeVectorStore

# Lado denso
vector_retriever = pinecone_store.as_retriever(search_kwargs={"k": 5})

# Lado disperso
bm25_retriever = BM25Retriever.from_documents(corpus_docs)
bm25_retriever.k = 5

# Ensemble
ensemble = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4],   # preferencia ligera por lo semántico
)
docs = ensemble.invoke("¿Cómo combina EnsembleRetriever varios recuperadores?")
```

## Algoritmo de ranking

Por defecto LangChain usa Reciprocal Rank Fusion (RRF). Cada documento recibe
una puntuación según su posición en cada recuperador; esas puntuaciones se ponderan y
se suman. Los documentos que aparecen altos en ambas listas suben al tope.

## Consejos prácticos

- Mantén el mismo `k` en cada sub-recuperador para que la fusión sea justa.
- Empieza con pesos iguales `[0.5, 0.5]` y ajústalos con un golden set pequeño.
- En corpora muy grandes, materializa el índice BM25 una vez y reutilízalo
  (BM25Retriever vive en memoria).
