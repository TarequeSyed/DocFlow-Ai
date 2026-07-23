# 🏗️ System Architecture – DocuFlow AI

> Version: 2.0
>
> This document serves as the single source of truth for the architectural design of **DocuFlow AI**. It describes how every component interacts, the responsibilities of each module, the data flow throughout the system, and the engineering principles that govern future development.
>
> This document is intended for developers, contributors, technical reviewers, and AI engineering interviewers.

---

# 1. Vision

DocuFlow AI is an enterprise-grade AI Document Intelligence Platform designed to transform unstructured documents into structured, explainable, searchable, and interconnected knowledge.

Rather than functioning as a simple Retrieval-Augmented Generation (RAG) application, DocuFlow AI aims to become a modular AI platform capable of:

- Intelligent document ingestion
- Schema-based information extraction
- Cross-document reasoning
- Explainable AI
- Knowledge graph generation
- Timeline reconstruction
- Layout-aware understanding
- Multi-document intelligence

The architecture emphasizes maintainability, modularity, explainability, and production readiness.

---

# 2. Architectural Philosophy

Every architectural decision should satisfy the following principles:

- Modular over Monolithic
- Composition over Inheritance
- Explicit over Implicit
- Simplicity over Cleverness
- Explainability over Black-box Behaviour
- Evolutionary Design over Large Rewrites

Every new module should integrate naturally into the existing architecture without requiring extensive modifications to existing code.

The platform should continuously evolve while maintaining backward compatibility whenever possible.

---

# 3. High-Level Architecture

```
                            Client
                               │
                               ▼
                    Next.js Frontend (UI)
                               │
                               ▼
                     FastAPI Application
                               │
 ┌─────────────────────────────┼─────────────────────────────┐
 │                             │                             │
 ▼                             ▼                             ▼

Document Workspace      Intelligence Engine         Explainability Engine

 │                             │                             │
 │                             │                             │
 ▼                             ▼                             ▼

CRUD                Retrieval Pipeline          Citation Generator
Metadata            Extraction Engine           Confidence Scorer
Collections         Knowledge Graph             Evidence Builder
Status              Timeline Builder            Metadata Resolver

 └─────────────────────────────┼─────────────────────────────┘
                               │
                               ▼
                   PostgreSQL + pgvector
```

---

# 4. Layered Architecture

```
+-------------------------------------------------------------+
|                    Presentation Layer                       |
|               Next.js + TailwindCSS + React                 |
+-------------------------------------------------------------+
                            │
                            ▼
+-------------------------------------------------------------+
|                        API Layer                            |
|               FastAPI Routers / Dependencies                |
+-------------------------------------------------------------+
                            │
                            ▼
+-------------------------------------------------------------+
|                    Application Layer                        |
|   Workspace │ Parsing │ Retrieval │ Extraction │ Graph      |
+-------------------------------------------------------------+
                            │
                            ▼
+-------------------------------------------------------------+
|                     Repository Layer                        |
|      SQLAlchemy Repositories / Database Interfaces          |
+-------------------------------------------------------------+
                            │
                            ▼
+-------------------------------------------------------------+
|                     Infrastructure Layer                    |
| PostgreSQL │ pgvector │ OCR │ Embedding Providers │ Docker  |
+-------------------------------------------------------------+
```

Dependencies always point downward.

Business logic must never depend directly on infrastructure implementations.

---

# 5. Major System Modules

The platform is divided into independent modules.

Each module owns exactly one responsibility.

```
DocuFlow AI

├── Document Workspace
├── Parsing Engine
├── Layout Intelligence Engine
├── Retrieval Engine
├── Extraction Engine
├── Explainability Engine
├── Knowledge Graph Engine
├── Timeline Engine
├── Embedding Engine
├── Repository Layer
└── Infrastructure
```

Each module should remain independently testable and replaceable.

---

# 6. Document Workspace

The Document Workspace serves as the primary interaction point for uploaded documents.

Unlike traditional upload-only workflows, documents become persistent workspace assets.

Responsibilities include:

