FROM python:3.9-slim

# Ye line add karo - build tools install karne ke liye
RUN apt-get update && apt-get install -y gcc g++

WORKDIR /app
COPY repo /app
RUN if [ -f "/app/requirements.txt" ]; then pip install --no-cache-dir -r /app/requirements.txt; fi
