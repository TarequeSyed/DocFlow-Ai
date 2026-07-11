# 🌐 DocuFlow AI

> **A production-oriented AI Document Intelligence Platform in active development. Current release: Working MVP.**

DocuFlow AI is a modular platform designed to ingest unstructured documents (PDFs, text files), parse and segment their contents, generate vector embeddings, and extract validated structured knowledge (JSON) conforming to custom metadata templates.

Unlike generic RAG chatbots that stop at conversational question-answering, DocuFlow AI is engineered to convert complex documents into queryable, machine-readable structured knowledge pipelines suitable for down-stream database indexing and business workflows.

---

## 🚧 Current Development Status

The repository currently hosts a **fully functional end-to-end MVP** demonstrating the core document parsing, vector indexing, semantic retrieval, and structured schema extraction pipelines. 

### ✅ Implemented in the Current MVP
* **Document Ingestion**: File uploading with hash-based deduplication to prevent duplicate parsing.
* **Document Parsing**: In-memory text extraction using native PyMuPDF (`fitz`) with scanning OCR fallbacks.
* **Intelligent Chunking**: Document segmentation utilizing LangChain's `RecursiveCharacterTextSplitter`.
* **Embedding Generation**: Dual-provider embedding factory pipeline supporting CPU-optimized `FastEmbed` and Matryoshka-truncated `OpenAI` embeddings (both standardized to 384 dimensions).
* **Database & Vector Index**: PostgreSQL relational model mappings running pgvector distance operators.
* **Adaptive Retrieval**: Query embedding generation and cosine similarity lookup.
* **Schema-Based structured Extraction**: Dynamic validation schema mapping utilizing runtime Pydantic validation models, with support for OpenAI Chat models or rule-based local mock extraction fallbacks.
* **Dashboard Interface**: Next.js (TailwindCSS v4) client-side tabbed workspace workspace managing uploads, schema templates, structured extraction runs, and semantic queries.
* **Dockerized Deployment**: Fully orchestrated environment managed via Docker Compose.

### 🔮 Scaffolded & Planned (Placeholders in Codebase)
The following advanced services are already architected, folder-scaffolded, and declared as clean placeholder interfaces (returning 501 / development indicators) to show enterprise-scale extensibility:
* **Knowledge Graph Retrieval**: Graph Database node/edge relationships mappings service.
* **Hybrid Retrieval**: Dense vector + keyword sparse search rankings.
* **Agentic Workflows**: Multi-step layout-aware extraction pipelines.
* **Validation & Confidence Scoring Engine**: Advanced data assertion and schema conformity scoring.
* **Enterprise Analytics**: Extraction accuracy and query benchmarks dashboards.

---

## 💡 Why DocuFlow AI? (Key Differentiator)

Generic RAG systems are designed for conversational question-answering, which is hard to automate or integrate with core enterprise applications. DocuFlow AI shifts the focus from **conversation** to **structured data extraction**. 

By mapping unstructured document contexts to dynamic, user-defined validation schemas, DocuFlow AI extracts clean, type-safe JSON records.

### Invoice Extraction Example
**Document Source Context:**
> "Acme Corp invoice INV-2026-991, dated July 11, 2026. The billed amount represents a total of 1,500.00 USD with a tax value of 270.00 GST."

**DocuFlow AI Structured Output:**
```json
{
  "invoice_number": "INV-2026-991",
  "vendor": "Acme Corp",
  "total_amount": 1500.00,
  "gst": 270.00
}
```

This output is accompanied by **Provenance Citation Trails** that link each extracted variable back to its exact parent chunk ID, page number, and similarity score, establishing audit trails for compliance.

---

## 🏗️ Architectural Concept

DocuFlow AI is built using **Clean Architecture** and **SOLID Principles** to ensure modularity, scalability, and loose coupling.

```
                                  +-------------------+
                                  |   Web Frontend    |
                                  | (Next.js / React) |
                                  +---------+---------+
                                            |
                                            | REST API (JSON)
                                            v
                                  +-------------------+
                                  |   FastAPI App     |
                                  +----+----+----+----+
                                       |    |    |
          +----------------------------+    |    +----------------------------+
          |                                 |                                 |
          v                                 v                                 v
+-------------------+             +-------------------+             +-------------------+
|  Document Parser  |             |  Vector Pipeline  |             |   LLM Extractor   |
| (PyMuPDF / OCR)   |             | (Embedding Prov.) |             |  (Structured JSON)|
+-------------------+             +---------+---------+             +-------------------+
                                            |
                                ┌───────────┴───────────┐
                                ▼                       ▼
                        +---------------+       +---------------+
                        |   FastEmbed   |       |  OpenAI Embed |
                        |  (Local CPU)  |       | (Cloud/384-d) |
                        +-------+-------+       +-------+-------+
                                |                       |
                                └───────────┬───────────┘
                                            v
                                  +-------------------+
                                  |    PostgreSQL     |
                                  |  (with pgvector)  |
                                  +-------------------+
```

