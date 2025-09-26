# Carbon Credit Platform - Offset

A backend prototype for managing carbon credits with full lifecycle tracking (created → sold → retired).

## Features

- **Deterministic IDs**: Same input always generates same record ID
- **Idempotent Operations**: Duplicate create requests return existing record
- **Append-only Events**: All changes stored as immutable events
- **Concurrency Safety**: Database constraints prevent double-retirement
- **Input Canonicalization**: Normalizes data before processing

## API Endpoints

### POST /records
Create a new carbon credit record.

```json
{
  "project_name": "Rainforest Conservation",
  "registry": "Verra", 
  "vintage": 2021,
  "quantity": 10.0,
  "serial_number": "VCS-12345"
}
```

### GET /records/{id}
Get record details with all events and current status.

### POST /records/{id}/retire
Retire a carbon credit (append RETIRED event).

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   python -m uvicorn main:app --reload
   ```

3. **Test the API**:
   ```bash
   python test_api.py
   ```

4. **View API docs**:
   Open http://127.0.0.1:8000/docs

## Database

- **SQLite** (default): `offset.db` 
- **PostgreSQL**: Set `DATABASE_URL` environment variable

## Architecture

- `models.py`: SQLAlchemy ORM models
- `schemas.py`: Pydantic request/response schemas  
- `routes.py`: FastAPI endpoints and business logic
- `database.py`: DB connection and session management
- `utils.py`: Input canonicalization and ID generation
- `main.py`: FastAPI app with startup hooks

## Data Model

### Records Table
- `id`: Deterministic SHA256 hash (primary key)
- `project_name`, `registry`, `vintage`, `quantity`, `serial_number`
- `created_at`: Timestamp

### Events Table  
- `id`: UUID (primary key)
- `record_id`: Foreign key to records
- `event_type`: CREATED, SOLD, RETIRED
- `payload`: JSON metadata
- `created_at`: Timestamp
- Unique constraint on (record_id, event_type) for RETIRED events

## Concurrency Protection

- Database-level unique constraints
- Transaction isolation
- Append-only event model prevents data races