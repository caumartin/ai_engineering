# Sistema RAG Escalable en la Nube con Pinecone y Búsqueda Híbrida

Módulo de Recuperación Escalable implementado con **Pinecone Serverless**, **LangChain**, **Hugging Face Embeddings** y **BM25** para recuperación híbrida (semántica + léxica).


## ⚙️ Configuración del Entorno

1. Clonar el repositorio y entrar al directorio.
2. Copiar el archivo de entorno y configurar tus API Keys:
   ```bash
   cp .env.example .env

3. Crear entorno virtual e instalar dependencias
   ```bash
   python - venv env
   source env/Scripts/aactivate
   pip install -r requirements.txt

4. Para correr:
   ```bash
   python -m src.ingest # Realiza la ingesta de documentos, embedding y carga en pinecone
   python -m evaluation.evaluate # Evalua usando el Golden Set
   python query.py # Pregunta de prueba de un set predefinido
   python query.py "¿Cuáles son las ventajas de usar un EnsembleRetriever?" # Pregunta customizada