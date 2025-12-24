# Deploy TriSLA v3.7.10 — Guia Completo

**Versão:** 3.7.10  
**Data:** 2025-12-05  
**Status:** ✅ Deployado e Operacional

---

## 📋 Pré-requisitos

### 1. Imagens Docker

Todas as imagens estão disponíveis no GHCR:

- ✅ `ghcr.io/abelisboa/trisla-sem-csmf:3.7.10`
- ✅ `ghcr.io/abelisboa/trisla-ml-nsmf:3.7.10`
- ✅ `ghcr.io/abelisboa/trisla-decision-engine:3.7.10`
- ✅ `ghcr.io/abelisboa/trisla-bc-nssmf:3.7.10`
- ✅ `ghcr.io/abelisboa/trisla-sla-agent-layer:3.7.10`
- ✅ `ghcr.io/abelisboa/trisla-nasp-adapter:3.7.10`
- ✅ `ghcr.io/abelisboa/trisla-ui-dashboard:3.7.10`

**Verificar:**
```bash
# Listar imagens no GHCR
docker pull ghcr.io/abelisboa/trisla-sem-csmf:3.7.10
```

### 2. Helm Values Atualizados

O arquivo `helm/trisla/values-nasp.yaml` já está atualizado com tags `3.7.10`:

```yaml
semCsmf:
  image:
    tag: 3.7.10  # ✅ Atualizado

mlNsmf:
  image:
    tag: 3.7.10  # ✅ Atualizado

decisionEngine:
  image:
    tag: 3.7.10  # ✅ Atualizado

bcNssmf:
  image:
    tag: 3.7.10  # ✅ Atualizado

slaAgentLayer:
  image:
    tag: 3.7.10  # ✅ Atualizado

naspAdapter:
  image:
    tag: 3.7.10  # ✅ Atualizado

uiDashboard:
  image:
    tag: 3.7.10  # ✅ Atualizado
```

### 3. Secret GHCR

**Criar secret no namespace `trisla`:**
```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=abelisboa \
  --docker-password=<GITHUB_TOKEN> \
  --namespace=trisla
```

---

## 🚀 Deploy no NASP

### Passo 1: Validar Helm Chart

```bash
cd ~/gtp5g/trisla

# Validar sintaxe
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml

# Visualizar templates (dry-run)
helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

### Passo 2: Deploy via Helm

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

### Passo 3: Verificar Deploy

```bash
# Verificar pods
kubectl get pods -n trisla

# Verificar se estão usando as imagens corretas
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'

# Verificar serviços
kubectl get svc -n trisla

# Verificar status do Helm release
helm status trisla -n trisla
```

**Status Esperado:**
- ✅ **Helm Release**: Revision 32 (deployed)
- ✅ **Pods**: 14 pods em Running
- ✅ **ServiceMonitors**: 6 configurados
- ✅ **OTEL Collector**: Running

---

## ✅ Validação Pós-Deploy

### 1. Health Checks

```bash
# Testar health endpoint de cada módulo
kubectl exec -n trisla deployment/trisla-sem-csmf -- \
  curl -s http://localhost:8080/health

kubectl exec -n trisla deployment/trisla-ml-nsmf -- \
  curl -s http://localhost:8081/health

kubectl exec -n trisla deployment/trisla-decision-engine -- \
  curl -s http://localhost:8082/health

kubectl exec -n trisla deployment/trisla-bc-nssmf -- \
  curl -s http://localhost:8083/health

kubectl exec -n trisla deployment/trisla-sla-agent-layer -- \
  curl -s http://localhost:8084/health
```

### 2. Métricas Prometheus

```bash
# Verificar métricas expostas
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080
curl http://localhost:8080/metrics | grep trisla_

# Verificar ServiceMonitors
kubectl get servicemonitors -n trisla

# Verificar targets no Prometheus
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
# Acessar: http://localhost:9090/targets
```

### 3. Traces OpenTelemetry

```bash
# Verificar logs de traces
kubectl logs -n trisla deployment/trisla-sem-csmf | grep -i "otlp\|trace"

