# 3. backend/app/core/image.py
import os
from PIL import Image
import pytesseract

def extract_text_from_image(file_path: str) -> str:
    """
    OCR extract text from image (jpg, png, etc.).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    return text.strip()
