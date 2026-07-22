import asyncio
import hashlib
import os
import sys

# Add backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.services.workspace.processor import DocumentProcessor

DEMO_DOCUMENTS = [
    {
        "filename": "01_quotation_acme_software.txt",
        "category": "QUOTATION",
        "content": """ACME SOFTWARE CORP - QUOTATION
Date: 2026-07-01
Supplier: Acme Software Corp
Customer: Client Corp
Reference: QUOTE-8820

Services Offered:
1. Document Intelligence Platform Core: $10,000.00
2. Custom Pipeline Configuration: $2,000.00
3. Training and Support: $1,500.00

Total Proposed: $13,500.00

Accepted by Client Corp Representative.""",
    },
    {
        "filename": "02_purchase_order_client_corp.txt",
        "category": "PURCHASE_ORDER",
        "content": """CLIENT CORP - PURCHASE ORDER
Date: 2026-07-03
Purchase Order Ref: PO-8877
Supplier: Acme Software Corp
Customer: Client Corp
Referencing Quotation: QUOTE-8820

Items ordered:
- DocFlow AI Enterprise License: $10,000.00
- Custom Pipeline Setup: $2,000.00
- 1-Year Premium Support: $1,500.00

Total Value: $13,500.00

Authorized Signature: John Doe, Director of Procurement.""",
    },
    {
        "filename": "03_delivery_note_setup.txt",
        "category": "DELIVERY_NOTE",
        "content": """ACME SOFTWARE CORP - DELIVERY & KICKOFF NOTE
Date: 2026-07-08
Delivery Note Ref: DN-0092
Associated PO: PO-8877
Supplier: Acme Software Corp
Customer: Client Corp

Services delivered and configured:
- AI Core Engine deployed in staging.
- Custom schemas configured: INVOICE, CONTRACT, DELIVERY.
- Training documentation delivered.

Received and signed off by: Jane Smith, Project Manager.""",
    },
    {
        "filename": "04_invoice_acme_9900.txt",
        "category": "INVOICE",
        "content": """ACME SOFTWARE CORP - BILLING INVOICE
Date: 2026-07-11
Invoice Number: INV-9900
Purchase Order Ref: PO-8877
Supplier: Acme Software Corp
Customer: Client Corp

Due Date: 2026-08-10

Billed items:
- Software core license: $10,000.00
- Extraction pipeline delivery: $2,000.00
- Staging support package: $1,500.00

Total Due: $13,500.00

Please transfer payments to Acme Bank, Account: 9988776655.""",
    },
    {
        "filename": "05_payment_receipt_9900.txt",
        "category": "PAYMENT_RECEIPT",
        "content": """CLIENT CORP - PAYMENT TRANSACTION RECEIPT
Date: 2026-07-15
Receipt Ref: REC-8801
Invoice Reference: INV-9900
Supplier: Acme Software Corp
Customer: Client Corp

Payment Amount Received: $13,500.00
Status: Complete
Transaction Hash: TXN_ACME_CLIENT_99882233

Thank you for your business!""",
    },
    {
        "filename": "06_warranty_certificate.txt",
        "category": "WARRANTY",
        "content": """ACME SOFTWARE CORP - WARRANTY & PREMIUM SUPPORT CERTIFICATE
Date: 2026-07-16
Certificate Ref: WAR-7711
Customer: Client Corp
Associated Purchase Order: PO-8877

Coverage details:
- 1-Year software defects warranty starting 2026-07-16.
- 24/7 SLA tier support for document ingestion pipeline problems.

Acme Support Team Contact: support@acmesoftware.com""",
    },
]


async def seed_demo() -> None:
    print("Starting Demo Workspace Seeding...")
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    processor = DocumentProcessor()

    async with AsyncSessionLocal() as session:
        for doc_info in DEMO_DOCUMENTS:
            content_bytes = doc_info["content"].encode("utf-8")
            file_hash = hashlib.sha256(content_bytes).hexdigest()

            # Save file to disk
            file_path = os.path.join(upload_dir, f"{file_hash}.txt")
            with open(file_path, "wb") as f:
                f.write(content_bytes)

            # Create PENDING document DB record
            db_doc = Document(
                filename=doc_info["filename"],
                file_path=file_path,
                file_hash=file_hash,
                mime_type="text/plain",
                size_bytes=len(content_bytes),
                status="PENDING",
                category="UNKNOWN",
            )
            session.add(db_doc)
            await session.commit()
            await session.refresh(db_doc)

            print(
                f"Ingested {doc_info['filename']} "
                f"as PENDING (ID: {db_doc.id}). Processing..."
            )

            # Execute processing synchronously for seeding
            try:
                await processor.process_document(db_doc.id)
                print(f"Successfully processed {doc_info['filename']}!")
            except Exception as e:
                print(f"Failed processing {doc_info['filename']}: {e}")

    print("Demo Workspace Seeding Complete!")


if __name__ == "__main__":
    asyncio.run(seed_demo())
