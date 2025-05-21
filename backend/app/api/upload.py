# backend/app/api/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.db.models import Document
from app.core.ocr import extract_paragraphs
from app.core.chunker import chunk_text
from app.services.vector_store import add_chunks_to_store, PERSIST_PATH

from pathlib import Path
import shutil
import logging
from datetime import datetime
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    """List all processed documents."""
    docs = db.query(Document).filter(Document.status == "processed").all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "author": doc.author,
            "doc_type": doc.doc_type,
            "created_at": doc.upload_time
        }
        for doc in docs
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    author: str = Form(default="unknown"),
    doc_type: str = Form(default="general"),
    db: Session = Depends(get_db)
):
    """
    Upload, OCR, chunk, embed, and store a document.
    """
    safe_filename = file.filename.replace(" ", "_")
    existing = db.query(Document).filter_by(filename=safe_filename).first()

    if existing:
        logger.info(f"📄 Document '{safe_filename}' already exists.")
        return {
            "document_id": existing.id,
            "filename": existing.filename,
            "sample": existing.ocr_text[:300] if existing.ocr_text else "",
            "full_text": existing.ocr_text or "",
            "persist_dir": PERSIST_PATH
        }

    # Save uploaded file
    data_dir = Path(settings.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / safe_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"✅ File saved: {file_path}")
    except Exception as e:
        logger.error(f"❌ File save failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save file")

    # OCR extraction
    try:
        paragraphs = extract_paragraphs(str(file_path), poppler_path=settings.POPPLER_PATH)
        for p in paragraphs:
            p.setdefault("citation", {"page": p.get("page_number"), "paragraph": p.get("paragraph_number")})
        full_text = "\n\n".join(p["text_snippet"] for p in paragraphs)
        logger.info(f"✅ OCR extracted {len(paragraphs)} paragraphs.")
    except Exception as e:
        logger.error(f"❌ OCR failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Text extraction failed")

    # Chunking and vector store
    try:
        doc_id = str(uuid.uuid4())
        chunk_texts, chunk_ids, metadata = chunk_text(text=full_text, doc_id=doc_id)

        for m in metadata:
            m["filename"] = safe_filename
            m["author"] = author
            m["doc_type"] = doc_type

        add_chunks_to_store(chunk_texts, chunk_ids, metadata, persist_path=PERSIST_PATH)
        logger.info(f"✅ Stored {len(chunk_texts)} chunks in vector store.")
    except Exception as e:
        logger.error(f"❌ Chunking or vector store failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to store in vector database")

    # Save document record to SQL DB
    try:
        new_doc = Document(
            filename=safe_filename,
            author=author,
            doc_type=doc_type,
            file_path=str(file_path),
            status="processed",
            ocr_text=full_text,
            upload_time=datetime.utcnow()
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        logger.info(f"✅ Document metadata saved to DB: {new_doc.id}")
    except Exception as e:
        logger.error(f"❌ DB save failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save document metadata")

    return {
        "document_id": new_doc.id,
        "doc_uid": doc_id,
        "filename": safe_filename,
        "text_extraction": "success",
        "chunking": f"{len(chunk_texts)} chunks created",
        "embedding": "success",
        "vector_db_storage": "ChromaDB updated",
        "persist_dir": PERSIST_PATH,
        "sample": full_text[:300],
        "full_text": full_text  # 👈 ADDED for frontend preview
    }
