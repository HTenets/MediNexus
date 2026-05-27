# MediNexus Architecture

## System Overview

Multi-agent AI medical diagnosis platform with modular skill system.

## Core Flow

User → Triage Agent → Doctor Agent (with Skill) → Review Agent → Output
                                     ↕
                              Coordinator Agent (consultation)
                                     ↕
                              Follow-up Agent (post-visit)

## Tech Stack

- Backend: FastAPI + Python 3.12
- Agent Orchestration: LangGraph
- Database: PostgreSQL 16 + pgvector
- Vector Store: Qdrant
- Memory: Mem0
- Frontend: Next.js 14 + React + shadcn/ui
