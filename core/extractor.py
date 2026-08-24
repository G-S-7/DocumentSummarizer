import io
import pdfplumber
import pytesseract
from PIL import Image
import pytesseract
from config import TESSERACT_CMD
class DocumentExtractor:
    def __init__(self, tesseract_cmd: str = TESSERACT_CMD):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_from_pdf(self, file_bytes: io.BytesIO) -> list[str]:
        """Extracts text page-by-page from a machine-native PDF."""
        pages_text = []
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages:
                text = page.extract_text(layout=True)
                pages_text.append(text.strip() if text else "")
        return pages_text

    def extract_from_image(self, file_bytes: io.BytesIO) -> str:
        """Runs OCR on an image file."""
        img = Image.open(file_bytes)
        ocr_text = pytesseract.image_to_string(img)
        return ocr_text.strip() if ocr_text else ""
    
    @staticmethod
    def extract_from_txt(file_bytes) -> str:
        """Reads and decodes plain text files into strings directly."""
        try:
            # Read bytes payload and decode using standard web-safe UTF-8 configuration
            return file_bytes.read().decode("utf-8")
        except UnicodeDecodeError:
            # Fallback handling for alternative legacy Windows document encoding structures
            file_bytes.seek(0)
            return file_bytes.read().decode("latin-1")