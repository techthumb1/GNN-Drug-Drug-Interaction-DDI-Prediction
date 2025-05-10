# syntax=docker/dockerfile:1.4

# --- Stage 1: Base environment with dependencies ---
    FROM python:3.12.10-slim AS base


    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        && rm -rf /var/lib/apt/lists/*
    
    # Upgrade pip and install poetry or pip-tools optionally
    RUN pip install --upgrade pip
    
    # Copy only requirements first to leverage layer caching
    COPY requirements.txt .
    
    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements.txt
    
    # --- Stage 2: Application code copy ---
    FROM base AS final
    
    WORKDIR /app
    
    # Copy rest of the application (after installing deps for better caching)
    COPY . .
    
    # Add this to fix module path resolution
    ENV PYTHONPATH=/app

    # Expose port
    EXPOSE 5050
    
    # Entry point
    CMD ["python", "backend/app.py"]
    