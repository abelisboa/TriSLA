# Infraestrutura - TriSLA Observability Portal v4.0

Configurações de Docker, Docker Compose e Helm Charts.

## 🐳 Docker

### Build

```bash
# Frontend
docker build -f infra/Dockerfile.frontend -t trisla-portal-frontend:4.0.0 ..

# Backend
docker build -f infra/Dockerfile.backend -t trisla-portal-backend:4.0.0 ..
```

## 🚀 Docker Compose (Local)

```bash
cd infra
docker-compose up -d
```

Acesse:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Prometheus: http://localhost:9090
- Loki: http://localhost:3100
- Tempo: http://localhost:3200

## ☸️ Helm (NASP/Kubernetes)

### Instalação

```bash
# Adicionar repositório (se aplicável)
helm repo add trisla-portal ./infra/helm/trisla-portal

# Instalar
helm install trisla-portal ./infra/helm/trisla-portal \
  --namespace trisla \
  --create-namespace \
  --set database.type=postgresql \
  --set database.postgresql.host=postgresql.trisla.svc.cluster.local
```

### Atualização

```bash
helm upgrade trisla-portal ./infra/helm/trisla-portal \
  --namespace trisla
```

### Desinstalação

```bash
helm uninstall trisla-portal --namespace trisla
```

## 📋 Componentes

### Deployments
- `trisla-portal-frontend` - Frontend Next.js
- `trisla-portal-backend` - Backend FastAPI

### Services
- `trisla-portal-frontend` - ClusterIP na porta 3000
- `trisla-portal-backend` - ClusterIP na porta 8000

### ServiceMonitor
- Configurado para descoberta automática pelo Prometheus
- Scraping de `/metrics` do backend

### PrometheusRules
- Alertas para backend/frontend down
- Alertas para alta latência
- Alertas para alta taxa de erro

### Ingress
- Configurado para expor o frontend
- Suporte a TLS via cert-manager

## 🔧 Configurações

### Variáveis de Ambiente

O backend requer as seguintes variáveis:
- `DATABASE_URL` - URL do banco de dados
- `REDIS_URL` - URL do Redis
- `PROMETHEUS_URL` - URL do Prometheus
- `LOKI_URL` - URL do Loki
- `TEMPO_URL` - URL do Tempo
- `OTEL_EXPORTER_OTLP_ENDPOINT` - Endpoint OTEL Collector
- URLs dos módulos TriSLA

### Volumes

- `data` - Dados do backend (SQLite, se usado)

## 📝 Notas

- ServiceMonitors requerem Prometheus Operator
- PrometheusRules requerem Prometheus Operator
- Ingress requer Ingress Controller (nginx, traefik, etc.)
- Para produção, use PostgreSQL ao invés de SQLite







