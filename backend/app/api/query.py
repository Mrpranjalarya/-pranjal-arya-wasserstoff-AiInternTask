# backend/app/api/query.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from anyio import to_thread
import logging
import datetime
import json

from app.db.session import get_db
from app.db.models import QueryLog
from app.services.llm_service import generate_answer
from app.services.vector_store import PERSIST_PATH

# Set up logging to include DEBUG messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    doc_ids: Optional[List[int]] = None  # Placeholder for future filtering
    top_k: Optional[int] = 5             # Placeholder for future ranking

class QueryResponse(BaseModel):
    answer: str
    citations: List[dict]
    themes: List[str]
    tabular_results: List[dict] = []
    synthesized_summary: Optional[str] = None

def safe_json_dumps(data):
    try:
        return json.dumps(data)
    except Exception:
        return json.dumps(str(data))

@router.post("/", response_model=QueryResponse)
async def query_documents(query: QueryRequest, db: Session = Depends(get_db)):
    # Validate input
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="❌ Question is required")
    logger.debug(f"🔍 Received question: {query.question}")

    # Generate answer offloaded to a background thread
    try:
        result = await to_thread.run_sync(generate_answer, PERSIST_PATH, query.question)
        logger.debug(f"[query_documents] generate_answer result: {result}")

        answer = result.get("answer", "")
        citations = result.get("citations", [])
        themes = result.get("themes", [])
        doc_table = result.get("doc_table", [])
        synthesized_summary = result.get("synthesized_summary", "")
        logger.info("✅ LLM response generated successfully")
    except Exception as e:
        logger.error(f"❌ Answer generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error generating answer")

    # Save query log to database
    try:
        log_entry = QueryLog(
            timestamp=datetime.datetime.utcnow(),
            question=query.question,
            document_id=None,
            document_name="ALL",
            vector_path=PERSIST_PATH,
            answer=answer,
            citations=safe_json_dumps(citations),
            themes=safe_json_dumps(themes)
        )
        db.add(log_entry)
        db.commit()
        logger.debug("✅ Query logged in database")
    except Exception as e:
        logger.warning(f"⚠️ Failed to save query log: {e}", exc_info=True)

    # Return the full response
    return QueryResponse(
        answer=answer,
        citations=citations,
        themes=themes,
        tabular_results=doc_table,
        synthesized_summary=synthesized_summary
    )
