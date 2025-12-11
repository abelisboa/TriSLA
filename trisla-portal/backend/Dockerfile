# Backend Dockerfile - Portal TriSLA
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Variáveis de ambiente padrão para módulos NASP
# Podem ser sobrescritas via Helm values.yaml
ENV SEM_CSMF_URL=http://trisla-sem-csmf:8080
ENV ML_NSMF_URL=http://trisla-ml-nsmf:8081
ENV DECISION_ENGINE_URL=http://trisla-decision-engine:8082
ENV BC_NSSMF_URL=http://trisla-bc-nssmf:8083
ENV SLA_AGENT_URL=http://trisla-sla-agent-layer:8084

# OTLP desabilitado por padrão
ENV OTEL_SDK_DISABLED=true

# Expor porta
EXPOSE 8001

# Comando para iniciar o servidor
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]

