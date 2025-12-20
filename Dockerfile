FROM python:3.11-slim

WORKDIR /app

# System dependencies (if needed for cryptography, PIL, etc.)
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY . .

# Ensure Python can import app.*
ENV PYTHONPATH=/app

# 🚀 START THE WORKER (THIS IS THE KEY)
CMD ["sh", "-c", "rq worker --url $REDIS_URL imports"]
