# Multi-stage Dockerfile for Phase 2

FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# =============================================================================
# API Stage
# =============================================================================
FROM base AS api

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Worker Stage
# =============================================================================
FROM base AS worker

CMD ["python", "workers/message_processor.py"]
