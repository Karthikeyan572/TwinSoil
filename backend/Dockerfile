FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PyMuPDF and Tesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/backend/

ENV PYTHONPATH=/app

# Pre-ingest knowledge base and ensure models exist
RUN python -m backend.ml.train_crop_model || true
RUN python -m backend.app.rag.ingestion || true

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
