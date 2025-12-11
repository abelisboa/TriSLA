# Guia de Deploy - TriSLA Observability Portal v4.0

**Versão:** 4.0  
**Data:** 2025-01-XX

---

## 📋 Sumário

1. [Pré-requisitos](#pré-requisitos)
2. [Deploy Local (Docker Compose)](#deploy-local)
3. [Deploy NASP (Helm Charts)](#deploy-nasp)
4. [Configuração](#configuração)
5. [Validação](#validação)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Local

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM disponível
- 10GB espaço em disco

### NASP

- Kubernetes 1.26+
- Helm 3.14+
- Acesso ao cluster NASP
- Namespace `trisla` criado
- Prometheus Operator instalado (opcional)

---

## 🐳 Deploy Local (Docker Compose)

### 1. Preparação

```bash
cd trisla-portal/infra
```

### 2. Configuração

Criar arquivo `.env` (opcional, valores padrão funcionam):

```bash
# .env
DATABASE_URL=sqlite:///./data/trisla_portal.db
REDIS_URL=redis://redis:6379/0
PROMETHEUS_URL=http://prometheus:9090
LOKI_URL=http://loki:3100
TEMPO_URL=http://tempo:3200
```

### 3. Build e Deploy

```bash
# Build e iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

### 4. Acessar

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100
- **Tempo**: http://localhost:3200

### 5. Parar Serviços

```bash
docker-compose down

# Remover volumes (cuidado!)
docker-compose down -v
```

---

## ☸️ Deploy NASP (Helm Charts)

### 1. Preparação

```bash
# Verificar acesso ao cluster
kubectl cluster-info

# Criar namespace (se não existir)
kubectl create namespace trisla
```

### 2. Configurar Secrets

```bash
# Secret para PostgreSQL (se usando)
kubectl create secret generic trisla-portal-db-secret \
  --from-literal=password=your-password \
  -n trisla

# Secret para imagens GHCR (se privado)
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=your-username \
  --docker-password=your-token \
  -n trisla
```

### 3. Instalar Helm Chart

```bash
cd trisla-portal/infra/helm/trisla-portal

# Instalar
helm install trisla-portal . \
  --namespace trisla \
  --create-namespace \
  --set database.type=postgresql \
  --set database.postgresql.host=postgresql.trisla.svc.cluster.local \
  --set observability.prometheus.url=http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
```

### 4. Verificar Deploy

```bash
# Verificar pods
kubectl get pods -n trisla -l app.kubernetes.io/name=trisla-portal

# Verificar services
kubectl get svc -n trisla -l app.kubernetes.io/name=trisla-portal

# Verificar ingress
kubectl get ingress -n trisla

# Ver logs
kubectl logs -n trisla -l component=backend --tail=50 -f
```

### 5. Atualizar Deploy

```bash
helm upgrade trisla-portal . \
  --namespace trisla \
  --set image.backend.tag=4.0.1
```

### 6. Desinstalar

```bash
helm uninstall trisla-portal --namespace trisla
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (Backend)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL do banco de dados | `sqlite:///./trisla_portal.db` |
| `REDIS_URL` | URL do Redis | `redis://localhost:6379/0` |
| `PROMETHEUS_URL` | URL do Prometheus | - |
| `LOKI_URL` | URL do Loki | - |
| `TEMPO_URL` | URL do Tempo | - |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Endpoint OTEL Collector | - |
| `TRISLA_SEM_CSMF_URL` | URL do SEM-CSMF | - |
| `TRISLA_ML_NSMF_URL` | URL do ML-NSMF | - |
| `TRISLA_DECISION_ENGINE_URL` | URL do Decision Engine | - |
| `TRISLA_BC_NSSMF_URL` | URL do BC-NSSMF | - |
| `TRISLA_SLA_AGENT_LAYER_URL` | URL do SLA-Agent Layer | - |
| `TRISLA_NASP_ADAPTER_URL` | URL do NASP Adapter | - |

### Variáveis de Ambiente (Frontend)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `NEXT_PUBLIC_API_URL` | URL da API backend | `http://localhost:8000` |

---

## ✅ Validação

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# API endpoints
curl http://localhost:8000/api/v1/health/global
curl http://localhost:8000/api/v1/modules
```

### Verificar Integrações

```bash
# Prometheus
curl http://localhost:8000/api/v1/prometheus/targets

# Contracts
curl http://localhost:8000/api/v1/contracts

# SLAs
curl http://localhost:8000/api/v1/slas/templates
```

---

## 🔧 Troubleshooting

### Problema: Backend não inicia

**Solução:**
```bash
# Verificar logs
docker-compose logs backend

# Verificar variáveis de ambiente
docker-compose exec backend env | grep DATABASE_URL
```

### Problema: Frontend não conecta ao backend

**Solução:**
```bash
# Verificar NEXT_PUBLIC_API_URL
docker-compose exec frontend env | grep NEXT_PUBLIC_API_URL

# Verificar conectividade
docker-compose exec frontend wget -O- http://backend:8000/health
```

### Problema: Prometheus não coleta métricas

**Solução:**
```bash
# Verificar ServiceMonitor
kubectl get servicemonitor -n trisla

# Verificar Prometheus targets
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
# Acessar http://localhost:9090/targets
```

### Problema: Banco de dados não conecta

**Solução:**
```bash
# Verificar conexão PostgreSQL
kubectl exec -n trisla <backend-pod> -- psql $DATABASE_URL -c "SELECT 1"

# Verificar secret
kubectl get secret trisla-portal-db-secret -n trisla
```

---

## ✅ Conclusão

O guia de deploy do TriSLA Observability Portal v4.0 fornece:

- **Deploy local** completo via Docker Compose
- **Deploy NASP** via Helm Charts
- **Configuração** detalhada de variáveis
- **Validação** de deploy
- **Troubleshooting** de problemas comuns

---

**Status:** ✅ **GUIA DE DEPLOY DOCUMENTADO**







