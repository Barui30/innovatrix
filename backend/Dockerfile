# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system deps for PDF/DOCX parsing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
