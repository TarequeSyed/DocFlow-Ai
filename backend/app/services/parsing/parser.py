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

    async def parse_pages(self, file_content: bytes, mime_type: str) -> list[str]:
        """
        Parses document byte streams page-by-page and returns list of texts.
        """
        text = await self.parse(file_content, mime_type)
        return [text] if text.strip() else []


class NativeTextParser(BaseParser):
    """
    Parser for documents containing digital text layers (e.g. native PDFs, text files).
    """

    async def parse(self, file_content: bytes, mime_type: str) -> str:
        pages = await self.parse_pages(file_content, mime_type)
        return "\n".join(pages).strip()

    async def parse_pages(self, file_content: bytes, mime_type: str) -> list[str]:
        logger.info("Executing Native Text Parsing (pages)...")
        if mime_type == "text/plain":
            return [file_content.decode("utf-8", errors="ignore")]

        try:
            import fitz  # PyMuPDF

            # Open document stream directly in memory
            doc = fitz.open(stream=file_content, filetype="pdf")
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return text_parts
        except Exception as e:
            logger.error(f"Native PyMuPDF extraction failed: {e}", exc_info=True)
            return []


class OCRParser(BaseParser):
    """
    OCR extraction engine for image-only or scanned documents.
    """

    async def parse(self, file_content: bytes, mime_type: str) -> str:
        pages = await self.parse_pages(file_content, mime_type)
        return "\n".join(pages).strip()

    async def parse_pages(self, file_content: bytes, mime_type: str) -> list[str]:
        logger.info("Executing OCR text extraction...")
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(stream=file_content, filetype=mime_type.split("/")[-1])
            pages = []
            for page in doc:
                try:
                    # Run PyMuPDF native page OCR via Tesseract
                    page_text = page.get_text(option="text", ocr=True)
                    pages.append(page_text)
                except Exception as page_err:
                    logger.warning(f"OCR failed for a page: {page_err}")
                    pages.append("")
            doc.close()
            return pages
        except Exception as e:
            logger.error(f"OCRParser execution failed: {e}", exc_info=True)
            return []


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
        pages = await self.parse_document_pages(file_content, mime_type)
        return "\n".join(pages).strip()

    async def parse_document_pages(
        self, file_content: bytes, mime_type: str
    ) -> list[str]:
        """
        Inspects the file type, routes it to the optimal parser,
        and returns list of page texts.
        """
        logger.info(f"Orchestrating parsing for file type: {mime_type}")

        if mime_type in ["image/png", "image/jpeg", "image/jpg"]:
            return await self.ocr_parser.parse_pages(file_content, mime_type)

        pages = await self.native_parser.parse_pages(file_content, mime_type)

        # Fallback to OCR if Native parser returned nothing (e.g. Scanned PDF)
        if not any(p.strip() for p in pages):
            logger.warning(
                "Native parser returned empty text pages. Falling back to OCRParser..."
            )
            return await self.ocr_parser.parse_pages(file_content, mime_type)

        return pages
