import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger("docuflow-chunker")


class BaseChunker(ABC):
    """
    Abstract interface for spliting extracted raw text into search-optimized segments.
    """

    @abstractmethod
    def split_text(self, text: str, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Splits raw text into a list of chunk dicts containing 'content' and 'metadata'.
        """
        pass


class IntelligentChunker(BaseChunker):
    """
    Modular chunker supporting semantic character splitters and layout/table boundaries.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Splits document text into manageable pieces, propagating metadata.
        """
        logger.info("Executing text chunking pipeline...")
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        split_docs = splitter.split_text(text)

        chunks = []
        for i, content in enumerate(split_docs):
            chunks.append(
                {
                    "content": content,
                    "chunk_index": i,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "character_length": len(content),
                    },
                }
            )

        logger.info(f"Chunking completed. Generated {len(chunks)} chunks.")
        return chunks
