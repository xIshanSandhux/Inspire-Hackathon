# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy application files
COPY blockchain.py database.py main.py requirements.txt ./

# Install dependencies (none required for this app, but keeping for future)
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true

# Create data directory for persistent storage
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set the data directory as a volume mount point
VOLUME ["/app/data"]

# Default command runs the interactive app
CMD ["python", "main.py", "--db", "/app/data/fingerprint_blockchain.db"]
