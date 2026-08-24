import io
from core.extractor import DocumentExtractor
from core.summarizer import TransformerSummarizer

class DocumentOrchestrator:
    def __init__(self, extractor: DocumentExtractor, summarizer: TransformerSummarizer):
        self.extractor = extractor
        self.summarizer = summarizer

    def process_document(self, file_name: str, file_type: str, file_bytes: bytes, summary_settings: dict = None) -> dict:
        """Orchestrates text extraction and summarization based on file type and user settings."""
        buffer = io.BytesIO(file_bytes)
        result = {"name": file_name, "type": file_type, "pages": [], "summary": ""}
        
        # Unpack settings with fallbacks
        settings = summary_settings or {}
        custom_prompt = settings.get("prompt", None)
        max_len = settings.get("max_len", 180)
        min_len = settings.get("min_len", 20)

        if file_type == "application/pdf":
            pages = self.extractor.extract_from_pdf(buffer)
            result["pages"] = pages
            full_text = "\n".join(pages)
            result["summary"] = self.summarizer.summarize(full_text, custom_prompt, max_len, min_len)
            
        elif file_type.startswith("image/"):
            raw_text = self.extractor.extract_from_image(buffer)
            result["pages"] = [raw_text]
            result["summary"] = self.summarizer.summarize(raw_text, custom_prompt, max_len, min_len)
            
        elif file_type == "text/plain":
            try:
                raw_text = file_bytes.decode("utf-8", errors="ignore").strip()
                result["pages"] = [raw_text]
                result["summary"] = self.summarizer.summarize(raw_text, custom_prompt, max_len, min_len)
            except Exception as e:
                result["error"] = f"Failed to read text file: {e}"
                
        return result