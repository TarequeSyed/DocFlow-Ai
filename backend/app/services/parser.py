import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("docuflow-parser")


class BaseParser(ABC):
    """
    Abstract base class for all document parsing modules.
    Ensures interchangeable extraction strategies.
    """

    @abstractmethod
    async def parse(self, file_content: bytes, mime_type: str) -> str:
        """
        Parses document byte streams and returns plain text.
        """
        pass


class NativeTextParser(BaseParser):
    """
    Parser for documents containing digital text layers (e.g. native PDFs, text files).
    """

    async def parse(self, file_content: bytes, mime_type: str) -> str:
        logger.info("Executing Native Text Parsing...")
        if mime_type == "text/plain":
            return file_content.decode("utf-8", errors="ignore")

        try:
            import fitz  # PyMuPDF

            # Open document stream directly in memory
            doc = fitz.open(stream=file_content, filetype="pdf")
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return "\n".join(text_parts).strip()
        except Exception as e:
            logger.error(f"Native PyMuPDF extraction failed: {e}", exc_info=True)
            return ""


class OCRParser(BaseParser):
    """
    OCR extraction engine for image-only or scanned documents.
    """

    async def parse(self, file_content: bytes, mime_type: str) -> str:
        logger.info("Executing OCR text extraction...")
        # TODO [Phase 3]: Integrate pytesseract or EasyOCR layout detection
        return "OCR_TEXT_EXTRACTED_PLACEHOLDER"


class VisionLayoutParser(BaseParser):
    """
    Layout-aware vision parsing (bounding-boxes, tables, structures).
    """

    async def parse(self, file_content: bytes, mime_type: str) -> str:
        logger.info("Executing Vision/Layout analysis (placeholder)...")
        # TODO [Future Feature]: Integrate LayoutLM / Florence-2 visual models
        return "VISION_LAYOUT_EXTRACTED_PLACEHOLDER"


class IntelligentParserOrchestrator:
    """
    Coordinates parsers depending on mime types or text layer availability.
    """

    def __init__(self) -> None:
        self.native_parser = NativeTextParser()
        self.ocr_parser = OCRParser()
        self.vision_parser = VisionLayoutParser()

    async def parse_document(self, file_content: bytes, mime_type: str) -> str:
        """
        Inspects the file type and routes it to the optimal parser.
        """
        logger.info(f"Orchestrating parsing for file type: {mime_type}")

        if mime_type in ["image/png", "image/jpeg", "image/jpg"]:
            return await self.ocr_parser.parse(file_content, mime_type)

        extracted_text = await self.native_parser.parse(file_content, mime_type)

        # Fallback to OCR if Native parser returned nothing (e.g. Scanned PDF)
        if not extracted_text.strip():
            logger.warning(
                "Native parser returned empty text. Falling back to OCRParser..."
            )
            return await self.ocr_parser.parse(file_content, mime_type)

        return extracted_text
