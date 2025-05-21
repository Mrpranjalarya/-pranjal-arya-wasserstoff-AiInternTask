# backend/app/services/embed_pdf.py

import os
import logging
from app.core.extract_text_from_pdf import extract_text_from_pdf
from app.core.embed import embed_and_store

logger = logging.getLogger(__name__)

def embed_pdf(file_path: str, persist_dir: str):
    """
    Extracts text from a PDF and embeds it into the vector store.

    Args:
        file_path (str): Path to the PDF file.
        persist_dir (str): Directory to persist the vector store.

    Returns:
        dict: Embedding result with status and metadata.
    """
    if not os.path.exists(file_path):
        logger.error(f"PDF file not found: {file_path}")
        return {"status": "error", "message": "File not found."}

    filename = os.path.basename(file_path)
    logger.info(f"📄 Processing PDF: {filename}")

    # Extract text
    text = extract_text_from_pdf(file_path)
    if not text:
        logger.warning(f"No text extracted from {filename}")
        return {"status": "error", "message": "No text found in PDF."}

    # Embed and store
    try:
        result = embed_and_store(
            text=text,
            persist_path=persist_dir,
            filename=filename,
            file_path=file_path
        )
        logger.info(f"✅ Successfully embedded: {filename}")
        return result
    except Exception as e:
        logger.error(f"Failed to embed PDF: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
