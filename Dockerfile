FROM python:3.9-slim

WORKDIR /app

COPY repo /app

# Install gcc and required build dependencies before installing Python packages
RUN apt-get update && \
    apt-get install -y gcc python3-dev musl-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN if [ -f "/app/requirements.txt" ]; then \
        pip install --no-cache-dir -r /app/requirements.txt; \
    fi

CMD ["python", "main.py"]
