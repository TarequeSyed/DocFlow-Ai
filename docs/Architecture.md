# 🏗️ System Architecture - DocuFlow AI

This document details the architectural layout, core design decisions, and system blueprints for **DocuFlow AI**.

---

## 1. Architectural Philosophy

DocuFlow AI strictly adheres to **Clean Architecture** and **SOLID Principles**. The codebase is designed to decouple business rules from infrastructure details (like database models, external APIs, and OCR engines).

### The Clean Architecture Layer Model

Our application is divided into concentric layers where dependencies only point inward:

```
+-----------------------------------------------------------+
|                   INFRASTRUCTURE LAYER                    |
|  [Next.js Frontend] [Docker] [PostgreSQL / pgvector]      |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                       API LAYER                           |
|       [FastAPI Routers] [Middlewares] [Dependencies]      |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                    APPLICATION LAYER                      |
|      [Services (Extraction, Parsing, Vector Ingestion)]    |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                     DATA ACCESS LAYER                     |
|           [Repositories] [SQLAlchemy DB Models]           |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                      DOMAIN LAYER                         |
|             [Pydantic Schemas / DTOs] [Enums]             |
+-----------------------------------------------------------+
```

1. **Domain Layer (`schemas/`, `constants/`)**: Holds plain models (Pydantic schemas) and enterprise rules. Free from external library imports (except Pydantic).
2. **Data Access Layer (`repositories/`, `models/`)**: Deals with raw data storage, querying, and updating. Translates DB models into domain schemas.
3. **Application Layer (`services/`)**: Orchestrates data flows and processes logic (e.g., parsing PDFs, generating embeddings, executing extraction workflows).
4. **API Layer (`api/`)**: Defines HTTP routes, input validation, serialization, authentication dependencies, and error handling.
5. **Infrastructure Layer**: Outer systems like Next.js, PostgreSQL/pgvector database, Hugging Face transformers, and LLM services.

---

## 2. Core Pipelines & Component Flows

### A. Document Ingestion & Processing Pipeline

This pipeline handles file uploading, persistent storage, text extraction (native and OCR), chunking, embedding generation, and indexing.

```mermaid
sequenceDiagram
    autonumber
    actor User as Client (Frontend)
    participant API as FastAPI Router
    participant DB as Postgres Repository
    participant Parser as Parser Service
    participant Embed as Embedding Service
    participant VecDB as pgvector Store

    User->>API: POST /api/v1/documents (Upload PDF/Image)
    API->>DB: Save Document Metadata (Status: PENDING)
    API->>Parser: Parse File
    alt Native PDF
        Parser->>Parser: Extract Native Text
    else Scanned PDF / Image
        Parser->>Parser: Run OCR Service (Tesseract/Google Vision)
    end
    Parser->>DB: Save Extracted Full Text & Update Status (PARSED)
    Parser->>Embed: Pass Full Text for Chunking
    Embed->>Embed: Apply Semantic/Recursive Character Chunking
    Embed->>Embed: Generate Embeddings (Sentence-Transformers)
    Embed->>VecDB: Save Chunks + 384-dim Embeddings
    VecDB-->>API: Success
    API-->>User: HTTP 201 Created (Document ID, Status: READY)
```

### B. AI Extraction Pipeline

Converts parsed documents into structured JSON objects adhering to user-defined extraction schemas.

```mermaid
sequenceDiagram
    autonumber
    actor User as Client (Frontend)
    participant API as FastAPI Router
    participant Service as Extraction Service
    participant LLM as LLM Connector
    participant Valid as Validation Layer
    participant DB as Postgres Repository

    User->>API: POST /api/v1/extractions (Document ID, Schema ID)
    API->>Service: Trigger Schema Extraction
    Service->>DB: Retrieve Document Text & Target Schema
    Service->>LLM: Formulate Prompt with Context + JSON Schema
    LLM->>LLM: Execute Completion (Structured Output)
    LLM-->>Service: Raw JSON Output
    Service->>Valid: Validate JSON against Pydantic Schema
    alt Valid Output
        Valid-->>Service: Validated Pydantic Object
    else Invalid Output (Schema Mismatch)
        Valid-->>Service: Raise ValidationError
        Service->>LLM: Retry Request (Prompt detailing validation error)
    end
    Service->>DB: Save Extracted Structured Data
    Service-->>API: Extraction Results
    API-->>User: HTTP 200 OK (Structured JSON Results)
```

---

## 3. SOLID & Clean Coding Patterns

To prevent the application from degrading into spaghetti code over time, we enforce the following guidelines:

### Single Responsibility Principle (SRP)
- **Routers** are thin. Their only job is to receive requests, run dependency injection, call a service, and return results.
- **Services** contain business logic. They do not query the database directly; instead, they call a Repository.
- **Repositories** handle database queries. They do not know about LLMs, schemas parsing, or file saving.

### Open/Closed Principle (OCP)
- **Parsers** inherit from a base class `BaseParser`. If we switch from PyMuPDF to an OCR engine, we subclass it without editing the service.
- **LLM Clients** inherit from `BaseLLMClient`. This allows swapping between Anthropic, OpenAI, or local Ollama with zero business logic modifications.

### Liskov Substitution Principle (LSP)
- All parser implementations must strictly adhere to the `BaseParser` interface:
  ```python
  class BaseParser(ABC):
      @abstractmethod
      async def parse(self, file_content: bytes) -> ParsedDocumentDTO:
          pass
  ```

### Dependency Inversion Principle (DIP)
- Inject dependencies using FastAPI's `Depends` system.
- Never instantiate database sessions, repositories, or services globally.
- E.g., a router depends on a service interface, which in turn depends on a repository interface.
