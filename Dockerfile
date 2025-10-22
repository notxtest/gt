########################################
# Start from a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install build dependencies for tgcrypto
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . /app

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Environment variable to force unbuffered output (helps in logging)
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