# Verificar OTEL Collector
kubectl logs -n trisla deployment/trisla-otel-collector

# Verificar status do OTEL Collector
kubectl get pods -n trisla | grep otel
```

### 4. Logs dos Módulos

```bash
# Ver logs de todos os módulos
for deployment in sem-csmf ml-nsmf decision-engine bc-nssmf sla-agent-layer nasp-adapter ui-dashboard; do
  echo "=== trisla-$deployment ==="
  kubectl logs -n trisla deployment/trisla-$deployment --tail=50
done
```

---

## 🔧 Configuração de Observability

### OTLP Endpoint

**OTEL Collector configurado:**
```yaml
env:
  - name: OTLP_ENDPOINT
    value: "http://trisla-otel-collector.trisla.svc.cluster.local:4317"
```

**Status:**
- ✅ **OTEL Collector**: Deployado no namespace `trisla`
- ✅ **Serviço**: `trisla-otel-collector` (ClusterIP, porta 4317)
- ✅ **Versão**: 0.141.0
- ✅ **Status**: Running

### Prometheus Scraping

**ServiceMonitors configurados (6):**
- `trisla-api-backend`
- `trisla-bc-nssmf`
- `trisla-decision-engine`
- `trisla-ml-nsmf`
- `trisla-sem-csmf`
- `trisla-sla-agent-layer`

**Verificar:**
```bash
# Listar ServiceMonitors
kubectl get servicemonitors -n trisla

# Detalhes de um ServiceMonitor
kubectl get servicemonitor trisla-sem-csmf -n trisla -o yaml
```

---

## 📊 Status Atual do Deploy

### Helm Release

- **Release**: `trisla`
- **Namespace**: `trisla`
- **Revision**: 32
- **Status**: ✅ deployed

### Pods em Execução

- **Total**: 14 pods em Running
  - SEM-CSMF: 2 pods
  - ML-NSMF: 2 pods
  - Decision Engine: 3 pods
  - BC-NSSMF: 2 pods
  - SLA-Agent Layer: 2 pods
  - NASP Adapter: 2 pods
  - UI Dashboard: 1 pod
  - OTEL Collector: 1 pod

### ServiceMonitors

- **Total**: 6 ServiceMonitors configurados
- **Status**: ✅ Ativos

### OTEL Collector

- **Deployment**: `trisla-otel-collector`
- **Serviço**: `trisla-otel-collector` (ClusterIP, porta 4317)
- **Status**: ✅ Running
- **Versão**: 0.141.0

### Imagens Deployadas

Todas as imagens estão na versão **3.7.10**:
- `ghcr.io/abelisboa/trisla-sem-csmf:3.7.10`
- `ghcr.io/abelisboa/trisla-ml-nsmf:3.7.10`
- `ghcr.io/abelisboa/trisla-decision-engine:3.7.10`
- `ghcr.io/abelisboa/trisla-bc-nssmf:3.7.10`
- `ghcr.io/abelisboa/trisla-sla-agent-layer:3.7.10`
- `ghcr.io/abelisboa/trisla-nasp-adapter:3.7.10`
- `ghcr.io/abelisboa/trisla-ui-dashboard:3.7.10`

---

## 🐛 Troubleshooting

### Pods em ImagePullBackOff

**Causa:** Secret GHCR não configurado ou token inválido.

**Solução:**
```bash
# Verificar secret
kubectl get secret ghcr-secret -n trisla

# Recriar secret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=abelisboa \
  --docker-password=<GITHUB_TOKEN> \
  --namespace=trisla \
  --dry-run=client -o yaml | kubectl apply -f -

# Reiniciar pods
kubectl delete pods -n trisla -l app.kubernetes.io/name=trisla
```

### Pods em CrashLoopBackOff

**Causa:** Erro na aplicação ou dependências.

**Solução:**
```bash
# Ver logs
kubectl logs -n trisla <pod-name> --previous

# Ver eventos
kubectl describe pod -n trisla <pod-name>

