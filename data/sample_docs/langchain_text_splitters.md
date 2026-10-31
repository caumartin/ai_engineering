# Divisores de texto de LangChain

## RecursiveCharacterTextSplitter

El `RecursiveCharacterTextSplitter` es el divisor de texto recomendado para texto genérico.
Intenta dividir según una lista de caracteres en orden, manteniendo juntas las unidades semánticas
en la medida de lo posible.

### Cómo funciona

1. Primero intenta dividir por dobles saltos de línea (`\n\n`) – límites de párrafo.
2. Si los chunks siguen siendo demasiado grandes, recurre a saltos de línea simples (`\n`).
3. Luego prueba con puntos que terminan oraciones (`. `).
4. Por último divide por espacios y caracteres individuales.

Parámetros típicos:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,      # tamaño objetivo en caracteres (~500-800 tokens)
    chunk_overlap=120,   # solapamiento para preservar contexto entre límites
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)
chunks = splitter.split_documents(documents)
```

### Por qué importa el tamaño del chunk

- **Demasiado pequeño** (< 200 tokens): los embeddings pierden contexto y la recuperación se vuelve ruidosa.
- **Demasiado grande** (> 1500 tokens): el embedding diluye la señal de cada hecho.
- **Punto óptimo**: 500–800 tokens con 10–20 % de solapamiento.

### Metadatos preservados

Cada `Document` resultante conserva los metadatos originales (`source`, `page`, …) y
añade un `chunk_index` secuencial para poder reconstruir el orden después.
