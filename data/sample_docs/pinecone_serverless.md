# Indices Serverless de Pinecone

## Crear un índice Serverless

Los índices Serverless de Pinecone escalan automáticamente: solo pagas por almacenamiento y consultas.
La capacidad, la replicación y la disponibilidad las gestiona Pinecone.

### SDK de Python (v5+)

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_API_KEY")

pc.create_index(
    name="rag-hybrid-index",
    dimension=384,                # debe coincidir con el modelo de embeddings (MiniLM/bge-small)
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1",
    ),
)
```

### Coincidencia de dimensiones (crítico)

| Modelo de embeddings (Hugging Face)               | Dimensión |
|---------------------------------------------------|-----------|
| sentence-transformers/all-MiniLM-L6-v2            | 384       |
| BAAI/bge-small-en-v1.5                            | 384       |
| intfloat/multilingual-e5-small                    | 384       |
| sentence-transformers/all-mpnet-base-v2           | 768       |
| BAAI/bge-base-en-v1.5                             | 768       |

Si insertas un vector de 384 dimensiones en un índice configurado para 768, Pinecone
lanza un error. Siempre verifica `describe_index().dimension` antes de la ingesta.

### Namespaces

Los namespaces permiten aislar distintos inquilinos o colecciones de documentos dentro del
mismo índice sin mezclar resultados. Pasa `namespace="mi-tenant"` en cada upsert y consulta.

### Comprobar que está listo

```python
while not pc.describe_index("rag-hybrid-index").status.get("ready"):
    time.sleep(2)
```
