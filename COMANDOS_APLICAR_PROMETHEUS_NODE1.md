# 🚀 Comandos para Aplicar Prometheus API no node1

## ⚠️ Situação

A API está rodando em **Kubernetes**. Precisamos:
1. Copiar `prometheus.py` para dentro do pod
2. Instalar `httpx` no pod
3. Reiniciar deployment para carregar mudanças

---

## ✅ Execute Estes Comandos no node1 (pasta ~/gtp5g/trisla-portal)

### PASSO 1: Identificar Pod

```bash
# Ver pods do portal
kubectl get pods -n trisla | grep portal

# Salvar nome do pod
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
echo "Pod: $POD_NAME"

# Verificar container (pode ser trisla-backend ou trisla-api)
kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[*].name}'
```

---

### PASSO 2: Copiar Arquivo para o Pod

```bash
# Tentar container trisla-backend primeiro
kubectl cp apps/api/prometheus.py trisla/$POD_NAME:/app/apps/api/prometheus.py -c trisla-backend || \
kubectl cp apps/api/prometheus.py trisla/$POD_NAME:/app/apps/api/prometheus.py -c trisla-api

# Verificar se foi copiado
kubectl exec -n trisla $POD_NAME -c trisla-backend -- ls -la /app/apps/api/prometheus.py || \
kubectl exec -n trisla $POD_NAME -c trisla-api -- ls -la /app/apps/api/prometheus.py
```

---

### PASSO 3: Instalar httpx no Pod

```bash
# Instalar httpx
kubectl exec -n trisla $POD_NAME -c trisla-backend -- pip install httpx || \
kubectl exec -n trisla $POD_NAME -c trisla-api -- pip install httpx

# Verificar instalação
kubectl exec -n trisla $POD_NAME -c trisla-backend -- pip list | grep httpx || \
kubectl exec -n trisla $POD_NAME -c trisla-api -- pip list | grep httpx
```

---

### PASSO 4: Verificar/Copiar main.py Atualizado

```bash
# Verificar se router já está no main.py do pod
kubectl exec -n trisla $POD_NAME -c trisla-backend -- grep -A 3 "prometheus_router" /app/apps/api/main.py || \
kubectl exec -n trisla $POD_NAME -c trisla-api -- grep -A 3 "prometheus_router" /app/apps/api/main.py

# Se não estiver, copiar main.py também
if ! kubectl exec -n trisla $POD_NAME -c trisla-backend -- grep -q "prometheus_router" /app/apps/api/main.py 2>/dev/null; then
    echo "⚠️  Router não encontrado, copiando main.py..."
    kubectl cp apps/api/main.py trisla/$POD_NAME:/app/apps/api/main.py -c trisla-backend || \
    kubectl cp apps/api/main.py trisla/$POD_NAME:/app/apps/api/main.py -c trisla-api
fi
```

---

### PASSO 5: Reiniciar Deployment

```bash
# Encontrar nome do deployment
DEPLOY_NAME=$(kubectl get deployment -n trisla | grep portal | awk '{print $1}')
echo "Deployment: $DEPLOY_NAME"

# Reiniciar
kubectl rollout restart deployment/$DEPLOY_NAME -n trisla

# Aguardar rollout completar
kubectl rollout status deployment/$DEPLOY_NAME -n trisla --timeout=5m
```

---

### PASSO 6: Verificar Logs e Testar

```bash
# Aguardar alguns segundos
sleep 10

# Ver logs
kubectl logs -n trisla -l app=trisla-portal --tail=50 -c trisla-backend | tail -20 || \
kubectl logs -n trisla -l app=trisla-portal --tail=50 -c trisla-api | tail -20

# Testar endpoint via port-forward existente (porta 8092)
curl http://localhost:8092/prometheus/health

# Ou criar novo port-forward
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 &
sleep 3
curl http://localhost:8000/prometheus/health
```

---

## 🔄 Alternativa: Script Automático

Execute tudo de uma vez:

```bash
chmod +x APLICAR_PROMETHEUS_API_KUBERNETES.sh
./APLICAR_PROMETHEUS_API_KUBERNETES.sh
```

---

## ⚠️ Nota sobre PROM_URL

O `values.yaml` tem:
```yaml
PROM_URL: "http://nasp-prometheus.monitoring.svc.cluster.local:9090/api/v1/query"
```

Mas nosso código remove `/api/v1/query` no final. Isso está OK, o código faz `.replace("/api/v1/query", "")`.

Se precisar ajustar, edite:
```bash
# Editar values.yaml local
vim helm/trisla-portal/values.yaml
# Mudar para: PROM_URL: "http://nasp-prometheus.monitoring.svc.cluster.local:9090"

# Aplicar via Helm
helm upgrade --install trisla-portal helm/trisla-portal \
  -n trisla \
  -f docs/config-examples/values-nasp.yaml \
  --set backend.env.PROM_URL="http://nasp-prometheus.monitoring.svc.cluster.local:9090"
```




