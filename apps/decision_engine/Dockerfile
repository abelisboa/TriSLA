# TriSLA Decision Engine - Dockerfile
# Motor de decisão central da arquitetura TriSLA

FROM python:3.11-slim

# Metadados
LABEL maintainer="abelisboa@unisinos.br"
LABEL description="TriSLA Decision Engine - Central Decision Engine"
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
ENV DECISION_ENGINE_PORT=8080
ENV GRPC_PORT=50051

# Expor portas
EXPOSE 8080 50051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Comando de inicialização
CMD ["python", "main.py"]

