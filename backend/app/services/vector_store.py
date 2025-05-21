# backend/app/services/vector_store.py

import os
import logging
from typing import Optional, List, Dict

from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from app.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Configuration: default directory for persisted vector store
PERSIST_PATH = os.getenv("CHROMA_PERSIST_PATH", "./chroma_store")

# Initialize embedding function
embedding_model = settings.EMBEDDING_MODEL or "sentence-transformers/all-MiniLM-L6-v2"
embedding_function = HuggingFaceEmbeddings(model_name=embedding_model)


def load_vector_store(persist_path: Optional[str] = None) -> Chroma:
    """
    Loads an existing Chroma vector store.
    """
    path = persist_path or PERSIST_PATH
    try:
        vector_store = Chroma(
            persist_directory=path,
            embedding_function=embedding_function
        )
        logger.info(f"✅ Loaded Chroma vector store from: {path}")
        return vector_store
    except Exception as e:
        logger.error(f"❌ Failed to load vector store at {path}: {e}", exc_info=True)
        raise


def add_chunks_to_store(
    chunk_texts: List[str],
    chunk_ids: List[str],
    metadatas: List[Dict],
    persist_path: Optional[str] = None
) -> None:
    """
    Adds new text chunks to the vector store with metadata and persists them.
    """
    try:
        vector_store = load_vector_store(persist_path)
        vector_store.add_texts(
            texts=chunk_texts,
            metadatas=metadatas,
            ids=chunk_ids
        )
        vector_store.persist()
        store_path = persist_path or PERSIST_PATH
        logger.info(f"✅ Added {len(chunk_texts)} chunks to Chroma vector store at {store_path}.")
    except Exception as e:
        logger.error(f"❌ Failed to add chunks to vector store: {e}", exc_info=True)


def query_similar_chunks(
    query: str,
    top_k: int = 5,
    filter: Optional[Dict] = None,
    persist_path: Optional[str] = None
) -> List[Dict]:
    """
    Query the vector store for top_k similar chunks given a user query.
    """
    try:
        vector_store = load_vector_store(persist_path)
        results = vector_store.similarity_search_with_score(
            query=query,
            k=top_k,
            filter=filter if filter else None
        )
        return [
            {
                "text": doc.page_content,
                "score": score,
                "metadata": doc.metadata
            }
            for doc, score in results
        ]
    except Exception as e:
        logger.error(f"❌ Similarity search failed: {e}", exc_info=True)
        return []
