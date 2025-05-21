import os
import uuid
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangchainDocument
from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Constants
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Text chunking logic
def split_text_into_chunks(text: str, doc_id: str) -> List[LangchainDocument]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    chunks = splitter.split_text(text)
    return [
        LangchainDocument(
            page_content=chunk,
            metadata={
                "doc_id": doc_id,
                "chunk_index": idx,
                "page": "?",
                "paragraph": "?"
            }
        )
        for idx, chunk in enumerate(chunks)
    ]

# Embedding + ChromaDB vector store logic
def embed_and_store(text: str, persist_path: str, filename: str, file_path: str):
    if not text.strip():
        raise ValueError("No content to embed.")

    doc_id = str(uuid.uuid4())
    documents = split_text_into_chunks(text, doc_id)

    # Use a good all-purpose embedding model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_path,
        collection_name=doc_id  # Optional
    )

    vector_store.persist()

    return {
        "status": "success",
        "doc_id": doc_id,
        "chunks": len(documents),
        "persist_path": persist_path
    }
