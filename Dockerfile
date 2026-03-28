FROM python:3.11-slim

WORKDIR /app

# Install Node.js for building the frontend
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install slim Python dependencies (no torch/sentence-transformers)
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Build frontend
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci --production=false

COPY frontend/ frontend/
RUN cd frontend && npm run build && rm -rf node_modules

# Copy backend code
COPY app/ app/
COPY rag/ rag/

# Create data directory
RUN mkdir -p data/uploads

ENV PORT=8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
