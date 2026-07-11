import logging
import uuid

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.embeddings.factory import EmbeddingProviderFactory
from app.models.document import Document, DocumentChunk
from app.repositories.vector import VectorRepository
from app.services.chunker import IntelligentChunker
from app.services.classifier import IntelligentDocumentClassifier
from app.services.parser import IntelligentParserOrchestrator

logger = logging.getLogger("docuflow-processor")


class DocumentProcessor:
    """
    Background executor running text parsing, classification, chunking,
    embedding generation, and pgvector database indexing.
    """

    def __init__(self) -> None:
        self.parser_orchestrator = IntelligentParserOrchestrator()
        self.classifier = IntelligentDocumentClassifier()
        self.chunker = IntelligentChunker()
        self.vector_repository = VectorRepository()

    async def process_document(self, document_id: uuid.UUID) -> None:
        """
        Loads document record, parses storage bytes, runs category classification,
        creates overlapping text chunks, embeds chunks, and saves to vector store.
        """
        logger.info(f"Background task triggered for document ID: {document_id}")

        async with AsyncSessionLocal() as session:
            # 1. Retrieve the document record
            stmt = select(Document).where(Document.id == document_id)
            result = await session.execute(stmt)
            db_doc = result.scalar_one_or_none()

            if not db_doc:
                logger.error(f"Document ID {document_id} not found in database.")
                return

            # Update status to PARSING
            db_doc.status = "PARSING"
            await session.commit()

            try:
                # 2. Read stored file content
                logger.info(f"Reading file from local storage: {db_doc.file_path}")
                with open(db_doc.file_path, "rb") as f:
                    file_content = f.read()

                # 3. Parse Document Content
                extracted_text = await self.parser_orchestrator.parse_document(
                    file_content, db_doc.mime_type
                )

                # 4. Classify Document Type
                file_metadata = {
                    "filename": db_doc.filename,
                    "mime_type": db_doc.mime_type,
                    "size_bytes": db_doc.size_bytes,
                }
                category = await self.classifier.classify(extracted_text, file_metadata)

                # 5. Segment Text into Chunks
                logger.info("Splitting text layer into chunks...")
                chunk_metadata = {"document_id": str(document_id)}
                chunks_data = self.chunker.split_text(extracted_text, chunk_metadata)

                # 6. Generate Vector Embeddings (GPU/CPU Threadpool offloaded)
                if chunks_data:
                    logger.info(
                        f"Generating embeddings for {len(chunks_data)} chunks..."
                    )
                    provider = EmbeddingProviderFactory.get_provider()
                    texts = [c["content"] for c in chunks_data]
                    embeddings = await provider.embed_documents(texts)

                    # Build SQLAlchemy chunk model instances
                    db_chunks = []
                    for chunk, emb in zip(chunks_data, embeddings, strict=False):
                        db_chunks.append(
                            DocumentChunk(
                                document_id=document_id,
                                chunk_index=chunk["chunk_index"],
                                content=chunk["content"],
                                embedding=emb,
                            )
                        )

                    # Bulk insert chunks + vectors to PostgreSQL pgvector tables
                    logger.info("Bulk-saving vector chunks to database...")
                    await self.vector_repository.bulk_insert_chunks(session, db_chunks)

                # 7. Update parent document state
                db_doc.full_text = extracted_text
                db_doc.category = category
                db_doc.status = "PARSED"
                db_doc.error_message = None

                logger.info(
                    f"Document processing completed for {document_id}. "
                    f"Classified as: {category}. Indexed {len(chunks_data)} chunks."
                )

            except Exception as e:
                logger.error(
                    f"Document processing failed for {document_id}: {e}",
                    exc_info=True,
                )
                db_doc.status = "FAILED"
                db_doc.error_message = str(e)

            # Commit updates
            await session.commit()
