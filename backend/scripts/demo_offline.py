import asyncio
import uuid
from datetime import datetime, timezone
from app.services.extraction.reasoner import CrossDocReasoner
from app.services.timeline.timeline_service import TimelineService
from app.services.graph.graph_service import GraphService

DEMO_DOCS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "filename": "01_quotation_acme_software.txt",
        "category": "QUOTATION",
        "content": "ACME SOFTWARE CORP - QUOTATION\nDate: 2026-07-01\nSupplier: Acme Software Corp\nCustomer: Client Corp\nReference: QUOTE-8820\nTotal Proposed: $13,500.00"
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "filename": "02_purchase_order_client_corp.txt",
        "category": "PURCHASE_ORDER",
        "content": "CLIENT CORP - PURCHASE ORDER\nDate: 2026-07-03\nPurchase Order Ref: PO-8877\nSupplier: Acme Software Corp\nCustomer: Client Corp\nReferencing Quotation: QUOTE-8820\nTotal Value: $13,500.00"
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "filename": "03_delivery_note_setup.txt",
        "category": "DELIVERY_NOTE",
        "content": "ACME SOFTWARE CORP - DELIVERY & KICKOFF NOTE\nDate: 2026-07-08\nDelivery Note Ref: DN-0092\nAssociated PO: PO-8877\nSupplier: Acme Software Corp\nCustomer: Client Corp\nReceived and signed off by: Jane Smith, Project Manager."
    },
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "filename": "04_invoice_acme_9900.txt",
        "category": "INVOICE",
        "content": "ACME SOFTWARE CORP - BILLING INVOICE\nDate: 2026-07-11\nInvoice Number: INV-9900\nPurchase Order Ref: PO-8877\nSupplier: Acme Software Corp\nCustomer: Client Corp\nTotal Due: $13,500.00"
    },
    {
        "id": "55555555-5555-5555-5555-555555555555",
        "filename": "05_payment_receipt_9900.txt",
        "category": "PAYMENT_RECEIPT",
        "content": "CLIENT CORP - PAYMENT TRANSACTION RECEIPT\nDate: 2026-07-15\nReceipt Ref: REC-8801\nInvoice Reference: INV-9900\nSupplier: Acme Software Corp\nCustomer: Client Corp\nPayment Amount Received: $13,500.00"
    },
    {
        "id": "66666666-6666-6666-6666-666666666666",
        "filename": "06_warranty_certificate.txt",
        "category": "WARRANTY",
        "content": "ACME SOFTWARE CORP - WARRANTY & PREMIUM SUPPORT CERTIFICATE\nDate: 2026-07-16\nCertificate Ref: WAR-7711\nCustomer: Client Corp\nAssociated Purchase Order: PO-8877"
    }
]

async def run_offline_demo():
    print("=" * 70)
    print("            DOCUFLOW AI - OFFLINE PLATFORM DEMONSTRATION")
    print("=" * 70)
    await asyncio.sleep(0.5)

    print("\n[Step 1] Ingesting & OCR Processing Mock Workspace Dataset...")
    for doc in DEMO_DOCS:
        print(f" -> Processing '{doc['filename']}' ({doc['category']})")
        await asyncio.sleep(0.2)
    print("Ingestion Completed! Generated layout text segments and page bounds indices.")

    await asyncio.sleep(0.5)
    print("\n" + "="*50)
    print("[Step 2] Knowledge Graph Engine Network Representation")
    print("="*50)
    graph_service = GraphService()
    # Mocking CytoScape network format DTO
    mock_entities = [
        {"id": "e1", "name": "Acme Software Corp", "type": "SUPPLIER"},
        {"id": "e2", "name": "Client Corp", "type": "CUSTOMER"},
        {"id": "e3", "name": "QUOTE-8820", "type": "QUOTATION"},
        {"id": "e4", "name": "PO-8877", "type": "PURCHASE_ORDER"},
        {"id": "e5", "name": "INV-9900", "type": "INVOICE"},
        {"id": "e6", "name": "$13,500.00", "type": "AMOUNT"},
    ]
    mock_relationships = [
        {"source": "e4", "target": "e1", "relation": "ISSUED_TO"},
        {"source": "e4", "target": "e2", "relation": "ORDERED_BY"},
        {"source": "e4", "target": "e3", "relation": "REFERENCES"},
        {"source": "e5", "target": "e4", "relation": "BILLS_ORDER"},
        {"source": "e5", "target": "e6", "relation": "HAS_TOTAL"},
    ]
    print("\nCytoscape Node Matrix:")
    for entity in mock_entities:
        print(f"  Node [{entity['id']}]: {entity['name']} (Class: {entity['type']})")
    print("\nCytoscape Relationship Map:")
    for rel in mock_relationships:
        print(f"  Edge: {rel['source']} --({rel['relation']})--> {rel['target']}")

    await asyncio.sleep(0.5)
    print("\n" + "="*50)
    print("[Step 3] Chronological Timeline Intelligence Engine")
    print("="*50)
    timeline_events = [
        {"date": "2026-07-01", "event": "Quotation QUOTE-8820 Issued", "doc": "01_quotation_acme_software.txt"},
        {"date": "2026-07-03", "event": "Purchase Order PO-8877 Authorized", "doc": "02_purchase_order_client_corp.txt"},
        {"date": "2026-07-08", "event": "Services DN-0092 Delivered & Kickoff note signed", "doc": "03_delivery_note_setup.txt"},
        {"date": "2026-07-11", "event": "Invoice INV-9900 Billed", "doc": "04_invoice_acme_9900.txt"},
        {"date": "2026-07-15", "event": "Payment REC-8801 Receipt Completed", "doc": "05_payment_receipt_9900.txt"},
        {"date": "2026-07-16", "event": "Warranty WAR-7711 Certificate active", "doc": "06_warranty_certificate.txt"},
    ]
    print("\nSequential progression:")
    for idx, item in enumerate(timeline_events, 1):
        print(f"  {idx}. [{item['date']}] {item['event']} (Source: {item['doc']})")
    
    print("\nAnalyzing missing link events...")
    # Triggering missing link analyzer
    missing_links = ["CONTRACT"]
    for alert in missing_links:
        print(f"  [TIMELINE WARNING]: Missing process step detected! No '{alert}' found for the procurement chain PO-8877.")

    await asyncio.sleep(0.5)
    print("\n" + "="*50)
    print("[Step 4] Cross-Document 3-Way Reconciliation Auditing")
    print("="*50)
    # Mocking values checks
    reconciliation_audit = {
        "invoice_id": "INV-9900",
        "purchase_order_id": "PO-8877",
        "matches": [
            {"field": "total_amount", "invoice_value": "$13,500.00", "po_value": "$13,500.00", "status": "MATCHED"},
            {"field": "supplier", "invoice_value": "Acme Software Corp", "po_value": "Acme Software Corp", "status": "MATCHED"}
        ],
        "mismatches": [],
        "delivery_status": "DELIVERED",
        "reconciliation_status": "COMPLIANT"
    }
    print(f"\nComparing Invoice {reconciliation_audit['invoice_id']} <-> PO {reconciliation_audit['purchase_order_id']}:")
    for check in reconciliation_audit["matches"]:
        print(f"  [OK] {check['field']}: Invoice Value ({check['invoice_value']}) matches PO Value ({check['po_value']})")
    
    print(f"  [OK] Delivery signoff status: {reconciliation_audit['delivery_status']}")
    print(f"  Reconciliation Audit Decision: {reconciliation_audit['reconciliation_status']}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_offline_demo())
