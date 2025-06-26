import os
import uuid
from fastapi import UploadFile
from app.core.ocr import extract_text_from_pdf

UPLOAD_DIR = "backend/data"

def save_file(upload_file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = upload_file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return file_path

def process_uploaded_document(file: UploadFile) -> dict:
    file_path = save_file(file)
    extracted_text = extract_text_from_pdf(file_path)
    return {
        "filename": file.filename,
        "file_path": file_path,
        "extracted_text": extracted_text.strip()
    }
