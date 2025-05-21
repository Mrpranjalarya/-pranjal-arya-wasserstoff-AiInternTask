import os
from typing import List, Dict, Optional
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document


def format_error_snippet(error: str, page: int = 0, para: int = 0) -> Dict:
    """Return a consistent error paragraph format."""
    return {
        "page_number": page,
        "paragraph_number": para,
        "text_snippet": error
    }


def extract_paragraphs_from_scanned_pdf(file_path: str, poppler_path: Optional[str] = None) -> List[Dict]:
    """Extract paragraphs from scanned PDF using OCR."""
    try:
        pages = convert_from_path(file_path, poppler_path=poppler_path) if poppler_path else convert_from_path(file_path)
    except Exception as e:
        return [format_error_snippet(f"PDF to image conversion failed: {e}")]

    paragraphs = []
    for i, page in enumerate(pages):
        try:
            text = pytesseract.image_to_string(page)
            para_list = [p.strip() for p in text.replace('\r', '').split('\n\n') if p.strip()]
            for j, para in enumerate(para_list):
                paragraphs.append({
                    "page_number": i + 1,
                    "paragraph_number": j + 1,
                    "text_snippet": para
                })
        except Exception as e:
            paragraphs.append(format_error_snippet(f"OCR failed on page {i+1}: {e}", page=i+1))
    return paragraphs


def extract_paragraphs_from_text_pdf(file_path: str) -> List[Dict]:
    """Extract paragraphs from text-based PDF using pdfminer."""
    try:
        text = extract_pdf_text(file_path)
        para_list = [p.strip() for p in text.split('\n\n') if p.strip()]
        return [{
            "page_number": 1,
            "paragraph_number": i + 1,
            "text_snippet": para
        } for i, para in enumerate(para_list)]
    except Exception as e:
        return [format_error_snippet(f"Text PDF extraction failed: {e}")]


def extract_paragraphs_from_docx(file_path: str) -> List[Dict]:
    """Extract paragraphs from DOCX file."""
    try:
        doc = Document(file_path)
        para_list = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return [{
            "page_number": 1,
            "paragraph_number": i + 1,
            "text_snippet": para
        } for i, para in enumerate(para_list)]
    except Exception as e:
        return [format_error_snippet(f"DOCX extraction failed: {e}")]


def extract_paragraphs_from_image(file_path: str) -> List[Dict]:
    """Extract paragraphs from image files using OCR."""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        para_list = [p.strip() for p in text.split('\n\n') if p.strip()]
        return [{
            "page_number": 1,
            "paragraph_number": i + 1,
            "text_snippet": para
        } for i, para in enumerate(para_list)]
    except Exception as e:
        return [format_error_snippet(f"OCR failed for image: {e}")]


def extract_paragraphs(file_path: str, poppler_path: Optional[str] = None) -> List[Dict]:
    """
    Unified interface to extract paragraphs from:
    - PDF (text or scanned)
    - DOCX
    - JPG/JPEG/PNG

    Adds 'page_number', 'paragraph_number', and 'text_snippet' to each entry.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            # Prefer text extraction
            text = extract_pdf_text(file_path)
            if text.strip():
                return extract_paragraphs_from_text_pdf(file_path)
            else:
                return extract_paragraphs_from_scanned_pdf(file_path, poppler_path)
        except Exception:
            return extract_paragraphs_from_scanned_pdf(file_path, poppler_path)

    elif ext == ".docx":
        return extract_paragraphs_from_docx(file_path)

    elif ext in [".jpg", ".jpeg", ".png"]:
        return extract_paragraphs_from_image(file_path)

    else:
        return [format_error_snippet(f"Unsupported file type: {ext}")]
