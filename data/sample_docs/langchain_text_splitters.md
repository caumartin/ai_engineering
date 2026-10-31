# LangChain Text Splitters

## RecursiveCharacterTextSplitter

The `RecursiveCharacterTextSplitter` is the recommended text splitter for generic text.
It tries to split on a list of characters in order, keeping semantic units together
as much as possible.

### How it works

1. It first attempts to split on double newlines (`\n\n`) – paragraph boundaries.
2. If chunks are still too large, it falls back to single newlines (`\n`).
3. Then it tries sentence-ending periods (`. `).
4. Finally it splits on spaces and individual characters.

Typical parameters:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,      # target size in characters (~500-800 tokens)
    chunk_overlap=120,   # overlap to preserve context across boundaries
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)
chunks = splitter.split_documents(documents)
```

### Why chunk size matters

- **Too small** (< 200 tokens): embeddings lose surrounding context and retrieval becomes noisy.
- **Too large** (> 1500 tokens): the embedding dilutes the signal of any single fact.
- **Sweet spot**: 500–800 tokens with 10–20 % overlap.

### Metadata preserved

Each resulting `Document` keeps the original metadata (`source`, `page`, …) and
adds a sequential `chunk_index` so you can reconstruct order later.
