# Hybrid Search: Dense + Sparse

## Why hybrid?

Pure dense (vector) search captures semantic similarity but can miss exact
technical terms, product codes or proper nouns. Pure sparse (BM25 / keyword)
search is excellent at exact matches but fails on paraphrases.

Hybrid search combines both signals.

## Dense vectors

Dense embeddings (e.g. Hugging Face `all-MiniLM-L6-v2` or `bge-small`) map text into a continuous
vector space. Cosine similarity ranks documents by meaning.

## Sparse vectors (BM25)

BM25 is a probabilistic ranking function based on term frequency and inverse
document frequency. It produces a sparse vector where only the dimensions that
correspond to present tokens are non-zero.

## Combining scores

A common approach is a weighted sum (or Reciprocal Rank Fusion):

```
final_score = α * dense_score + (1 - α) * sparse_score
```

In LangChain this is implemented by `EnsembleRetriever`:

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

ensemble = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5],
)
```

## When hybrid shines

- Technical documentation with many acronyms and API names.
- Legal or medical corpora where exact terminology is critical.
- Multi-lingual or code-mixed queries.
