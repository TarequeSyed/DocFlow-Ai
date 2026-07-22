from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.parsing.parser import (
    IntelligentParserOrchestrator,
    NativeTextParser,
    OCRParser,
)


@pytest.mark.asyncio
async def test_native_text_parser_plain():
    """
    Tests NativeTextParser on a plain text content stream.
    """
    parser = NativeTextParser()
    content = b"Hello DocFlow AI! Plain Text Test Page."
    pages = await parser.parse_pages(content, "text/plain")
    assert len(pages) == 1
    assert pages[0] == "Hello DocFlow AI! Plain Text Test Page."


@pytest.mark.asyncio
@patch("fitz.open")
async def test_native_text_parser_pdf(mock_fitz_open):
    """
    Tests NativeTextParser on mock PDF file content.
    """
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Extracted PDF text layer."
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    parser = NativeTextParser()
    pages = await parser.parse_pages(b"%PDF-1.4 mock content", "application/pdf")
    assert len(pages) == 1
    assert pages[0] == "Extracted PDF text layer."
    mock_fitz_open.assert_called_once()


@pytest.mark.asyncio
@patch("fitz.open")
async def test_ocr_parser_pdf(mock_fitz_open):
    """
    Tests OCRParser on mock scanned PDF.
    """
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "OCR Scanned Text output."
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    parser = OCRParser()
    pages = await parser.parse_pages(b"%PDF-1.4 scanned", "application/pdf")
    assert len(pages) == 1
    assert pages[0] == "OCR Scanned Text output."
    mock_page.get_text.assert_called_with(option="text", ocr=True)


@pytest.mark.asyncio
async def test_orchestrator_image():
    """
    Tests IntelligentParserOrchestrator routes images straight to OCR.
    """
    orchestrator = IntelligentParserOrchestrator()
    orchestrator.ocr_parser = MagicMock()
    orchestrator.ocr_parser.parse_pages = AsyncMock(return_value=["Image text"])

    pages = await orchestrator.parse_document_pages(b"jpeg bytes", "image/jpeg")
    assert pages == ["Image text"]


@pytest.mark.asyncio
async def test_orchestrator_fallback():
    """
    Tests that IntelligentParserOrchestrator falls back to OCR
    if NativeParser yields empty strings.
    """
    orchestrator = IntelligentParserOrchestrator()
    orchestrator.native_parser = MagicMock()
    orchestrator.native_parser.parse_pages = AsyncMock(return_value=["", "  "])
    orchestrator.ocr_parser = MagicMock()
    orchestrator.ocr_parser.parse_pages = AsyncMock(
        return_value=["OCR page 1 text", "OCR page 2 text"]
    )

    pages = await orchestrator.parse_document_pages(
        b"scanned pdf bytes", "application/pdf"
    )
    assert pages == ["OCR page 1 text", "OCR page 2 text"]
