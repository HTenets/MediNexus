# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MediNexus (医枢) is an open-source multi-agent medical diagnosis platform (v0.1.0, early development). It orchestrates multiple AI agents — Triage, Doctor (with specialty Skills), Review, Coordinator, and Follow-up — to conduct medical consultations, with guardrails for safety, a plugin system for extensibility, and hierarchical memory for patient context.

## Tech Stack

- **Backend**: FastAPI + Python 3.12+, LangGraph for agent orchestration, Celery for async tasks
- **Databases**: PostgreSQL 17 + pgvector (primary store), Qdrant (vector store), Redis (cache/sessions)
- **Memory**: Mem0 for long-term patient memory (episodic + semantic + working stores)
- **LLM**: Unified client interface with Anthropic, OpenAI, and Ollama providers
- **Frontend**: Next.js 14 + React 18 + Tailwind CSS 3 + shadcn/ui

## Commands

```bash
# Development servers
make dev-backend       # uvicorn app.main:app --reload on port 8000
make dev-frontend      # next dev on default port

# Docker
make docker-up         # docker-compose up --build (postgres + redis + qdrant + backend)
make docker-down       # docker-compose down

# Database
make db-migrate msg="description"  # alembic revision --autogenerate
make db-upgrade                    # alembic upgrade head
make db-downgrade                  # alembic downgrade -1
make init-db                       # python scripts/init_db.py

# Dependencies
make install           # pip install -e . (backend) + npm install (frontend)
```

Environment variables (loaded via `pydantic-settings` from `.env`, prefixed `MEDINEXUS_`): `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`, `JWT_SECRET`, `JWT_ALGORITHM`.

## Architecture

### Agent Pipeline

```
User → TriageAgent → DoctorAgent (with Skills) → ReviewAgent → Output
              ↕
       CoordinatorAgent (multi-specialty consultations)
              ↕
       FollowupAgent (post-visit monitoring)
```

All agents inherit from `BaseAgent` (`backend/agents/base.py`) and implement `async run(context) -> HandoverManifest`. The `HandoverManifest` (`backend/app/schemas/agent.py`) is the standard inter-agent message format carrying `facts`, `pending_questions`, `risk_flags`, `evidence_level` (A/B/C), and arbitrary `context`. Each agent also has `on_pre_process` and `on_post_process` hooks for plugin injection.

### Orchestration Layer (`backend/orchestration/`)

- `state.py` — `SessionState` dataclass tracking session_id, patient_id, current_agent, history, context
- `graph.py` — `ConsultationGraph` (LangGraph-based state graph, currently stub)
- `supervisor.py` — `SupervisorAgent` routes patients to the appropriate agent based on context
- `stream.py` — Streaming support

### Memory System (`backend/memory/`)

Hierarchical memory with three tiers:
- **Working Memory** (`working.py`) — Redis-backed short-term session state (TTL-based)
- **Episodic Memory** (`stores/episodic.py`) — Past consultation/visit records
- **Semantic Memory** (`stores/semantic.py`) — Patient profile (allergies, history, conditions)
- `manager.py` — `MemoryManager` orchestrates retrieval across all tiers

### Knowledge & RAG (`backend/knowledge/`)

- `rag.py` — `RAGQuery` using Qdrant vector store
- `graph_rag.py` — `GraphRAGQuery` with identical API for interchangeable use
- `loader.py` — Knowledge loading utilities

### LLM Layer (`backend/llm/`)

- `client.py` — `BaseLLMClient` abstract class with `chat()` and `chat_stream()` methods
- `providers/anthropic.py`, `providers/openai.py`, `providers/ollama.py` — Provider implementations

### Guardrails (`backend/guardrails/`)

- `emergency_detector.py` — Keyword + semantic detection of emergency signals (suicide, chest pain, etc.) in both English and Chinese
- `pii_sanitizer.py` — PII sanitization
- `identity_verifier.py` — Identity verification

### Plugin System (`plugins/sdk/`)

- `base.py` — `BasePlugin` abstract class with `initialize()` and `shutdown()` lifecycle
- `hooks.py` — `PluginHooks` for `on_agent_pre_process` and `on_agent_post_process` interception points

### API Layer (`backend/app/`)

Routes mounted at `/api/v1`:
- `POST /api/v1/consult` — Start a consultation
- `GET /api/v1/consult/{id}` — Get consultation status
- `WS /ws/{session_id}` — WebSocket streaming dialogue
- `GET /api/v1/patients/{id}` — Patient info
- `GET /api/v1/records/{id}` — Medical records
- `GET /health` — Health check

### Frontend (`frontend/`)

Next.js 14 App Router with Tailwind CSS and shadcn/ui components.

## Configuration

Settings loaded via `pydantic-settings` from environment variables prefixed with `MEDINEXUS_`, with `.env` file support. Config class at `backend/app/config.py`.

## Code Conventions

- All agents are in `backend/agents/<name>/` with `agent.py` (implementation), `prompt.py` (system prompts), and `__init__.py`
- Doctor agent additionally has `skills/` and `diagnosis_flow.py` (state machine: INITIAL → HISTORY_TAKING → DIFFERENTIAL → TREATMENT → COMPLETED)
- Review agent has `checkers/` and `rules/` submodules
- Database models use SQLAlchemy 2.0+ async style with asyncpg
- All agent-to-agent communication uses `HandoverManifest` Pydantic model
