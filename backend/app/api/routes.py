from fastapi import APIRouter, UploadFile, File
from typing import List
from app.services.document_service import process_uploaded_document

router = APIRouter()

@router.post("/upload", summary="Upload PDFs or images")
async def upload_documents(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            doc = process_uploaded_document(file)
            results.append({
                "filename": doc["filename"],
                "preview": doc["extracted_text"][:300]
            })
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
    return {"documents": results}
