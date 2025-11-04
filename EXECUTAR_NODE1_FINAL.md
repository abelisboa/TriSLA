# ✅ Comandos Finais para Executar no node1

## 🎯 Execute Estes Comandos

```bash
cd ~/gtp5g/trisla-portal

# 1. Adicionar httpx ao requirements.txt
echo "Adicionando httpx ao requirements.txt..."
grep -q "httpx" apps/api/requirements.txt || echo "httpx" >> apps/api/requirements.txt
cat apps/api/requirements.txt | grep httpx
echo ""

# 2. Verificar se httpx já está disponível no pod atual
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Testando se httpx está disponível no pod..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx; print('✅ httpx JÁ está disponível!')" 2>&1 || \
  echo "⚠️ httpx não está disponível - precisa rebuild da imagem"
echo ""

# 3. Testar endpoint (criar port-forward)
echo "Criando port-forward na porta 8000..."
kubectl port-forward -n trisla svc/trisla-portal 8000:8000 > /tmp/pf.log 2>&1 &
PF_PID=$!
sleep 8

echo "Testando /prometheus/health..."
curl -s http://localhost:8000/prometheus/health
echo ""
echo ""

# 4. Verificar logs para erros
echo "Verificando logs (últimas 20 linhas)..."
kubectl logs -n trisla -l app=trisla-portal --tail=20 | grep -i -E "prometheus|httpx|error|traceback" || \
kubectl logs -n trisla -l app=trisla-portal --tail=20
echo ""

# 5. Parar port-forward
kill $PF_PID 2>/dev/null
echo "✅ Port-forward encerrado"
```

---

## 🔧 Se httpx não estiver disponível - Próximos Passos

### Opção A: Testar outros endpoints (pode funcionar mesmo sem httpx se Prometheus não for chamado ainda)

```bash
# Testar health geral da API
curl http://localhost:8000/api/v1/health
```

### Opção B: Rebuild imagem com httpx

```bash
# Se você tiver acesso ao Docker no node1 e GHCR:
cd apps/api

# Build
docker build -t ghcr.io/abelisboa/trisla-api:prometheus .

# Push
docker push ghcr.io/abelisboa/trisla-api:prometheus

# Atualizar deployment
kubectl set image deployment/trisla-portal -n trisla \
  trisla-api=ghcr.io/abelisboa/trisla-api:prometheus

# Aguardar
kubectl rollout status deployment/trisla-portal -n trisla --timeout=5m
```

---

## 📊 Status Atual

✅ **Completo:**
- `prometheus.py` criado (4352 bytes, 119 linhas)
- `main.py` atualizado (5891 bytes) com router
- Deployment reiniciado

⚠️ **Pendente:**
- `httpx` precisa ser adicionado ao `requirements.txt` (feito)
- Se `httpx` não estiver na imagem, precisa rebuild

🎯 **Próximo:**
- Testar endpoint para ver se funciona
- Se não funcionar, rebuild imagem com `httpx`




