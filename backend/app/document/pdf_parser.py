import pymupdf
from pathlib import Path
from typing import Dict, Any, List
from backend.app.document.ocr import ocr_image
from backend.app.document.table_extractor import extract_tables_from_text

class PDFParser:
    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parses digital PDF or images.
        If native digital text has >= 50 characters, uses PyMuPDF directly.
        Extracts structural tables via find_tables() or text fallbacks.
        If digital text is unusable (< 50 characters or scanned), routes to OCR.
        Preserves page numbers, extracted tables, and headings.
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext in [".png", ".jpg", ".jpeg"]:
            text = ocr_image(str(path))
            return {
                "file_path": str(path),
                "is_ocr": True,
                "pages": [{"page_number": 1, "text": text}],
                "raw_text": text,
                "tables": extract_tables_from_text(text)
            }

        # PDF extraction via PyMuPDF
        doc = pymupdf.open(str(path))
        pages_data: List[Dict[str, Any]] = []
        full_text_list: List[str] = []
        total_native_chars = 0
        extracted_tables: List[Dict[str, Any]] = []

        for page_idx, page in enumerate(doc):
            page_text = page.get_text("text")
            total_native_chars += len(page_text.strip())
            pages_data.append({
                "page_number": page_idx + 1,
                "text": page_text
            })
            full_text_list.append(page_text)

            # Try PyMuPDF structured table extraction
            try:
                finder = page.find_tables()
                if hasattr(finder, "tables"):
                    for t in finder.tables:
                        extracted_tables.append({"rows": t.extract()})
            except Exception:
                pass

        doc.close()

        # Gate OCR check: Don't OCR every file — only when native text extraction is unusable
        if total_native_chars < 50:
            doc = pymupdf.open(str(path))
            ocr_full_text = []
            ocr_pages = []
            for page_idx, page in enumerate(doc):
                pix = page.get_pixmap(dpi=150)
                temp_img_path = path.parent / f"{path.stem}_page_{page_idx+1}.png"
                pix.save(str(temp_img_path))
                page_ocr_text = ocr_image(str(temp_img_path))
                ocr_full_text.append(page_ocr_text)
                ocr_pages.append({
                    "page_number": page_idx + 1,
                    "text": page_ocr_text
                })
                if temp_img_path.exists():
                    temp_img_path.unlink()
            doc.close()
            combined_ocr = "\n\n".join(ocr_full_text)
            return {
                "file_path": str(path),
                "is_ocr": True,
                "pages": ocr_pages,
                "raw_text": combined_ocr,
                "tables": extract_tables_from_text(combined_ocr)
            }

        combined_text = "\n\n".join(full_text_list)
        if not extracted_tables:
            extracted_tables = extract_tables_from_text(combined_text)

        return {
            "file_path": str(path),
            "is_ocr": False,
            "pages": pages_data,
            "raw_text": combined_text,
            "tables": extracted_tables
        }

pdf_parser = PDFParser()
