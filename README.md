# Book Management System

Async REST API for managing books and authors. FastAPI + PostgreSQL + SQLAlchemy 2.0 (async) + Alembic, JWT auth.

## Quick start (Docker)

```bash
docker compose up --build
```

API: http://localhost:8000
Swagger: http://localhost:8000/api/v1/docs · ReDoc: http://localhost:8000/api/v1/redoc

Migrations run automatically on container start.

## Local development

```bash
docker compose up -d db
python -m venv venv && venv\Scripts\activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/books/`
- `POST /api/v1/books/`
- `GET /api/v1/books/{id}`
- `PATCH /api/v1/books/{id}`
- `DELETE /api/v1/books/{id}`
- `POST /api/v1/books/bulk`
- `GET /api/v1/books/export`
- `GET /api/v1/health`

Reads are public; create/update/delete/bulk require a Bearer access token.
