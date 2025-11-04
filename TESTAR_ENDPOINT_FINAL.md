# ✅ Testar Endpoint Final

## ✅ Status

- ✅ `main.py` atualizado (5891 bytes)
- ✅ `prometheus.py` copiado (4352 bytes)
- ✅ Deployment reiniciado
- ❌ `httpx` e `requests` não disponíveis
- ⚠️ Pod mudou de nome após restart

---

## 🎯 Execute Estes Comandos

```bash
cd ~/gtp5g/trisla-portal

# 1. Pegar novo pod
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')
echo "Novo Pod: $POD_NAME"
echo ""

# 2. Verificar se arquivos ainda estão lá
echo "2️⃣ Verificando arquivos..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/main.py && \
  echo "✅ Router está no main.py" || echo "❌ Router não está no main.py"
echo ""

# 3. Ver logs de inicialização (ver se router foi carregado)
echo "3️⃣ Logs de inicialização (prometheus/router):"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=100 | grep -i -E "prometheus|router.*prometheus" | tail -10
echo ""

# 4. Ver todos os logs recentes para erros
echo "4️⃣ Logs recentes (últimas 30 linhas):"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=30
echo ""

# 5. Criar port-forward com novo pod
echo "5️⃣ Criando port-forward..."
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 > /tmp/pf.log 2>&1 &
PF_PID=$!
sleep 8

# 6. Testar endpoint
echo "6️⃣ Testando /prometheus/health..."
curl -s http://localhost:8000/prometheus/health
echo ""
echo ""

# Se retornar:
# - 404 Not Found → Router não foi carregado
# - 500 Internal Server Error → Router carregado mas httpx não disponível
# - JSON com status → Funcionando!

# 7. Parar port-forward
kill $PF_PID 2>/dev/null
```

---

## 🔍 Interpretar Resultados

### Se retornar 404 Not Found:
- Router não foi carregado
- Verificar logs para ver erro de import

### Se retornar 500 Internal Server Error:
- Router foi carregado! ✅
- Mas `httpx` não está disponível
- Solução: modificar `prometheus.py` para usar alternativa OU rebuild imagem

### Se retornar JSON:
- Tudo funcionando! ✅

---

## 🔧 Se Router Foi Carregado Mas httpx Não Está

Podemos modificar `prometheus.py` para usar `urllib` (built-in do Python):

```bash
# Ver se urllib está disponível (sempre está)
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import urllib.request; print('✅ urllib OK')"

# Se funcionar, podemos criar versão modificada do prometheus.py usando urllib
```

Ou podemos tentar instalar httpx de outra forma (mas provavelmente não funcionará sem internet).

---

## 📋 Comandos Completos (Copie e Cole)

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Pod: $POD_NAME"
echo ""

echo "Verificando arquivos..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- grep -q "prometheus_router" /app/main.py && \
  echo "✅ Router no main.py" || echo "❌ Router não no main.py"
echo ""

echo "Logs (prometheus/router):"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=100 | grep -i -E "prometheus|router.*prometheus"
echo ""

echo "Criando port-forward..."
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 > /tmp/pf.log 2>&1 &
sleep 8

echo "Testando endpoint..."
curl -s http://localhost:8000/prometheus/health
echo ""
echo ""

echo "Logs recentes:"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=20
```




