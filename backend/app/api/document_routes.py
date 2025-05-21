# backend/app/api/document_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import logging

from app.db.session import get_db
from app.db.models import Document

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DocumentResponse(BaseModel):
    id: int
    filename: str
    author: str
    doc_type: str
    upload_time: str  # ISO 8601 formatted datetime string
    status: str


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)) -> List[DocumentResponse]:
    """
    Returns a list of all uploaded documents.
    """
    try:
        docs = db.query(Document).all()
        if not docs:
            logger.info("No documents found in the database.")
            return []
    except Exception as e:
        logger.error(f"Failed to fetch documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            author=doc.author,
            doc_type=doc.doc_type,
            upload_time=doc.upload_time.isoformat() if doc.upload_time else None,
            status=doc.status
        )
        for doc in docs
    ]
