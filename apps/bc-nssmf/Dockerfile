FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y     gcc     g++     make     && rm -rf /var/lib/apt/lists/*

# --- BEGIN SOLC INSTALL ---
# Instalar solc via snap ou download direto (Debian não tem PPA)
RUN apt-get update &&     apt-get install -y curl wget &&     wget -O /tmp/solc-static-linux https://github.com/ethereum/solidity/releases/download/v0.8.24/solc-static-linux &&     chmod +x /tmp/solc-static-linux &&     mv /tmp/solc-static-linux /usr/local/bin/solc &&     solc --version
# --- END SOLC INSTALL ---

# Copiar requirements primeiro (para cache de layers)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
# Garantir que contratos sejam copiados corretamente
COPY src/contracts/ /app/src/contracts/

ENV PYTHONPATH=/app
ENV PORT=8083
ENV KAFKA_ENABLED=false
ENV KAFKA_BROKERS=""

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8083/health')"

EXPOSE 8083

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8083"]
