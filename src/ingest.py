import os
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from src.config import settings

def init_pinecone_index():
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index_name = settings.PINECONE_INDEX_NAME
    
    existing_indexes = [idx["name"] for idx in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Creando índice serverless en Pinecone para Hugging Face: {index_name}...")
        pc.create_index(
            name=index_name,
            dimension=384, # Dimensión nativa de all-MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print("Índice creado exitosamente.")
    else:
        print(f"El índice '{index_name}' ya existe.")
    return pc

def run_ingestion(data_path: str = "data/sample_docs"):
    init_pinecone_index()
    
    print("Cargando documentos...")
    loader = DirectoryLoader(data_path, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("No se encontraron documentos para ingestar.")
        return

    print(f"Aplicando chunking a {len(documents)} documentos...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        length_function=len
    )
    docs = text_splitter.split_documents(documents)
    
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        doc.metadata["doc_id"] = f"{os.path.basename(source)}_chunk_{i}"
        doc.metadata["text_content"] = doc.page_content

    print("Generando embeddings con Hugging Face (all-MiniLM-L6-v2) e insertando en Pinecone...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = PineconeVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        index_name=settings.PINECONE_INDEX_NAME,
        text_key="text_content"
    )
    print("¡Ingesta con Hugging Face completada con éxito!")

if __name__ == "__main__":
    run_ingestion()