import os
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from src.config import settings

class RAGSystem:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 1. Recuperador Vectorial (Pinecone)
        self.vectorstore = PineconeVectorStore(
            index_name=settings.PINECONE_INDEX_NAME,
            embedding=self.embeddings,
            text_key="text_content"
        )
        self.vector_retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        
        # 2. Recuperador Léxico (BM25)
        self.bm25_retriever = self._init_bm25_retriever()
        
        # 3. Recuperador Híbrido Oficial (EnsembleRetriever)
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever, self.vector_retriever],
            weights=[0.4, 0.6]  # 40% BM25 (léxico) y 60% Vectorial (semántico)
        )

    def _init_bm25_retriever(self) -> BM25Retriever:
        sample_corpus_path = "data/sample_docs"
        docs = []
        if os.path.exists(sample_corpus_path):
            from langchain_community.document_loaders import DirectoryLoader, TextLoader
            loader = DirectoryLoader(sample_corpus_path, glob="**/*.md", loader_cls=TextLoader)
            raw_docs = loader.load()
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
            docs = splitter.split_documents(raw_docs)
        
        # Sincronizar metadatos exactamente igual que en el pipeline de ingesta
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "unknown")
            doc.metadata["doc_id"] = f"{os.path.basename(source)}_chunk_{i}"
            doc.metadata["text_content"] = doc.page_content

        if not docs:
            docs = [Document(page_content="Documento de respaldo inicial para BM25.", metadata={"doc_id": "fallback_1"})]
            
        bm25 = BM25Retriever.from_documents(docs)
        bm25.k = 5
        return bm25

    def retrieve(self, query: str, k: int = 5):
        self.vector_retriever.search_kwargs["k"] = k
        self.bm25_retriever.k = k
        
        results = self.ensemble_retriever.invoke(query)
        return results[:k]