- Upload documents
- Delete documents
- View document metadata
- Search uploaded documents
- Track processing status
- View extraction status
- View document relationships
- Launch AI operations

Future extensions:

- Document collections
- Version history
- Bulk operations
- Folder organization
- User ownership
- Collaboration

The workspace should behave similarly to modern cloud storage systems while remaining tightly integrated with AI capabilities.

---

# 7. Core Data Flow

Every uploaded document follows a standardized lifecycle.

```
Upload

↓

Metadata Registration

↓

Document Parsing

↓

Layout Analysis

↓

Chunk Generation

↓

Embedding Generation

↓

Vector Storage

↓

Extraction

↓

Knowledge Graph Update

↓

Timeline Update

↓

Ready for Query
```

Every stage should remain independently replaceable.

---

# 8. Document Processing Pipeline

```
Client Upload

↓

Workspace Service

↓

Parser Orchestrator

↓

Native Parser
OCR Parser
Layout Parser

↓

Document Classifier

↓

Chunk Generator

↓

Embedding Provider

↓

Vector Database

↓

Extraction Engine

↓

Knowledge Graph

↓

Timeline Builder

↓

Ready
```

Each stage performs exactly one responsibility.

---

# 9. Document Workspace Architecture

```
Document Workspace

├── Upload Service
├── Delete Service
├── Metadata Service
├── Search Service
├── Status Service
├── Processing Queue
└── Workspace API
```

The Workspace is responsible only for document lifecycle management.

It must never contain extraction logic.

---

# 10. Parsing Engine

The Parsing Engine converts uploaded files into machine-readable content.

Supported parsers include:

- Native PDF Parser
- OCR Parser
- Image Parser
- Office Document Parser (Future)

Responsibilities:

- Detect file type
- Extract raw text
- Preserve page structure
- Preserve reading order
- Preserve metadata
- Forward structured output downstream

The Parsing Engine should never perform AI reasoning.

---

# 11. Layout Intelligence Engine

This replaces the traditional "Visual RAG" concept.

Layout Intelligence is responsible for understanding visual structure rather than merely retrieving text.

Responsibilities include:

- Table Detection
- Reading Order Reconstruction
- Bounding Box Extraction
- Layout Preservation
- Region Detection
- Header/Footer Identification
- Multi-column Analysis
- Form Understanding

Future capabilities:

- Signature Detection
- Stamp Detection
- Diagram Parsing
- Handwritten Notes

The output of this engine enriches downstream retrieval and extraction.

---

# 12. Retrieval Engine

The Retrieval Engine determines which information should be sent to the LLM.

Supported retrieval strategies include:

- Semantic Search
- Metadata Search
- Hybrid Search
- Layout-aware Retrieval
- Table-aware Retrieval
- Knowledge Graph Retrieval
- Timeline-aware Retrieval

The engine should automatically select the most appropriate retrieval strategy.

Future strategies may be added without modifying downstream business logic.

---

# 13. Extraction Engine

The Extraction Engine converts retrieved context into validated structured information.

Responsibilities:

- Prompt construction
- Schema injection
- LLM interaction
- Validation
- Retry mechanisms
- JSON enforcement
- Business rule validation

Extraction should always remain deterministic after validation.

---

# 14. Explainability Engine

Every AI answer should be explainable.

The Explainability Engine is responsible for generating transparent evidence.

Modules include:

```
Explainability Engine

├── Citation Generator
├── Confidence Scorer
├── Evidence Extractor
├── Metadata Resolver
└── Reasoning Trace Builder
```

Every extracted field should ideally contain:

- Source document
- Page number
- Chunk reference
- Confidence score
- Supporting evidence
- Retrieval strategy

This module exists independently from the LLM to ensure explainability remains consistent regardless of model provider.

---

# 15. Knowledge Graph Engine

The Knowledge Graph Engine transforms isolated document information into interconnected knowledge.

It should not simply visualize documents.

Instead, it should construct semantic relationships between entities.

Example entities include:

- Supplier
- Customer
- Invoice
- Purchase Order
- Contract
- Material
- Employee
- Project
- Payment
- Certificate

Responsibilities include:

