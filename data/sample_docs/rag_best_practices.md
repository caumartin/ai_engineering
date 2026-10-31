# RAG Best Practices – Metadata & Chunking

## What metadata to store with each chunk

When you upsert vectors into Pinecone you should attach rich metadata so that
the retrieval layer can filter and the generation layer can cite sources.

Recommended fields:

| Field        | Type   | Purpose                                      |
|--------------|--------|----------------------------------------------|
| `text`       | string | Original chunk content (avoids extra DB)     |
| `source`     | string | File name or URL                             |
| `page`       | int    | Page number (for PDFs)                       |
| `category`   | string | High-level tag (technical, legal, …)         |
| `chunk_index`| int    | Position inside the original document        |

Example upsert payload:

```python
{
    "id": "a1b2c3…",
    "values": [0.012, -0.034, …],   # 384-dim embedding (MiniLM)
    "metadata": {
        "text": "The RecursiveCharacterTextSplitter …",
        "source": "langchain_text_splitters.md",
        "page": 0,
        "category": "technical",
        "chunk_index": 3,
    }
}
```

## Chunking guidelines

- Target 500–800 tokens (≈ 700–1100 characters for English).
- Use 10–20 % overlap so facts that sit on a boundary are not lost.
- Prefer recursive splitters that respect paragraph and sentence boundaries.
- Never embed the whole document as a single vector for long manuals.

## Namespaces

Use a dedicated namespace per tenant or per document collection. This keeps
queries fast and avoids cross-contamination of results.

## Evaluation

Always maintain a small golden set of (question, expected_source) pairs and
measure Precision@k and Recall@k after every change to the pipeline.
