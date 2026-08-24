import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

class TransformerSummarizer:
    def __init__(self, model_name: str = "google/flan-t5-large"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    def summarize(self, text: str, custom_prompt: str = None, max_len: int = 180, min_len: int = 20) -> str:
        """Generates an abstractive summary of input text based on dynamic user settings."""
        if not text or len(text.strip()) < 50:
            return "Text too short to generate a meaningful summary."

        try:
            # If no user prompt is given, use a highly structured default bullet instruction
            if not custom_prompt or custom_prompt.strip() == "":
                prompt = (
                    f"Extract the main points from the following text and list them "
                    f"as clear bullet points starting with '* ':\n\n{text}"
                )
            else:
                # Inject the user's custom instruction cleanly
                prompt = f"{custom_prompt.strip()}\n\nText:\n{text}"

            inputs = self.tokenizer(
                prompt, return_tensors="pt", truncation=True, max_length=512
            )
            
            outputs = self.model.generate(
                **inputs,
                max_length=max_len,
                min_length=min_len,
                num_beams=4,
                no_repeat_ngram_size=3,
                repetition_penalty=2.0,
                early_stopping=True
            )
            
            summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return self._format_bullet_points(summary)
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return f"Error generating summary: {str(e)}"

    def _format_bullet_points(self, text: str) -> str:
        """Post-processes FLAN-T5 output into clean, vertical Markdown bullet points."""
        text = text.strip()
        # Common ways FLAN outputs unformatted bullets: "• point 1 • point 2" or "* point 1 * point 2"
        for delimiter in ["•", "*", "-", " - "]:
            if delimiter in text:
                parts = [p.strip() for p in text.split(delimiter) if p.strip()]
                return "\n".join(f"* {part}" for part in parts)
        
        # Fallback split if the model separated thoughts by raw periods instead of lists
        if len(text.split(". ")) > 1:
            parts = [p.strip() for p in text.split(". ") if p.strip()]
            return "\n".join(f"* {part.rstrip('.')}" for part in parts)
            
        return text