- Entity Detection
- Entity Linking
- Relationship Discovery
- Graph Construction
- Graph Updates
- Graph Queries
- Graph Visualization DTO generation

The implementation technology is intentionally abstract.

Antigravity is encouraged to choose the implementation that best balances:

- Maintainability
- Scalability
- Visualization quality
- Performance
- Simplicity

Possible implementations include:

- JSON Graph
- NetworkX
- Cytoscape
- Force Graph
- Neo4j (Future)

The chosen implementation should remain replaceable without affecting business logic.

# 16. Timeline Intelligence Engine

The Timeline Intelligence Engine reconstructs the chronological flow of related documents.

Rather than simply sorting documents by upload time, this engine infers relationships using multiple reasoning strategies.

The objective is to reconstruct the lifecycle of a business process.

Example:

```
Quotation
    ↓
Purchase Order
    ↓
Invoice
    ↓
Partial Payment
    ↓
Delivery Note
    ↓
Final Payment
    ↓
Warranty Certificate
```

This allows users to understand the progression of work without manually organizing documents.

## Responsibilities

- Timeline Reconstruction
- Relationship Ordering
- Event Extraction
- Date Normalization
- Missing Link Detection
- Chronological Visualization DTO generation

## Timeline Strategies

The Timeline Engine should evaluate multiple ordering strategies.

```
Timeline Builder

├── Explicit Date Matching
├── Metadata Ordering
├── Entity Relationship Ordering
├── Semantic Similarity Ordering
└── AI-based Timeline Inference
```

The engine should automatically select the highest-confidence ordering strategy.

Future implementations may combine multiple strategies into hybrid ordering.

---

# 17. Cross-Document Intelligence Engine

Traditional document systems treat each document independently.

DocuFlow AI instead performs reasoning across multiple documents.

Responsibilities include:

- Multi-document Retrieval
- Cross-document Validation
- Entity Resolution
- Duplicate Detection
- Information Reconciliation
- Business Rule Verification

Examples include:

Invoice ↔ Purchase Order

Contract ↔ Invoice

Quotation ↔ Payment

Delivery Note ↔ Invoice

Invoice ↔ Bank Receipt

Future extensions:

- Compliance Verification
- Procurement Auditing
- Financial Reconciliation
- Multi-document Question Answering

---

# 18. Knowledge Graph + Timeline Integration

The Knowledge Graph and Timeline Engine should operate together rather than independently.

Knowledge Graph

```
Supplier

↓

Invoice

↓

Payment
```

Timeline

```
Quotation

↓

Purchase Order

↓

Invoice

↓

Payment
```

Combined View

```
Supplier A

│

├── Quotation

│

├── Purchase Order

│

├── Invoice

│

└── Payment
```

The frontend may visualize these relationships using either 2D or 3D graph layouts.

The implementation technology remains flexible.

---

# 19. Demo Workspace

The repository should include a complete demonstration workspace.

Its purpose is to allow reviewers and interviewers to experience the full platform without uploading their own documents.

The Demo Workspace should include:

- Realistic procurement documents
- Contracts
- Quotations
- Purchase Orders
- Invoices
- Payment Receipts
- Delivery Notes

The documents should intentionally reference one another.

Example:

Quotation A

↓

Purchase Order A

↓

Invoice A

↓

Partial Payment

↓

Final Payment

↓

Warranty

The platform should automatically:

- extract structured information
- build the knowledge graph
- reconstruct the timeline
- answer questions
- generate explainable citations

This allows every major feature to be demonstrated immediately.

---

# 20. Explainable Retrieval Pipeline

Every answer produced by the system should include its reasoning metadata.

```
User Question

↓

Retrieval Engine

↓

Relevant Chunks

↓

Knowledge Graph

↓

Timeline Context

↓

LLM Extraction

↓

Validation

↓

Explainability Engine

↓

Final Response
```

Every response should ideally contain:

- extracted answer
- confidence score
- source document
- page number
- supporting evidence
- retrieval strategy
- related documents

The objective is to maximize user trust.

---

# 21. Provider Pattern

