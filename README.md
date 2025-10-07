
# 🌱 Carbon Credit Tracker

A production-minded REST API to manage the carbon credit lifecycle with immutable audit trails and deterministic, idempotent record creation. Built with FastAPI, SQLAlchemy, and an append-only event log for full traceability.


## Table of contents

- [Quick overview](#quick-overview)  
- [Key features](#key-features)  
- [Architecture](#architecture)  
- [Data model (high level)](#data-model-high-level)  
- [Getting started](#getting-started)  
- [API overview](#api-overview)  
- [Design decisions](#design-decisions)  
- [Configuration & deployment](#configuration--deployment)  
- [Testing](#testing)  
- [Project layout](#project-layout)  
- [Contributing & license](#contributing--license)

---

## Quick overview

This service manages carbon credits through their lifecycle (CREATED → SOLD → RETIRED) using event-sourcing principles. Every action is recorded in an append-only events table so state can be reconstructed at any point in time and audited for compliance.

## Key features

- Deterministic record IDs (SHA256) for idempotent creates  
- Append-only event log (CREATED, SOLD, RETIRED, ...)  
- Database-level constraints to prevent race conditions (e.g., double-retire)  
- Input canonicalization for consistent ID generation  
- Pydantic validation and OpenAPI (Swagger) docs via FastAPI  
- Small, auditable codebase ready for SQLite (dev) and PostgreSQL (prod)

## Architecture

High-level flow:

┌──────────────┐    ┌──────────────┐    ┌────────────────────┐
│  FastAPI     │──▶ │ SQLAlchemy   │──▶ │ SQLite / Postgres  │
│  (routes)    │    │ (models)     │    │ (storage)          │
└──────────────┘    └──────────────┘    └────────────────────┘
       ▲
       │
       ▼
┌──────────────┐    ┌──────────────┐
│ Pydantic     │    │ Utils        │
│ (schemas)    │    │ (canonicalize│
└──────────────┘    │  + id gen)   │
                    └──────────────┘

Core flow:
- Incoming requests -> validated by Pydantic -> canonicalize inputs -> generate deterministic ID -> persist immutable record (if not exists) -> append CREATED event -> return record + events.

## Data model (high level)

Records (immutable snapshot)
- id: deterministic SHA256 (primary key)  
- project_name, registry, vintage, quantity, serial_number  
- created_at timestamp

Events (append-only)
- id: UUID (primary key)  
- record_id: FK -> records.id  
- event_type: CREATED | SOLD | RETIRED | ...  
- payload: JSON (optional metadata)  
- created_at timestamp  
- Unique constraint (record_id, event_type) prevents duplicate events like double-retire.

Example SQL (conceptual)
```sql
-- records (immutable)
CREATE TABLE records (
  id TEXT PRIMARY KEY,
  project_name TEXT NOT NULL,
  registry TEXT NOT NULL,
  vintage INTEGER NOT NULL,
  quantity NUMERIC(18,4) NOT NULL,
  serial_number TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL
);

-- events (append-only)
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  record_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload JSON,
  created_at TIMESTAMP NOT NULL,
  UNIQUE(record_id, event_type)
);
```

## Getting started

Prerequisites
- Python 3.8+  
- pip (or poetry)  
- Optional: PostgreSQL for production

Install & run (development)
```bash
git clone https://github.com/gupta-nu/carboncerdit.git
cd carboncerdit
pip install -r requirements.txt
uvicorn main:app --reload
```

OpenAPI docs: http://127.0.0.1:8000/docs

## API overview

POST /records
- Create a record (idempotent). Canonicalizes input and derives a deterministic SHA256 id.
- Request (JSON):
```json
{
  "project_name": "Solar Farm Maharashtra",
  "registry": "VCS",
  "vintage": 2023,
  "quantity": 100.0,
  "serial_number": "VCS-001"
}
```
- Success: 201 Created (or 200 if identical record already exists). Returns record and event list.

GET /records/{id}
- Return the record and full event history including computed status (ACTIVE/RETIRED).

POST /records/{id}/retire
- Append a RETIRED event. Returns 200 on success, 409 Conflict if already retired.

Example curl (create)
```bash
curl -X POST "http://127.0.0.1:8000/records" \
  -H "Content-Type: application/json" \
  -d '{"project_name":"Solar Farm","registry":"VCS","vintage":2023,"quantity":100,"serial_number":"VCS-001"}'
```

Error model
- Uses standard HTTP codes: 400 (validation), 404 (not found), 409 (conflict), 500 (server error). Error bodies follow FastAPI default {"detail": "..."} format.

## Design decisions (concise)

- Deterministic ID: canonicalize inputs (trim, lowercase, NFKC), quantize decimals, concatenate fields, then SHA256 — guarantees identical inputs map to the same record id and makes create idempotent.
- Event sourcing: immutable audit trail simplifies compliance and forensic inspection.
- DB constraints + transactions: rely on the RDBMS for concurrency correctness (unique constraint on record/event combos).
- Minimal domain model: keeps attack surface small and logic auditable.

## Configuration & deployment

Environment
- DATABASE_URL (default: sqlite:///./carbon_credits.db)

SQLite (dev)
```bash
uvicorn main:app
```

Postgres (prod example)
```bash
export DATABASE_URL="postgresql://user:password@localhost/carbon_credits"
uvicorn main:app --host 0.0.0.0 --port 8000
```

Consider adding Alembic for migrations in production.

## Testing

Run lightweight integration tests (assumes server running or tests start the app)
```bash
python test_api.py
```
Tests validate create → get → retire flows and conflict handling.

## Project layout

carboncerdit/
- main.py — FastAPI app, startup hooks  
- routes.py — API endpoints and handlers  
- models.py — SQLAlchemy models (Record, Event)  
- schemas.py — Pydantic request/response models  
- database.py — DB engine & session management  
- utils.py — canonicalization & deterministic id generation  
- test_api.py — minimal integration tests  
- requirements.txt  
- sample-registry.json

Files of interest:
- utils.generate_record_id — deterministic SHA256 id logic  
- models.Event — contains UniqueConstraint('record_id','event_type') to prevent double-retire

## Contributing & license

Contributions are welcome. Suggested workflow:
1. Fork
2. Create branch
3. Add tests
4. Open a PR

License: MIT — see LICENSE file.

Contact
- Open an issue or PR on the repository for questions or improvements.

