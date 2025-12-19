FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# This runs the worker process
# If you instead have something like "from queues import worker"
# and run "celery -A queues worker", change CMD accordingly.
CMD ["python", "-m", "app.main"]