### Future Extensions
* **Knowledge Graph Directory**: Connects entities dynamically (e.g. linking vendors to specific invoices and purchase order records).
* **Multi-Agent Orchestration**: Agent pipelines that dynamically check extraction errors and rerun corrections loops.
* **Enterprise Analytics**: Automated latency, cost, and extraction quality evaluations.

---

## 🛠️ Technology Stack

| Component | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.12, FastAPI, SQLAlchemy 2.0 (Async), Alembic, Pydantic v2 |
| **AI / Vector Search** | pgvector, FastEmbed, OpenAI API, LangChain (Recursive Splitter) |
| **Frontend Framework** | Next.js, React 19, TypeScript, TailwindCSS v4 |
| **Database** | PostgreSQL |
| **DevOps & Quality** | Docker, Docker Compose, Ruff, Black, Mypy |

---

## 📂 Folder Structure

```
DocFlow AI/
├── backend/                  # FastAPI Application Service
│   ├── app/
│   │   ├── api/              # Versioned API routes & dependencies
│   │   ├── core/             # Database connection pools & structured logging
│   │   ├── models/           # SQLAlchemy Declarative Models
│   │   ├── schemas/          # Pydantic validation DTOs
│   │   ├── services/         # Core business logic (Parser, Chunker, Extractor)
│   │   ├── repositories/     # Data access layer (Vector repository operations)
│   │   └── tests/            # Test suite
│   ├── alembic/              # Async migration scripts
│   ├── Dockerfile            # Multi-layer Docker cached build
│   └── requirements.txt      # Runtime dependencies
├── frontend/                 # Next.js SPA Client
│   ├── src/
│   │   └── app/              # Next.js page components, layouts, global styles
│   ├── Dockerfile            # Container build for frontend
│   └── package.json          # Node script commands & configurations
├── docs/                     # Design and architectural documentation
│   ├── Architecture.md       # High-level architecture and data flows
│   ├── Database.md           # Schema design and pgvector documentation
│   ├── API.md                # Endpoint layout and responses
│   └── Status.md             # Project lifecycle tracking
└── docker-compose.yml        # Orchestration configuration
```

---

## 🗺️ Project Roadmap

### ✅ Current MVP
* [x] Async Database setup using SQLAlchemy 2.0.
* [x] In-memory PDF text parsing via PyMuPDF.
* [x] Document segmenter chunking via LangChain.
* [x] Dual-provider Embedding Factory model truncation to 384 dimensions.
* [x] Relational schema mappings and pgvector similarity queries.
* [x] Dynamic runtime Pydantic validations models builder.
* [x] Structured JSON LLM extraction API and mock parser rules fallback.
* [x] Next.js frontend single-page dashboard with drop-zone uploads and status polling.

### 🚧 Active Development
* [ ] Advanced validation scoring (evaluating LLM extraction values).
* [ ] Multi-document cross-referencing reasoning loops.
* [ ] Dense + Sparse keyword hybrid search merges.

### 🔮 Future Vision
* [ ] Graph Database integration for Entity Knowledge Graph lookups.
* [ ] Multi-Agent self-correction retry engines.
* [ ] Production CI/CD pipelines and deployment charts.

---

## 🚀 Quick Start (Development)

### 1. Prerequisites
* Docker & Docker Compose
* Python 3.12+ (for local backend development)
* Node.js v20+ (for local frontend development)

### 2. Run via Docker Compose
```bash
docker compose up --build
```
The application will launch the following services:
* **Backend (FastAPI)**: `http://localhost:8000` (API documentation at `/docs`)
* **Frontend (Next.js)**: `http://localhost:3000`
* **Database (PostgreSQL + pgvector)**: `localhost:5432`

---

## 🔌 Embedding Provider Configuration

Decouple embedding engines solely via environment variables in the `.env` configuration file:

```ini
# For CPU-optimized local FastEmbed (Zero cost, no internet required)
EMBEDDING_PROVIDER=fastembed
FASTEMBED_MODEL=BAAI/bge-small-en-v1.5

# For OpenAI cloud API (requires key)
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your-openai-api-key
```

### Performance & Vector Dimensions Tradeoffs
* **FastEmbed (Default)**: Generates 384-dimension embeddings. Highly optimized for speed and low CPU footprints. Zero operational costs.
* **OpenAI**: The `text-embedding-3-small` model normally outputs 1536 dimensions. We utilize **Matryoshka Representation Learning** to truncate outputs directly to **384 dimensions** at the API-side. This allows seamless toggling between FastEmbed and OpenAI without altering PostgreSQL `pgvector` schemas.

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.
