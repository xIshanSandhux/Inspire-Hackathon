# Inspire Hackathon - Development Commands
# ========================================

.PHONY: help install install-backend install-frontend run run-backend run-frontend test setup-env

# Python venv path
VENV := backend/.venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "  Setup:"
	@echo "    make install          - Install all dependencies (backend + frontend)"
	@echo "    make install-backend  - Create venv and install Python backend dependencies"
	@echo "    make install-frontend - Install Node.js frontend dependencies"
	@echo "    make setup-env        - Create .env files from examples"
	@echo ""
	@echo "  Run:"
	@echo "    make run              - Run both backend and frontend (in parallel)"
	@echo "    make run-backend      - Run the FastAPI backend server"
	@echo "    make run-frontend     - Run the Next.js frontend dev server"
	@echo ""
	@echo "  Test:"
	@echo "    make test             - Run backend tests"
	@echo "    make test-backend     - Run backend tests"
	@echo ""
	@echo "  Utils:"
	@echo "    make gen-key          - Generate a new Fernet encryption key"
	@echo "    make clean            - Clean up generated files"

# ========================================
# Installation
# ========================================

install: install-backend install-frontend
	@echo "✅ All dependencies installed!"

# Create venv if it doesn't exist
$(VENV)/bin/activate:
	@echo "🐍 Creating Python virtual environment..."
	python3 -m venv $(VENV)

install-backend: $(VENV)/bin/activate
	@echo "📦 Installing backend dependencies in venv..."
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt
	@echo "✅ Backend installed in $(VENV)"

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && pnpm install

# ========================================
# Environment Setup
# ========================================

setup-env:
	@echo "🔧 Setting up environment files..."
	@if [ ! -f backend/.env ]; then \
		cp backend/example.env backend/.env; \
		echo "✅ Created backend/.env from example.env"; \
		echo "⚠️  Please edit backend/.env and add your API keys!"; \
	else \
		echo "ℹ️  backend/.env already exists, skipping..."; \
	fi
	@if [ ! -f frontend/.env.local ]; then \
		echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local; \
		echo "✅ Created frontend/.env.local"; \
	else \
		echo "ℹ️  frontend/.env.local already exists, skipping..."; \
	fi

gen-key:
	@echo "🔑 Generating Fernet encryption key..."
	@$(PYTHON) -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# ========================================
# Running Services
# ========================================

run: 
	@echo "🚀 Starting both backend and frontend..."
	@echo "   Backend will run on: http://localhost:8000"
	@echo "   Frontend will run on: http://localhost:3000"
	@echo ""
	@make -j2 run-backend run-frontend

run-backend:
	@echo "🐍 Starting FastAPI backend on http://localhost:8000..."
	$(VENV)/bin/python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "⚛️  Starting Next.js frontend on http://localhost:3000..."
	cd frontend && pnpm dev

# ========================================
# Testing
# ========================================

test: test-backend

test-backend:
	@echo "🧪 Running backend tests..."
	$(VENV)/bin/python -m pytest backend -v

# ========================================
# Cleanup
# ========================================

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"

clean-venv:
	@echo "🧹 Removing Python virtual environment..."
	rm -rf $(VENV)
	@echo "✅ Virtual environment removed!"
