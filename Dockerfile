FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Requirements install
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
