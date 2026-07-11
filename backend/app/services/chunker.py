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
        chunks = []

        # Fallback simple split implementation (mock splitter for skeleton verification)
        words = text.split()
        current_chunk_words = []
        current_length = 0
        chunk_index = 0

        for word in words:
            current_chunk_words.append(word)
            current_length += len(word) + 1
            if current_length >= self.chunk_size:
                content = " ".join(current_chunk_words)
                chunks.append(
                    {
                        "content": content,
                        "chunk_index": chunk_index,
                        "metadata": {
                            **metadata,
                            "chunk_index": chunk_index,
                            "character_length": len(content),
                        },
                    }
                )
                chunk_index += 1
                current_chunk_words = current_chunk_words[-5:]  # basic mock overlap
                current_length = sum(len(w) + 1 for w in current_chunk_words)

        if current_chunk_words:
            content = " ".join(current_chunk_words)
            chunks.append(
                {
                    "content": content,
                    "chunk_index": chunk_index,
                    "metadata": {
                        **metadata,
                        "chunk_index": chunk_index,
                        "character_length": len(content),
                    },
                }
            )

        # TODO [Phase 4]: Replace with LangChain text splitter
        # TODO [Future Feature]: Integrate semantic split
        # TODO [Future Feature]: Integrate layout/table-aware split

        logger.info(f"Chunking completed. Generated {len(chunks)} chunks.")
        return chunks
