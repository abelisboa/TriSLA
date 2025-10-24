FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt

# Instalar curl e dependências antes do pip
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
