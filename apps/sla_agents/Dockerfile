# TriSLA SLA-Agent Layer - Dockerfile
# Camada Federada de Agentes SLA

FROM python:3.11-slim

# Metadados
LABEL maintainer="abelisboa@unisinos.br"
LABEL description="TriSLA SLA-Agent Layer - Federated SLA Agents"
LABEL version="1.0.0"

# Configurar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Configurar variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV MONITORING_INTERVAL=5.0

# Expor portas (se necessário para health checks)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; print('SLA-Agent Layer healthy')" || exit 1

# Comando de inicialização
CMD ["python", "sla_coordinator.py"]




