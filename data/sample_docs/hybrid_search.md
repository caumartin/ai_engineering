# Búsqueda híbrida: denso + disperso

## ¿Por qué híbrida?

La búsqueda densa pura (vectorial) captura similitud semántica pero puede fallar con
términos técnicos exactos, códigos de producto o nombres propios. La búsqueda dispersa pura
(BM25 / palabras clave) es excelente con coincidencias exactas pero falla con paráfrasis.

La búsqueda híbrida combina ambas señales.

## Vectores densos

Los embeddings densos (por ejemplo Hugging Face `all-MiniLM-L6-v2` o `bge-small`) proyectan
el texto en un espacio vectorial continuo. La similitud coseno ordena documentos por significado.

## Vectores dispersos (BM25)

BM25 es una función de ranking probabilística basada en frecuencia de términos y frecuencia
inversa de documentos. Produce un vector disperso donde solo las dimensiones de los tokens
presentes son distintas de cero.

## Combinar puntuaciones

Un enfoque habitual es una suma ponderada (o Reciprocal Rank Fusion):

```
puntuacion_final = α * puntuacion_densa + (1 - α) * puntuacion_dispersa
```

En LangChain esto se implementa con `EnsembleRetriever`:

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

ensemble = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5],
)
```

## Cuándo brilla lo híbrido

- Documentación técnica con muchos acrónimos y nombres de API.
- Corpora legales o médicos donde la terminología exacta es crítica.
- Consultas multilingües o con código mezclado.
