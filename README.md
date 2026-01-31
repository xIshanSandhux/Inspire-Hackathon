# Inspire Hackathon — Document Vault

A digital document vault for vulnerable populations. Users register with a fingerprint and upload ID documents (driver’s license, passport, BC Services Card, BC ID Card). Staff (clinics, shelters, gov) can look up a person by fingerprint and view verified documents. Data is encrypted at rest.

- **Backend:** FastAPI, SQLite, document extraction (Google Document AI or OCR + LLM), Fernet encryption, Clerk + API key auth
- **Frontend:** Next.js — service kiosk (fingerprint → upload docs), gov/admin dashboards (search by fingerprint, view documents)

## Quick start

```bash
make install          # Backend venv + frontend deps
make setup-env       # Copy .env from examples
make run             # Backend :8000, frontend :3000
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Project layout

| Path        | Description                                                                                            |
| ----------- | ------------------------------------------------------------------------------------------------------ |
| `backend/`  | FastAPI app, `core/` (auth, crypto, db, document/LLM services), `features/` (identity, document, auth) |
| `frontend/` | Next.js app — `app/service/dashboard` (kiosk), `app/gov/dashboard`, `app/admin/dashboard`              |
| `Makefile`  | `install`, `run`, `run-backend`, `run-frontend`, `test`, `gen-key`, `setup-env`                        |

## Config

- **Backend:** `backend/.env` — see `backend/example.env`. Set `ENCRYPTION_KEY` (run `make gen-key`), optional Clerk keys and `CLERK_PUBLISHABLE_KEY` for JWT, or `API_KEYS` for service auth. Document AI: `GCP_PROJECT_ID`, `DOCUMENT_AI_PROCESSOR_ID`.
- **Frontend:** `frontend/.env.local` — `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Tests

```bash
make test             # Backend pytest
```

---

# Presentation link

https://docs.google.com/presentation/d/1tD6U19FRvFxaWvYWLvJNTvwJ6LIIs2Dozox-dK9dIM4/edit?usp=sharing
