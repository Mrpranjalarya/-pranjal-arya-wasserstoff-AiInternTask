# 1. backend/app/core/word.py
import os
from docx import Document as DocxDocument

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a .docx file, tagging paragraphs.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    doc = DocxDocument(file_path)
    output = ""
    for i, para in enumerate(doc.paragraphs, start=1):
        text = para.text.strip()
        if text:
            output += f"\n--- Para {i} ---\n{text}\n"
    return output.strip()