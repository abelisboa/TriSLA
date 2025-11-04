# 🔍 Diagnosticar Estrutura do Pod

## Problemas Encontrados

1. ❌ Caminho `/app/apps/api` não existe
2. ❌ Container não se chama `trisla-backend`
3. ⚠️ Problemas de rede para instalar httpx

---

## 🔧 PASSO 1: Diagnosticar Estrutura do Pod

Execute no node1:

```bash
cd ~/gtp5g/trisla-portal

# Pegar pod
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
echo "Pod: $POD_NAME"

# 1. Ver containers disponíveis
echo "=== Containers ==="
kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[*].name}'
echo ""
echo ""

# 2. Ver estrutura de diretórios (usar primeiro container)
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')
echo "Container: $CONTAINER"
echo ""

echo "=== /app ==="
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -la /app 2>/dev/null | head -20
echo ""

echo "=== /app/apps ==="
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -la /app/apps 2>/dev/null
echo ""

echo "=== Procurando main.py ==="
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "main.py" -type f 2>/dev/null
echo ""

# 3. Ver variáveis de ambiente
echo "=== PYTHONPATH ==="
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- env | grep PYTHONPATH
echo ""

# 4. Ver comando que está rodando
echo "=== Comando ==="
kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].command}'
echo ""
```

---

## ✅ Execute o Script Automático

```bash
chmod +x DIAGNOSTICAR_POD_ESTRUTURA.sh
./DIAGNOSTICAR_POD_ESTRUTURA.sh
```

Após ver os resultados, ajustaremos os comandos de cópia!




