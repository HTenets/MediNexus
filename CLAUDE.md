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

## AI Code Structure (AI 可读代码结构)

This project maintains AI-readable code structure documentation for long-term AI-assisted development.

### `.claude/codebase/` — Code Graph (代码图谱)

The canonical reference for AI to understand the codebase before making changes:

| File | Purpose |
|------|---------|
| [MODULE_MAP.md](.claude/codebase/MODULE_MAP.md) | Complete module inventory — responsibilities, interfaces, dependencies, status |
| [API_SURFACE.md](.claude/codebase/API_SURFACE.md) | REST + WebSocket API specification |
| [DATA_FLOW.md](.claude/codebase/DATA_FLOW.md) | Data flow diagrams (REST / WebSocket / Agent Pipeline) |
| [DEPENDENCY_GRAPH.md](.claude/codebase/DEPENDENCY_GRAPH.md) | Import dependency graph + impact analysis |
| [BUILD_STATUS.md](.claude/codebase/BUILD_STATUS.md) | Component completion status, known issues, roadmap |
| [CONVENTIONS.md](.claude/codebase/CONVENTIONS.md) | Code conventions with examples |

### Memory System — Persistent Context (持久化上下文)

Tracks project state, decisions, and priorities across sessions. Located at `~/.claude/projects/E--Program-MediNexus/memory/`.

### Quick Links for AI

| When... | Read this first |
|---------|-----------------|
| Adding a new Agent | `CONVENTIONS.md` (template) + `MODULE_MAP.md` (existing agents) |
| Adding an API endpoint | `API_SURFACE.md` (existing routes) + `CONVENTIONS.md` (routing style) |
| Modifying the pipeline | `DATA_FLOW.md` (data flow) + `DEPENDENCY_GRAPH.md` (impact analysis) |
| Understanding priorities | `BUILD_STATUS.md` (what's done vs TODO) |
| Making an architecture decision | `architecture-decisions.md` (existing ADRs) |

## 部署注意：低配服务器内存优化（2核2G）

本项目在阿里云 2核2G 实例部署时，**构建阶段极易因内存不足（OOM）卡死**，开发与部署务必注意：

- **前端构建内存**：`infrastructure/docker/Dockerfile.frontend` 已将 `NODE_OPTIONS=--max-old-space-size` 限制为 `1024`（原为 2048，在 2G 机器上会 OOM）。调小此值前需先确认服务器已配置 swap，否则 Next.js 构建可能直接失败。
- **运行时内存上限**：`docker-compose.yml` 已为所有服务设置 `mem_limit` / `memswap_limit`（适配 2G：postgres/backend/qdrant/frontend 各 512M，worker 384M，redis/nginx 各 128M）。**修改 `docker-compose.yml` 内存相关配置时，必须保证各服务上限之和不超过服务器物理内存 + swap**，否则运行时会 OOM。
- **构建命令**：部署时**禁止** `docker-compose build --no-cache` 的并行全量构建；应串行构建（`build --no-parallel` 或逐个 `build <service>`），并在构建前 `down` + `prune` 释放内存。详细步骤见 `docs/deploy-aliyun.md` 第 10.4 节。
- **升级服务器**：官方推荐配置为 4核8G（见 `docs/deploy-aliyun.md` 第 2.1 节）。2G 为最低可行配置，仅适合 demo。
