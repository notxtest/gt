FROM python:3.10-alpine
WORKDIR /app
COPY . /app

# Alpine mein build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
