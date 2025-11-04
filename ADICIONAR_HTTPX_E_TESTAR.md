# 🔧 Adicionar httpx ao requirements.txt e Testar

## ⚠️ Problema Detectado

- ✅ `main.py` atualizado
- ✅ Deployment reiniciado
- ❌ `httpx` não instalado (problema de rede)

---

## ✅ Solução: Adicionar httpx ao requirements.txt

Como o pod não tem acesso à internet para instalar `httpx`, precisamos adicionar ao `requirements.txt` e rebuildar a imagem.

### PASSO 1: Adicionar httpx ao requirements.txt

```bash
cd ~/gtp5g/trisla-portal

# Verificar se httpx já está no requirements.txt
grep -q "httpx" apps/api/requirements.txt && echo "✅ httpx já está" || echo "httpx" >> apps/api/requirements.txt

# Verificar
echo "Conteúdo do requirements.txt:"
cat apps/api/requirements.txt | grep httpx
```

---

### PASSO 2: Testar Endpoint (pode funcionar se httpx já estiver na imagem)

Mesmo que a instalação via pip tenha falhado, `httpx` pode já estar na imagem Docker. Vamos testar:

```bash
# Criar port-forward
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 &
PF_PID=$!
sleep 5

# Testar endpoint
echo "Testando /prometheus/health..."
curl -s http://localhost:8000/prometheus/health | jq . || curl -s http://localhost:8000/prometheus/health

# Verificar logs para erros
echo ""
echo "Logs recentes:"
kubectl logs -n trisla -l app=trisla-portal --tail=30 | grep -i -E "prometheus|httpx|error" || \
kubectl logs -n trisla -l app=trisla-portal --tail=30

# Parar port-forward (se necessário)
# kill $PF_PID 2>/dev/null
```

---

### PASSO 3: Se httpx não estiver disponível - Rebuild Imagem

Se o endpoint falhar com erro de `httpx` não encontrado:

```bash
# 1. Garantir que httpx está no requirements.txt
echo "httpx" >> apps/api/requirements.txt

# 2. Verificar se há Dockerfile
ls -la apps/api/Dockerfile

# 3. Build nova imagem (se Docker disponível no node1)
cd apps/api
docker build -t ghcr.io/abelisboa/trisla-api:prometheus .
docker push ghcr.io/abelisboa/trisla-api:prometheus

# 4. Atualizar deployment
kubectl set image deployment/trisla-portal -n trisla \
  trisla-api=ghcr.io/abelisboa/trisla-api:prometheus

# 5. Aguardar rollout
kubectl rollout status deployment/trisla-portal -n trisla --timeout=5m
```

---

## 🎯 Comandos Rápidos (Execute no node1)

```bash
cd ~/gtp5g/trisla-portal

# 1. Adicionar httpx ao requirements.txt
grep -q "httpx" apps/api/requirements.txt || echo "httpx" >> apps/api/requirements.txt
echo "✅ requirements.txt atualizado"

# 2. Testar endpoint (pode funcionar se httpx já estiver na imagem)
echo ""
echo "Criando port-forward..."
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 > /dev/null 2>&1 &
sleep 5

echo "Testando /prometheus/health..."
curl -s http://localhost:8000/prometheus/health || echo "❌ Endpoint não respondeu"

echo ""
echo "Verificando logs para erros..."
kubectl logs -n trisla -l app=trisla-portal --tail=20 | tail -10
```

---

## 📋 Verificar Status Atual

```bash
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Verificar se httpx está disponível no Python
echo "Testando import httpx no pod..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx; print('✅ httpx disponível')" 2>&1 || \
  echo "❌ httpx não disponível - precisa adicionar ao requirements.txt e rebuild"

# Verificar se prometheus.py pode ser importado
echo ""
echo "Testando import prometheus..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import sys; sys.path.insert(0, '/app/apps/api'); from prometheus import router; print('✅ prometheus.py pode ser importado')" 2>&1
```




