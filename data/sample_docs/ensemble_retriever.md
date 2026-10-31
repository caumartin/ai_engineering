# EnsembleRetriever in LangChain

## Purpose

`EnsembleRetriever` merges the results of several independent retrievers and
re-ranks them according to configurable weights.

## Typical configuration

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_pinecone import PineconeVectorStore

# Dense side
vector_retriever = pinecone_store.as_retriever(search_kwargs={"k": 5})

# Sparse side
bm25_retriever = BM25Retriever.from_documents(corpus_docs)
bm25_retriever.k = 5

# Ensemble
ensemble = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.6, 0.4],   # slightly prefer semantic
)
docs = ensemble.invoke("How does EnsembleRetriever combine multiple retrievers?")
```

## Ranking algorithm

By default LangChain uses Reciprocal Rank Fusion (RRF). Each document receives
a score based on its rank in every retriever; the scores are then weighted and
summed. Documents that appear high in both lists rise to the top.

## Practical tips

- Keep the same `k` on every sub-retriever so the fusion is fair.
- Start with equal weights `[0.5, 0.5]` and tune on a small golden set.
- For very large corpora, materialise the BM25 index once and reuse it
  (BM25Retriever is in-memory).
