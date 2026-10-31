# Buenas prácticas de RAG – Metadatos y chunking

## Qué metadatos guardar con cada chunk

Al insertar vectores en Pinecone conviene adjuntar metadatos ricos para que
la capa de recuperación pueda filtrar y la de generación pueda citar fuentes.

Campos recomendados:

| Campo        | Tipo   | Propósito                                      |
|--------------|--------|------------------------------------------------|
| `text`       | string | Contenido original del chunk (evita una BD extra) |
| `source`     | string | Nombre de archivo o URL                        |
| `page`       | int    | Número de página (para PDFs)                   |
| `category`   | string | Etiqueta de alto nivel (técnico, legal, …)     |
| `chunk_index`| int    | Posición dentro del documento original         |

Ejemplo de payload de upsert:

```python
{
    "id": "a1b2c3…",
    "values": [0.012, -0.034, …],   # embedding de 384 dims (MiniLM)
    "metadata": {
        "text": "El RecursiveCharacterTextSplitter …",
        "source": "langchain_text_splitters.md",
        "page": 0,
        "category": "technical",
        "chunk_index": 3,
    }
}
```

## Guías de chunking

- Objetivo: 500–800 tokens (≈ 700–1100 caracteres en español/inglés).
- Usa 10–20 % de solapamiento para no perder hechos que caen en el límite.
- Prefiere divisores recursivos que respeten párrafos y oraciones.
- Nunca embeds un manual largo como un solo vector.

## Namespaces

Usa un namespace dedicado por inquilino o por colección de documentos. Así las
consultas son más rápidas y se evita la contaminación cruzada de resultados.

## Evaluación

Mantén siempre un golden set pequeño de pares (pregunta, documento_esperado) y
mide Precision@k y Recall@k después de cada cambio en el pipeline.
