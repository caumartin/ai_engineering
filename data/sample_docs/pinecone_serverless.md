# Pinecone Serverless Indexes

## Creating a Serverless Index

Pinecone Serverless indexes scale automatically: you pay only for storage and queries.
Capacity, replication and availability are managed by Pinecone.

### Python SDK (v5+)

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_API_KEY")

pc.create_index(
    name="rag-hybrid-index",
    dimension=384,                # must match embedding model (MiniLM/bge-small)
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1",
    ),
)
```

### Dimension matching (critical)

| Embedding model (Hugging Face)                    | Dimension |
|---------------------------------------------------|-----------|
| sentence-transformers/all-MiniLM-L6-v2            | 384       |
| BAAI/bge-small-en-v1.5                            | 384       |
| intfloat/multilingual-e5-small                    | 384       |
| sentence-transformers/all-mpnet-base-v2           | 768       |
| BAAI/bge-base-en-v1.5                             | 768       |

If you upsert a 384-dimensional vector into an index configured for 768, Pinecone
raises an error. Always verify `describe_index().dimension` before ingestion.

### Namespaces

Namespaces let you isolate different tenants or document collections inside the
same index without mixing results. Pass `namespace="my-tenant"` on every upsert
and query.

### Checking readiness

```python
while not pc.describe_index("rag-hybrid-index").status.get("ready"):
    time.sleep(2)
```
