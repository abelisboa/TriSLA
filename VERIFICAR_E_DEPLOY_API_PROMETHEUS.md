# 🔍 Verificar e Deploy API Prometheus no Kubernetes

## ⚠️ Situação Atual

- ✅ `prometheus.py` criado (119 linhas)
- ✅ Router adicionado ao `main.py`
- ❌ API não responde (conexão fechada)
- ℹ️ API parece estar rodando em **Kubernetes**

---

## 🔧 PASSO 1: Verificar Deploy Atual

Execute no node1:

```bash
# Verificar pods do trisla-portal
kubectl get pods -n trisla | grep portal

# Verificar serviços
kubectl get svc -n trisla | grep portal

# Verificar deployments
kubectl get deployment -n trisla | grep portal

# Ver logs do backend
kubectl logs -n trisla -l app=trisla-portal-backend --tail=50

# Verificar se prometheus.py existe no pod
kubectl exec -n trisla -l app=trisla-portal-backend -- ls -la /app/apps/api/ | grep prometheus
```

---

## 📦 PASSO 2: Opções para Atualizar Código

### Opção A: Atualizar Direto no Pod (Teste Rápido)

```bash
# Copiar arquivo para dentro do pod
POD_NAME=$(kubectl get pods -n trisla -l app=trisla-portal-backend -o jsonpath='{.items[0].metadata.name}')
echo "Pod: $POD_NAME"

# Copiar prometheus.py
kubectl cp apps/api/prometheus.py trisla/$POD_NAME:/app/apps/api/prometheus.py

# Reiniciar pod (para carregar novo código)
kubectl rollout restart deployment/trisla-portal-backend -n trisla

# Aguardar reiniciar
kubectl rollout status deployment/trisla-portal-backend -n trisla

# Ver logs
kubectl logs -n trisla -l app=trisla-portal-backend --tail=50 | grep -i prometheus
```

### Opção B: Rebuild Imagem (Recomendado para Produção)

```bash
# 1. Commit mudanças no código (se git disponível)
cd ~/gtp5g/trisla-portal
git add apps/api/prometheus.py apps/api/main.py
git commit -m "Add Prometheus API endpoint"

# 2. Build e push nova imagem
docker build -t ghcr.io/abelisboa/trisla-api:prometheus -f Dockerfile.api .
docker push ghcr.io/abelisboa/trisla-api:prometheus

# 3. Atualizar deployment
kubectl set image deployment/trisla-portal-backend \
  backend=ghcr.io/abelisboa/trisla-api:prometheus \
  -n trisla

# 4. Aguardar rollout
kubectl rollout status deployment/trisla-portal-backend -n trisla
```

### Opção C: Atualizar via Helm (Melhor Prática)

```bash
# Se usa Helm (parece que sim, pelo processo helm):
cd ~/gtp5g/trisla-portal

# Atualizar values.yaml ou usar --set
helm upgrade --install trisla-portal \
  helm/trisla-portal \
  -n trisla \
  -f docs/config-examples/values-nasp.yaml \
  --set backend.image="ghcr.io/abelisboa/trisla-api:latest" \
  --set backend.pullPolicy="Always" \
  --atomic \
  --wait \
  --timeout 10m
```

---

## ✅ PASSO 3: Testar Endpoint

```bash
# Via kubectl port-forward (já está rodando na 8092)
curl http://localhost:8092/prometheus/health

# Ou criar novo port-forward na 8000
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 &
sleep 3
curl http://localhost:8000/prometheus/health

# Via serviço diretamente (se dentro do cluster)
curl http://trisla-portal.trisla.svc.cluster.local:8000/prometheus/health
```

---

## 🐛 Debug: Verificar Erros

```bash
# Ver logs detalhados
kubectl logs -n trisla -l app=trisla-portal-backend --tail=100

# Verificar se httpx está instalado no container
kubectl exec -n trisla -l app=trisla-portal-backend -- pip list | grep httpx

# Se não estiver, instalar:
kubectl exec -n trisla -l app=trisla-portal-backend -- pip install httpx

# Verificar se main.py importa prometheus_router
kubectl exec -n trisla -l app=trisla-portal-backend -- grep -A 5 "prometheus_router" /app/apps/api/main.py
```

---

## 📋 Resumo Comandos Rápidos

```bash
# 1. Verificar pods
kubectl get pods -n trisla | grep portal

# 2. Copiar arquivo para pod (Opção A)
POD=$(kubectl get pods -n trisla -l app=trisla-portal-backend -o jsonpath='{.items[0].metadata.name}')
kubectl cp apps/api/prometheus.py trisla/$POD:/app/apps/api/prometheus.py

# 3. Instalar httpx no pod
kubectl exec -n trisla $POD -- pip install httpx

# 4. Reiniciar deployment
kubectl rollout restart deployment/trisla-portal-backend -n trisla

# 5. Aguardar e testar
kubectl rollout status deployment/trisla-portal-backend -n trisla
sleep 10
curl http://localhost:8092/prometheus/health
```




