import logging
from pathlib import Path
from PIL import Image

logger = logging.getLogger(__name__)

def ocr_image(image_path: str) -> str:
    """
    Attempts OCR using pytesseract (primary) or easyocr (fallback).
    If OCR libraries or binaries are not installed, returns an empty string or fallback note.
    """
    # 1. Try pytesseract
    try:
        import pytesseract
        text = pytesseract.image_to_string(Image.open(image_path))
        if text.strip():
            return text
    except Exception as e:
        logger.debug(f"pytesseract extraction failed or unavailable: {e}")

    # 2. Try easyocr fallback
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(image_path)
        extracted = " ".join([res[1] for res in results])
        if extracted.strip():
            return extracted
    except Exception as e:
        logger.debug(f"easyocr extraction failed or unavailable: {e}")

    logger.warning("No OCR tool available or image could not be read.")
    return ""