# Verificar variáveis de ambiente
kubectl exec -n trisla <pod-name> -- env | grep -E "OTLP|KAFKA|DATABASE"
```

### Métricas Não Aparecem

**Solução:**
```bash
# Testar endpoint diretamente
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080
curl http://localhost:8080/metrics

# Verificar ServiceMonitor
kubectl get servicemonitors -n trisla

# Verificar targets no Prometheus
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
# Acessar: http://localhost:9090/targets
```

### OTEL Collector Não Recebe Traces

**Solução:**
```bash
# Verificar se OTEL Collector está rodando
kubectl get pods -n trisla | grep otel

# Verificar logs
kubectl logs -n trisla deployment/trisla-otel-collector

# Verificar se serviço existe
kubectl get svc -n trisla | grep otel

# Verificar DNS
kubectl exec -n trisla <pod-name> -- nslookup trisla-otel-collector.trisla.svc.cluster.local
```

---

## 📊 Monitoramento

### Dashboards Grafana

Após o deploy, acesse os dashboards Grafana:

- **TriSLA Overview**: Visão geral de todos os módulos
- **Métricas por Módulo**: Métricas detalhadas de cada módulo
- **Latência das Interfaces**: Latência das interfaces I-01 a I-07
- **Health Status**: Status de saúde de todos os módulos

### Alertas Prometheus

Configure alertas baseados em métricas:

- Latência alta (> 1s)
- Taxa de erro alta (> 5%)
- Health status = 0
- Pods não prontos

---

## 📚 Documentação Relacionada

- **Guia de Deploy NASP**: [`docs/nasp/NASP_DEPLOY_GUIDE.md`](../nasp/NASP_DEPLOY_GUIDE.md)
- **Observability v3.7.10**: [`docs/OBSERVABILITY_v3.7.10.md`](../OBSERVABILITY_v3.7.10.md)
- **Changelog v3.7.10**: [`docs/CHANGELOG_v3.7.10.md`](../CHANGELOG_v3.7.10.md)
- **Relatório Técnico Final**: [`TRISLA_PROMPTS_v3.5/FASE_6_RELATORIO_TECNICO_FINAL.md`](../../TRISLA_PROMPTS_v3.5/FASE_6_RELATORIO_TECNICO_FINAL.md)

---

## ✅ Comandos Úteis

### Status Geral
```bash
# Todos os pods
kubectl get pods -n trisla

# ServiceMonitors
kubectl get servicemonitors -n trisla

# Serviços
kubectl get svc -n trisla

# Helm Release
helm status trisla -n trisla
```

### Logs
```bash
# Logs de um pod específico
kubectl logs -n trisla <pod-name> --tail=50

# Logs de todos os pods de um componente
kubectl logs -n trisla -l component=sem-csmf --tail=50
```

### Métricas
```bash
# Verificar métricas diretamente no pod
kubectl exec -n trisla <pod-name> -- curl -s http://localhost:8080/metrics
```

### Acessar Prometheus
```bash
# Port-forward para Prometheus
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090

# Acessar: http://localhost:9090
# Targets: http://localhost:9090/targets
```

### Acessar Métricas dos Módulos
```bash
# SEM-CSMF
kubectl port-forward -n trisla svc/trisla-sem-csmf 8000:8080
curl http://localhost:8000/metrics

# ML-NSMF
kubectl port-forward -n trisla svc/trisla-ml-nsmf 8001:8081
curl http://localhost:8001/metrics

# Decision Engine
kubectl port-forward -n trisla svc/trisla-decision-engine 8002:8082
curl http://localhost:8002/metrics

# BC-NSSMF
kubectl port-forward -n trisla svc/trisla-bc-nssmf 8003:8083
curl http://localhost:8003/metrics

# SLA-Agent Layer
kubectl port-forward -n trisla svc/trisla-sla-agent-layer 8004:8084
curl http://localhost:8004/metrics
```

### Verificar OTEL Collector
```bash
# Status
kubectl get pods -n trisla | grep otel

# Logs
kubectl logs -n trisla -l app=trisla-otel-collector --tail=50 -f
```

---

**Status:** ✅ Guia completo de deploy v3.7.10

**Última atualização:** 2025-12-05








