# Alpaca Data Collector - Docker Image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Poetry
RUN pip install poetry

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install Python dependencies
RUN poetry install --only main --no-dev

# Copy application code
COPY config/ ./config/
COPY ingest/ ./ingest/
COPY *.py ./

# Create necessary directories
RUN mkdir -p logs
RUN mkdir -p /app/financial_data/ohlcv
RUN mkdir -p /app/financial_data/events

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import yaml; print('OK')" || exit 1

# Default command
CMD ["python3", "ingest/orchestrator.py"]
