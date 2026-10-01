# AGENTS.md

Guidance for AI coding agents (Claude Code, or any subagent) working in this
repo. Read this before touching code. Task-specific specs live in `/tasks`.

## Project summary

A self-hosted job-application tracker: Vue 3 (Vite) + Tailwind frontend,
FastAPI + SQLAlchemy backend, Postgres database, all wired together with
Docker Compose for local dev with hot reload.

## Stack & conventions

**Backend** (`backend/app/`)
- FastAPI, SQLAlchemy (sync, `Session`), Pydantic v2.
- Pattern per resource: `models.py` (ORM) → `schemas.py` (Pydantic) →
  `crud.py` (DB functions) → `routers/<resource>.py` (HTTP layer).
- New resources get their own router file, included in `main.py`.
- Use `model_dump(exclude_unset=True)` for partial updates (see
  `crud.update_application`).
- No migration tool is set up yet — `models.Base.metadata.create_all` runs on
  startup. If a task needs a schema change to an *existing* table with data
  you care about, add Alembic rather than relying on `create_all` (it won't
  alter existing tables).

**Frontend** (`frontend/src/`)
- Vue 3, `<script setup>` only — do not mix with a plain `<script>` export
  in the same file.
- Tailwind utility classes for all styling; no separate CSS files per
  component. Keep the existing muted slate/amber palette.
- API calls go through `src/api.js`; add new resource methods there rather
  than calling `fetch` directly from components.
- One component = one concern. Follow the existing
  `KanbanBoard` → `ApplicationCard` / `ApplicationModal` split when adding
  UI for a new feature.

**Environment variables**
- Backend reads config via `os.getenv` (see `database.py`). Add new vars the
  same way; document them in `docker-compose.yml` and in the relevant
  task's "Env vars" section, and add a default so local dev doesn't break.
- Never commit real API keys. `.env` is gitignored — use `.env.example` for
  documented defaults/placeholders if a task introduces one.

## Task workflow for subagents
Prerequisite: Always delegate task to the agent defined in `tasks/!maintask.txt` as subagent

1. Pick one file from `/tasks` — each is scoped to be implementable
   independently without touching the other task's files.
2. Implement backend changes first (model → schema → crud → router →
   `main.py` registration), then frontend.
3. Update `README.md`'s "API endpoints" table and "Data model" section if
   you add/change either.
4. Do not refactor unrelated code while implementing a task. If you spot
   something that should change, note it at the end of your summary instead
   of doing it inline.
5. Mark the task file's checklist items with `[x]` as you complete them, and
   add a `## Status` line at the top (`Not started` / `In progress` /
   `Done`) so parallel subagents and the human can see progress at a glance.
6. Commit message must be structured similar to `feat: <description>` as an example.
