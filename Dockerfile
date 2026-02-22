# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies first
RUN pip install --no-cache-dir fastapi uvicorn[standard] httpx python-multipart

# Copy project files
COPY projet_collecte_dechets/ ./projet_collecte_dechets/

# Hugging Face Spaces requires running as a non-root user (UID 1000)
RUN useradd -m -u 1000 user && chown -R user:user /app
USER user

# Hugging Face defaults to 7860
EXPOSE 7860

# Start the server (Uses PORT env var if available, otherwise 7860)
CMD ["sh", "-c", "uvicorn projet_collecte_dechets.webapp.backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
