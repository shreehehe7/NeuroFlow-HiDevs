import os
from PIL import Image
import pytesseract
from typing import List
from google import genai
from . import ExtractedPage

def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return image

def extract_image(file_path: str) -> List[ExtractedPage]:
    image = Image.open(file_path)
    # Ensure it's in a compatible mode for OCR and saving if needed
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    
    ocr_text = pytesseract.image_to_string(image).strip()
    
    resized_image = resize_image(image)
    
    # Vision LLM via Google GenAI (using gemini-1.5-flash)
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        prompt = "Describe this image in detail. Focus on the main subjects, layout, colors, and any charts or diagrams."
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[resized_image, prompt]
        )
        description = response.text
    except Exception as e:
        description = f"Failed to generate description via Vision LLM: {str(e)}"
        
    combined_content = description
    if ocr_text:
        combined_content += f"\n\nText found in image:\n{ocr_text}"
        
    return [ExtractedPage(
        page_number=1,
        content=combined_content,
        content_type="image_description",
        metadata={"ocr_text_length": len(ocr_text), "has_vision_description": True}
    )]
