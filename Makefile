# Fingerprint Identity Blockchain System
# Makefile for easy project management

.PHONY: help run run-docker build clean test verify shell db-stats

# Default target
help:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║     🔐 Fingerprint Identity Blockchain System                 ║"
	@echo "╠══════════════════════════════════════════════════════════════╣"
	@echo "║  Available commands:                                          ║"
	@echo "║                                                               ║"
	@echo "║  Local Development:                                           ║"
	@echo "║    make run          - Run the application locally            ║"
	@echo "║    make run-quick    - Quick register mode (one fingerprint)  ║"
	@echo "║    make test         - Run tests                              ║"
	@echo "║                                                               ║"
	@echo "║  Docker:                                                      ║"
	@echo "║    make build        - Build Docker image                     ║"
	@echo "║    make run-docker   - Run in Docker container                ║"
	@echo "║    make shell        - Open shell in Docker container         ║"
	@echo "║    make stop         - Stop Docker container                  ║"
	@echo "║    make logs         - View Docker container logs             ║"
	@echo "║                                                               ║"
	@echo "║  Maintenance:                                                 ║"
	@echo "║    make clean        - Remove database and cache files        ║"
	@echo "║    make clean-docker - Remove Docker containers and images    ║"
	@echo "║    make verify       - Verify blockchain integrity            ║"
	@echo "║    make db-stats     - Show database statistics               ║"
	@echo "║                                                               ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"

# ============================================
# Local Development
# ============================================

# Run the application locally
run:
	@echo "🚀 Starting Fingerprint Blockchain System..."
	python3 main.py

# Run in quick register mode
run-quick:
	@echo "🚀 Quick register mode..."
	python3 main.py --register

# Run with custom difficulty (for testing)
run-easy:
	@echo "🚀 Running with low difficulty (fast mining)..."
	python3 main.py --difficulty 1

run-hard:
	@echo "🚀 Running with high difficulty (slow but secure)..."
	python3 main.py --difficulty 4

# Run basic tests
test:
	@echo "🧪 Running tests..."
	python3 -c "\
from blockchain import Blockchain, Block; \
from database import Database; \
import tempfile; \
import os; \
print('Testing Blockchain...'); \
bc = Blockchain(difficulty=1); \
bc.initialize_chain(); \
assert len(bc.chain) == 1, 'Genesis block failed'; \
print('  ✅ Genesis block created'); \
bc.add_fingerprint_record('test_hash', ['ID001', 'ID002']); \
assert len(bc.chain) == 2, 'Block addition failed'; \
print('  ✅ Block added successfully'); \
assert bc.is_chain_valid(), 'Chain validation failed'; \
print('  ✅ Chain validation passed'); \
print('Testing Database...'); \
db = Database(':memory:'); \
db.save_block(bc.chain[0].to_dict()); \
db.save_block(bc.chain[1].to_dict()); \
loaded = db.load_all_blocks(); \
assert len(loaded) == 2, 'Database load failed'; \
print('  ✅ Database save/load passed'); \
records = db.get_fingerprint_records(); \
assert len(records) == 1, 'Record query failed'; \
print('  ✅ Record queries passed'); \
print(''); \
print('✅ All tests passed!'); \
"

# ============================================
# Docker Commands
# ============================================

# Build Docker image
build:
	@echo "🐳 Building Docker image..."
	docker-compose build

# Run in Docker (interactive mode)
run-docker:
	@echo "🐳 Running in Docker container..."
	docker-compose run --rm fingerprint-blockchain

# Start Docker container in background
start:
	@echo "🐳 Starting Docker container in background..."
	docker-compose up -d

# Stop Docker container
stop:
	@echo "🛑 Stopping Docker container..."
	docker-compose down

# View Docker logs
logs:
	docker-compose logs -f

# Open shell in Docker container
shell:
	@echo "🐚 Opening shell in Docker container..."
	docker-compose run --rm fingerprint-blockchain /bin/bash

# ============================================
# Maintenance
# ============================================

# Verify blockchain integrity
verify:
	@echo "🔍 Verifying blockchain integrity..."
	python3 -c "\
from main import FingerprintApp; \
app = FingerprintApp(); \
app.verify_blockchain(); \
app.close(); \
"

# Show database statistics
db-stats:
	@echo "📊 Database statistics..."
	python3 -c "\
from main import FingerprintApp; \
app = FingerprintApp(); \
app.show_statistics(); \
app.close(); \
"

# View database schema
db-schema:
	@echo "📋 Database schema..."
	python3 database.py

# Clean local files
clean:
	@echo "🧹 Cleaning up..."
	rm -f *.db
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Cleaned!"

# Clean Docker resources
clean-docker:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down -v --rmi local
	@echo "✅ Docker resources cleaned!"

# Full clean
clean-all: clean clean-docker
	@echo "✅ All cleaned!"

# ============================================
# Development Helpers
# ============================================

# Show blockchain contents
show-chain:
	python3 -c "\
from main import FingerprintApp; \
app = FingerprintApp(); \
app.show_blockchain(); \
app.close(); \
"

# Show all records
show-records:
	python3 -c "\
from main import FingerprintApp; \
app = FingerprintApp(); \
app.show_all_records(); \
app.close(); \
"

# Export blockchain to JSON
export:
	@echo "📤 Exporting blockchain to blockchain_export.json..."
	python3 -c "\
from main import FingerprintApp; \
app = FingerprintApp(); \
with open('blockchain_export.json', 'w') as f: \
    f.write(app.blockchain.to_json()); \
print('✅ Exported to blockchain_export.json'); \
app.close(); \
"
