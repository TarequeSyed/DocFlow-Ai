import logging
import uuid

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.services.classifier import IntelligentDocumentClassifier
from app.services.parser import IntelligentParserOrchestrator

logger = logging.getLogger("docuflow-processor")


class DocumentProcessor:
    """
    Orchestrates the asynchronous background parsing and classification pipeline.
    """

    def __init__(self) -> None:
        self.parser_orchestrator = IntelligentParserOrchestrator()
        self.classifier = IntelligentDocumentClassifier()

    async def process_document(self, document_id: uuid.UUID) -> None:
        """
        Loads document by ID from database, parses the stored file,
        runs type classification, and commits results.
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

                # 5. Save results and update status
                db_doc.full_text = extracted_text
                db_doc.category = category
                db_doc.status = "PARSED"
                db_doc.error_message = None

                logger.info(
                    f"Document processing completed for {document_id}. "
                    f"Classified as: {category}."
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
