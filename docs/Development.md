# 🛠️ Development Guide - DocuFlow AI

This guide explains how to set up the development environment, configure variables, enforce styling conventions, run tests, and manage container deployments.

---

## 1. Prerequisites

Before starting, ensure you have installed:
- **Docker** and **Docker Compose**
- **Python 3.12+**
- **Node.js v20+** and **npm**
- **Git**

---

## 2. Environment Variables (`.env`)

Create a `.env` file in the project root directory. Do not commit this file to version control. Reference the template in `.env.example`.

### Core Configuration Variables
```ini
# Application Mode
ENVIRONMENT=development
PROJECT_NAME="DocuFlow AI"

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_postgres_pass
POSTGRES_DB=docuflow_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# Embedding Providers Config
EMBEDDING_PROVIDER=fastembed # 'fastembed' or 'openai'
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
FASTEMBED_MODEL=BAAI/bge-small-en-v1.5

# LLM Extractor Credentials
OPENAI_API_KEY=your-openai-api-key-here
LLM_MODEL_NAME=gpt-4o-mini

# Parsing Storage Config
UPLOAD_DIR=/app/uploads
```

---

## 3. Code Standards & Style Enforcers

We enforce linting and formatting policies on every commit.

### Backend (Python)
- **Formatters**: `black` (line length: 88), `isort` (imports ordering).
- **Linter**: `ruff` (combines PEP8 checks, Pyflakes, and security audits).
- **Type Checker**: `mypy` for static analysis.

#### Commands to run locally
```bash
# Execute code formatting
black backend/
isort backend/

# Execute ruff linter checks
ruff check backend/ --fix

# Run static type verification
mypy backend/
```

### Frontend (TypeScript / React)
- **Linter**: `ESLint` (React & Next.js rules).
- **Formatter**: `Prettier`.

#### Commands to run locally
```bash
# Execute lint check
cd frontend
npm run lint

# Execute prettier check
npm run format
```

---

## 4. Run Locally (Docker Compose)

The easiest way to bootstrap the application is using Docker Compose.

```bash
# Spin up all containers in detached mode
docker compose up -d --build

# Inspect streaming log feeds
docker compose logs -f

# Shut down containers and clean up volumes
docker compose down -v
```

---

## 5. Testing Guidelines

Never push code without completing testing verification. Development packages are defined in `backend/requirements-dev.txt`.

### Backend Testing (Pytest)
We write asynchronous tests using `pytest` and `pytest-asyncio`. 

```bash
# Execute test suite
docker compose run --entrypoint pytest backend

# Execute tests with coverage check
docker compose run --entrypoint "pytest --cov=app --cov-report=term-missing" backend
```

### Mocking Guidelines
- **External APIs (LLMs)**: Mock LLM service responses using `unittest.mock` or a custom mock connector. Never trigger real LLM calls during automated unit/integration tests.
- **Database**: Use a separate transactional test database session (`asyncpg`) that rolls back transactions after each test run.

---

## 6. Git & Commit Workflows

We use the **Conventional Commits** standard. Commit messages must be structured as follows:

```
<type>(<scope>): <description>

[optional body]
```

### Accepted Commit Types
- `feat`: A new user-facing feature.
- `fix`: A bug fix.
- `docs`: Documentation edits only.
- `style`: Formatting, missing semi-colons, etc. (no business code changes).
- `refactor`: Restructuring code without changing its external behavior.
- `test`: Adding or editing tests.
- `chore`: Modifying build tasks, package manager configs, etc.

#### Example Commit
```bash
git commit -m "feat(parser): add native PDF extraction with text flow preservation"
```
