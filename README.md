# CodeLens AI

AI-Powered Python Code Evaluation, Debugging & LLM Coding Assessment Platform.

## Overview
CodeLens AI is a professional developer platform that analyzes Python code using deterministic program analysis (AST parsing, static analysis, Ruff, Bandit, Radon complexity metrics), sandboxed Docker execution, automated test generation (pytest), and evidence-based LLM reasoning.

## Tech Stack
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Celery, Pytest
- **Python Analysis:** AST, Ruff, Bandit, Radon
- **LLM Provider Abstraction:** Google Gemini, OpenAI, Anthropic
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, Monaco Editor
- **Infrastructure:** Docker, Docker Compose, Isolated Docker Sandboxes

## Quick Start (Docker Compose)
1. Clone the repository.
2. Copy `.env.example` to `.env` and configure your API keys.
3. Run:
   ```bash
   docker-compose up --build
