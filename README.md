# 🌐 DocuFlow AI

> **An AI-powered Document Intelligence Platform for Information Extraction, Retrieval, Validation, and Workflow Automation.**

DocuFlow AI is an enterprise-grade platform designed to process unstructured documents (PDFs, images, Word files), extract validated structured knowledge using Large Language Models (LLMs), index chunks into a vector database for semantic search, and orchestrate workflow automations.

---

## 🏗️ Architectural Concept

DocuFlow AI is built using **Clean Architecture** and **SOLID Principles** to ensure modularity, scalability, and long-term maintainability. 

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
                              ┌─────────────┴─────────────┐
                              ▼                           ▼
                      +---------------+           +---------------+
                      |   FastEmbed   |           |  OpenAI Embed |
                      |  (Local CPU)  |           | (Cloud/384-d) |
                      +-------+-------+           +-------+-------+
                              |                           |
                              └─────────────┬─────────────┘
                                            v
                                  +-------------------+
                                  |    PostgreSQL     |
                                  |  (with pgvector)  |
                                  +-------------------+
```

---

## 🛠️ Technology Stack

| Component | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 |
| **AI / Vector** | pgvector, FastEmbed, OpenAI Embeddings, LangChain |
| **Frontend** | Next.js, TypeScript, TailwindCSS, shadcn/ui, React Query, Zod, Recharts |
| **Database** | PostgreSQL |
| **DevOps & QA** | Docker, Docker Compose, Pytest, Ruff, Black, ESLint, Prettier |

---

## 📂 Folder Structure

```
DocFlow AI/
├── backend/                  # FastAPI Application Service
│   ├── app/
│   │   ├── api/              # API router, versioning, dependencies, request schemas
│   │   ├── core/             # Configuration, logging setup, security, database session
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── schemas/          # Pydantic schemas (DTOs)
│   │   ├── services/         # Core business logic (Parsing, Chunking, Extraction)
│   │   ├── repositories/     # Database read/write operations (Data Access Layer)
│   │   └── tests/            # Test suite (unit, integration, mock databases)
│   ├── alembic/              # Database migration tracking
│   ├── Dockerfile            # Container build for backend
│   ├── requirements.txt      # Python dependencies
│   └── alembic.ini           # Migration settings
├── frontend/                 # Next.js Frontend App
│   ├── app/                  # Next.js App Router (pages & endpoints)
│   ├── components/           # Reusable UI components (shadcn/ui)
│   ├── lib/                  # Utilities, fetchers, configuration
│   ├── hooks/                # Custom React hooks (React Query etc.)
│   ├── types/                # TypeScript type definitions
│   ├── Dockerfile            # Container build for frontend
│   └── package.json          # Node dependencies
├── docs/                     # Design and architectural documentation
│   ├── Architecture.md       # High-level architecture and data flows
│   ├── Database.md           # Schema design and pgvector documentation
│   ├── API.md                # Endpoint layout and responses
│   ├── Development.md        # Setup guide, linting/formatting rules
│   ├── Roadmap.md            # Milestones and project phases
│   └── Status.md             # Project lifecycle tracking
├── docker-compose.yml        # Orchestration file (backend, frontend, db)
├── .env.example              # Template environment variables
└── README.md                 # Project README
```

---

## 🗺️ Project Roadmap

- [x] **Phase 0: Project Planning** - Architecture, database schema, API specification, Docker roadmap.
- [x] **Phase 1: Repo Initialization** - Multi-container environment setup (Compose), styling, boilerplate setup, and Embedding Provider refactoring.
- [ ] **Phase 2: Backend Foundation** - Config, Logging, SQLAlchemy 2.0 connection, Alembic setup, health routes.
- [ ] **Phase 3: Parsing Pipeline** - PDF/image ingestion, text extracting, OCR framework design.
- [ ] **Phase 4: Vector Store** - Vector database initialization, chunking strategy, and EmbeddingProvider vector pipeline.
- [ ] **Phase 5: Structured AI Extraction** - Prompt management, structured JSON schema mapping, validation & retry.
- [ ] **Phase 6: REST API Development** - Extraction validation, search endpoints, files querying.
- [ ] **Phase 7: Frontend Interface** - Dashboards, live uploading, extracting viewer, interactive vector search.
- [ ] **Phase 8: Production Polish** - CI pipelines, complete test suites, database indexing, user-guide generation.

---

## 🚀 Quick Start (Development)

> Detailed setup guide is available in [Development.md](file:///e:/Tareque%20Files/DocFlow%20Ai/docs/Development.md).

### 1. Prerequisites
- Docker & Docker Compose
- Node.js v20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### 2. Run with Docker Compose (Once Phase 1 is initialized)
```bash
docker compose up --build
```
The application will launch the following services:
- **Backend (FastAPI)**: `http://localhost:8000`
- **Frontend (Next.js)**: `http://localhost:3000`
- **Database (PostgreSQL + pgvector)**: `localhost:5432`

---

## 🔌 Embedding Provider Configuration

DocuFlow AI decouples vector ingestion logic using the **Provider Pattern**. You can switch the embedding backend solely via environment settings:

```ini
# To use lightweight local CPU embeddings (ONNX-powered, zero API costs)
EMBEDDING_PROVIDER=fastembed
FASTEMBED_MODEL=BAAI/bge-small-en-v1.5

# To use OpenAI cloud API (higher accuracy, requires network)
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your-openai-api-key-here
```

### Performance & Vector Dimensions Tradeoffs
- **FastEmbed (Default)**: Generates 384-dimension embeddings. Highly optimized for speed and low CPU footprints. Zero operational costs.
- **OpenAI**: The `text-embedding-3-small` model normally outputs 1536 dimensions. We utilize **Matryoshka Representation Learning** to truncate outputs directly to **384 dimensions** at the API-side. This allows seamless toggling between FastEmbed and OpenAI without altering PostgreSQL `pgvector` schemas.

---

## 📄 License
This project is licensed under the MIT License. See the LICENSE file for details.
