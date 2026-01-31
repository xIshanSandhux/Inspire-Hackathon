# Backend

FastAPI backend for the Inspire Hackathon document vaulting system.

## Structure

```
/backend
├── main.py              # Application entry point
├── router.py            # Aggregates all feature routers
├── requirements.txt     # Python dependencies
├── example.env          # Environment template
├── .env                 # Local environment (git ignored)
├── /core
│   ├── util.py          # Reusable utilities
│   ├── /config
│   │   └── settings.py  # Pydantic settings
│   ├── /db
│   │   ├── base.py      # SQLAlchemy declarative base
│   │   ├── engine.py    # Engine and session factory
│   │   ├── init_db.py   # Database initialization
│   │   └── dependencies.py  # FastAPI DB dependency
│   └── /auth
│       └── dependencies.py  # Auth dependencies (placeholder)
└── /features
    └── (feature modules go here)
```

## Setup

1. Create virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment file:

   ```bash
   cp example.env .env
   ```

4. Run the server (SQLite database file is created automatically):

   ```bash
   # From project root
   uvicorn backend.main:app --reload

   # Or directly
   python -m backend.main
   ```

## API Endpoints

- `GET /health` - Health check
- More endpoints will be added in `/features`

## Adding Features

Create a new feature module in `/features`:

```
/features/identity
├── __init__.py
├── models.py    # SQLAlchemy models
├── schemas.py   # Pydantic schemas
├── router.py    # FastAPI router
└── service.py   # Business logic
```

Then register the router in `/backend/router.py`.

## Database

Using SQLAlchemy 2.0 with SQLite. Models inherit from `backend.core.db.Base`.
The database file (`inspire.db`) is created automatically on first run.

To add a new model:

1. Create model in feature's `models.py`
2. Import it in `backend/core/db/init_db.py`
3. Tables are auto-created on startup

## Configuration

Settings are loaded from environment variables via Pydantic Settings.
See `core/config/settings.py` for available options.
