# Deploy TriSLA v3.7.9 — guide Completo

**Versão:** 3.7.9  
**Data:** 2025-01-XX  
**Status:** ✅ Pronto for Deploy

---

## 📋 Pré-requisitos

### 1. Imagens Docker

Todas as imagens devem estar disponíveis no GHCR:

- ✅ `ghcr.io/abelisboa/trisla-sem-csmf:3.7.9`
- ✅ `ghcr.io/abelisboa/trisla-ml-nsmf:3.7.9`
- ✅ `ghcr.io/abelisboa/trisla-decision-engine:3.7.9`
- ✅ `ghcr.io/abelisboa/trisla-bc-nssmf:3.7.9`
- ✅ `ghcr.io/abelisboa/trisla-sla-agent-layer:3.7.9`

**verify:**
```bash
# Listar imagens no GHCR
docker pull ghcr.io/abelisboa/trisla-sem-csmf:3.7.9
```

### 2. Helm Values Atualizados

O arquivo `helm/trisla/values-nasp.yaml` já está atualizado com tags `3.7.9`:

```yaml
semCsmf:
  image:
    tag: 3.7.9  # ✅ Atualizado

mlNsmf:
  image:
    tag: 3.7.9  # ✅ Atualizado

decisionEngine:
  image:
    tag: 3.7.9  # ✅ Atualizado

bcNssmf:
  image:
    tag: 3.7.9  # ✅ Atualizado

slaAgentLayer:
  image:
    tag: 3.7.9  # ✅ Atualizado
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

### Passo 3: verify Deploy

```bash
# verify pods
kubectl get pods -n trisla

# verify se estão usando as imagens corretas
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'

# verify serviços
kubectl get svc -n trisla

# verify status of Helm release
helm status trisla -n trisla
```

---

## ✅ validation Pós-Deploy

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

### 2. metrics Prometheus

```bash
# verify metrics expostas
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080
curl http://localhost:8080/metrics | grep trisla_
```

### 3. Traces OpenTelemetry

```bash
# verify logs de traces
kubectl logs -n trisla deployment/trisla-sem-csmf | grep -i "otlp\|trace"

# verify OTLP Collector (se configurado)
kubectl logs -n monitoring deployment/otel-collector
```

### 4. Logs dos Módulos

```bash
# Ver logs de todos os módulos
for deployment in sem-csmf ml-nsmf decision-engine bc-nssmf sla-agent-layer; do
  echo "=== trisla-$deployment ==="
  kubectl logs -n trisla deployment/trisla-$deployment --tail=50
done
```

---

## 🔧 Configuração de Observability

### OTLP Endpoint

**Se OTLP Collector estiver configurado:**
```yaml
env:
  - name: OTLP_ENDPOINT
    value: "http://otel-collector.monitoring.svc.cluster.local:4317"
```

**Se OTLP estiver desabilitado:**
```yaml
env:
  - name: OTLP_ENABLED
    value: "false"
```

### Prometheus Scraping

**ServiceMonitor (se Prometheus Operator estiver instalado):**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: trisla
  namespace: trisla
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: trisla
  endpoints:
    - port: http
      path: /metrics
```

---

## 🐛 Troubleshooting

### Pods in ImagePullBackOff

**Causa:** Secret GHCR não configurado ou token inválido.

**solution:**
```bash
# verify secret
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

### Pods in CrashLoopBackOff

**Causa:** error na aplicação ou dependências.

**solution:**
```bash
# Ver logs
kubectl logs -n trisla <pod-name> --previous

# Ver eventos
kubectl describe pod -n trisla <pod-name>

# verify variables de environment
kubectl exec -n trisla <pod-name> -- env | grep -E "OTLP|KAFKA|DATABASE"
```

### metrics Não Aparecem

**solution:**
```bash
# Testar endpoint diretamente
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080
curl http://localhost:8080/metrics

# verify ServiceMonitor
kubectl get servicemonitor -n trisla

# verify targets no Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Acessar: http://localhost:9090/targets
```

---

## 📊 Monitoramento

### Dashboards Grafana

Após o deploy, acesse os dashboards Grafana:

- **TriSLA Overview**: Visão geral de todos os módulos
- **metrics por Módulo**: metrics detalhadas de cada módulo
- **Latência das Interfaces**: Latência das interfaces I-01 a I-07
- **Health Status**: Status de saúde de todos os módulos

### Alertas Prometheus

Configure alertas baseados in metrics:

- Latência alta (> 1s)
- Taxa de error alta (> 5%)
- Health status = 0
- Pods não prontos

---

## 📚 Documentação Relacionada

- **guide de Deploy NASP**: [`docs/nasp/NASP_DEPLOY_GUIDE.md`](../nasp/NASP_DEPLOY_GUIDE.md)
- **Observability v3.7.9**: [`docs/OBSERVABILITY_v3.7.9.md`](../OBSERVABILITY_v3.7.9.md)
- **validation Build**: [`VALIDACAO_BUILD_3.7.9_PROXIMOS_PASSOS.md`](../../VALIDACAO_BUILD_3.7.9_PROXIMOS_PASSOS.md)
- **Atualização Helm**: [`ATUALIZACAO_HELM_VALUES_3.7.9.md`](../../ATUALIZACAO_HELM_VALUES_3.7.9.md)

---

**Status:** ✅ guide completo de deploy v3.7.9














