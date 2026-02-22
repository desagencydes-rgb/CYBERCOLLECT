# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY projet_collecte_dechets/ ./projet_collecte_dechets/

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn[standard] httpx python-multipart

# Expose port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "projet_collecte_dechets.webapp.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
