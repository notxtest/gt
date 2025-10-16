########################################
# Start from a lightweight Python image
FROM python:3.10-slim
WORKDIR /app
COPY . /app

# Install build dependencies FIRST
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Environment variable to force unbuffered output (helps in logging)
ENV PYTHONUNBUFFERED=1

# Run the bot..
CMD ["python", "main.py"]
