# Dockerfile
FROM python:3.11.12-slim-bookworm

WORKDIR /app

# System dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Dockerfile (add this above RUN python)
COPY models /app/models
COPY backend/drugbank_data /app/backend/drugbank_data
COPY backend/app /app/backend/app
COPY backend/config /app/backend/config
COPY backend/templates /app/backend/templates
COPY backend/static /app/backend/static
COPY src/utils /app/utils 
COPY src /app/src
COPY run.py .


EXPOSE 8080

# Production entrypoint
CMD ["gunicorn", "run:app", "--bind=0.0.0.0:8080", "--workers=2", "--timeout=600"]
