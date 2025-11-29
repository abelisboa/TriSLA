FROM python:3.10-slim
RUN pip install --no-cache-dir web3 fastapi uvicorn requests

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app
ENV PORT=8083

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \

EXPOSE 8083


