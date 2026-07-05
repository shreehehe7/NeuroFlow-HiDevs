import pypdfium2 as pdfium
import pytesseract
import pdfplumber
from PIL import Image
from typing import List
from . import ExtractedPage

def extract_pdf(file_path: str) -> List[ExtractedPage]:
    pages: List[ExtractedPage] = []
    
    # First pass: Text and OCR using pypdfium2
    pdf = pdfium.PdfDocument(file_path)
    for i in range(len(pdf)):
        page = pdf[i]
        page_number = i + 1
        textpage = page.get_textpage()
        text = textpage.get_text_bounded()
        
        # Check if scanned (less than 50 characters)
        if len(text.strip()) < 50:
            # Rasterize and OCR
            bitmap = page.render(scale=2)  # Higher scale for better OCR
            pil_image = bitmap.to_pil()
            ocr_text = pytesseract.image_to_string(pil_image, config='--psm 6')
            if ocr_text.strip():
                pages.append(ExtractedPage(
                    page_number=page_number,
                    content=ocr_text.strip(),
                    content_type="text",
                    metadata={"source": "ocr"}
                ))
        else:
            if text.strip():
                pages.append(ExtractedPage(
                    page_number=page_number,
                    content=text.strip(),
                    content_type="text",
                    metadata={"source": "digital"}
                ))
    
    # Second pass: Table extraction using pdfplumber
    with pdfplumber.open(file_path) as plumber_pdf:
        for i, page in enumerate(plumber_pdf.pages):
            page_number = i + 1
            tables = page.extract_tables()
            for table in tables:
                # Convert table to markdown
                markdown_table = []
                for row_idx, row in enumerate(table):
                    cleaned_row = [str(cell).replace('\n', ' ') if cell is not None else "" for cell in row]
                    markdown_table.append("| " + " | ".join(cleaned_row) + " |")
                    # Add separator after header
                    if row_idx == 0:
                        markdown_table.append("|" + "|".join(["---"] * len(cleaned_row)) + "|")
                
                if markdown_table:
                    pages.append(ExtractedPage(
                        page_number=page_number,
                        content="\n".join(markdown_table),
                        content_type="table",
                        metadata={"source": "pdfplumber"}
                    ))
                    
    # Sort pages by page_number
    pages.sort(key=lambda x: (x.page_number, 1 if x.content_type == "table" else 0))
    return pages
