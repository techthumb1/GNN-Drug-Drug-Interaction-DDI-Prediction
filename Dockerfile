# syntax=docker/dockerfile:1.4

# --- Stage 1: Base environment with dependencies ---
FROM python:3.12.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/src

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy only requirements for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final image with app code ---
FROM base AS final

WORKDIR /app

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 5050

# Entry point to start the app
CMD ["python", "run.py"]