External services should never be tightly coupled with business logic.

Every provider should implement a common interface.

Examples include:

Embedding Provider

```
EmbeddingProvider

├── FastEmbed
├── OpenAI
├── VoyageAI
└── Future Providers
```

LLM Provider

```
LLMProvider

├── OpenAI
├── Anthropic
├── Gemini
├── Ollama
└── Future Providers
```

OCR Provider

```
OCRProvider

├── PyMuPDF
├── Tesseract
├── Google Vision
├── Azure OCR
└── Future Providers
```

Business logic should remain independent from provider implementations.

---

# 22. Recommended Repository Structure

```
backend/

api/
core/
config/

services/

    workspace/
    parsing/
    retrieval/
    extraction/
    explainability/
    graph/
    timeline/
    embeddings/
    layout/

repositories/

models/

schemas/

providers/

    llm/
    embeddings/
    parser/
    ocr/

utils/

tests/

frontend/

components/

pages/

hooks/

lib/

docs/

improvements/
```

Each directory should own exactly one responsibility.

---

# 23. AI Architectural Freedom

The architecture described in this document represents the intended direction of the project rather than a strict implementation constraint.

When implementing any feature, Antigravity should evaluate whether an alternative design provides superior:

- maintainability
- scalability
- modularity
- explainability
- performance
- developer experience
- user experience

If a better implementation exists:

- explain the reasoning
- explain the tradeoffs
- document the architectural decision
- preserve compatibility whenever practical

The objective is not to follow this document literally.

The objective is to build the best possible version of DocuFlow AI.

---

# 24. Architectural Innovation

Antigravity is encouraged to think beyond explicit feature requests.

Whenever appropriate, propose additional improvements that naturally integrate into the existing architecture.

Suggested improvements should:

- solve real engineering problems
- improve AI reliability
- reduce technical debt
- improve maintainability
- enhance explainability
- improve user experience
- remain realistically implementable

Before implementation:

- explain the proposal
- justify the engineering value
- describe architectural impact

Innovation should always serve the product rather than simply introducing complexity.

---

# 25. Development Lifecycle

Every feature should follow a consistent engineering workflow.

```
Understand

↓

Analyze

↓

Design

↓

Plan

↓

Implement

↓

Verify

↓

Debug

↓

Document

↓

Review

↓

Commit
```

Each stage should be completed before progressing to the next.

---

# 26. Definition of Architectural Completion

A module is considered architecturally complete only when:

- responsibilities are clearly defined
- interfaces are stable
- dependencies remain loosely coupled
- documentation is updated
- implementation remains replaceable
- tests can be written independently
- future extensions are clearly identified

---

# 27. Future Expansion Hooks

The architecture intentionally reserves extension points for future capabilities.

Examples include:

- Visual Question Answering
- Agentic Workflows
- Human Feedback Loops
- Retrieval Benchmark Dashboard
- Document Version Graph
- Multi-user Collaboration
- Enterprise Authentication
- Workflow Automation
- Compliance Auditing
- Document Recommendation Engine
- AI-powered Document Classification
- Natural Language Workflow Builder
- Active Learning Pipelines
- Autonomous Extraction Optimization

Future modules should integrate without requiring significant architectural changes.

---

# 28. Architectural Principles

Every engineering decision should optimize for:

- Simplicity
- Readability
- Maintainability
- Modularity
- Explainability
- Scalability
- Reliability
- Testability
- Production Readiness

Avoid introducing unnecessary complexity simply because it is technically interesting.

Prefer solutions that another engineer can understand, extend, and maintain one year later.

---

# 29. Final Architectural Vision

DocuFlow AI should evolve into a modular AI Document Intelligence Platform capable of managing, understanding, connecting, and explaining complex document ecosystems.

The platform should not merely answer questions about documents.

It should:

- understand relationships
- reconstruct workflows
- explain its reasoning
- connect isolated information
- provide trustworthy AI outputs
- remain extensible for future AI capabilities

Every architectural decision should move the project closer to becoming a production-grade AI platform suitable for enterprise environments while remaining understandable, maintainable, and interview-ready.