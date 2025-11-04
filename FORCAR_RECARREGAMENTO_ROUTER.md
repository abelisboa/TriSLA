# 🔄 Forçar Recarregamento do Router

## ✅ Status

- ✅ Arquivos copiados
- ✅ Router no main.py
- ❌ Endpoint retorna 404 (router não carregado)

O problema é que o Python já carregou o main.py antes de copiarmos os arquivos. Precisamos forçar o recarregamento.

---

## 🔧 Opções

### Opção 1: Reiniciar Processo Python (Melhor)

```bash
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Ver processo uvicorn
echo "Processo atual:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ps aux | grep python | grep -v grep

# Reiniciar processo (enviar SIGHUP ou matar e deixar container recriar)
# Mas cuidado: pode reiniciar todo o container

# OU melhor: Ver se há algum modo de reload
```

### Opção 2: Verificar Logs para Erros

```bash
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Logs completos (inicialização):"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --tail=200 | grep -i -E "prometheus|router|error|exception|traceback" | head -30

echo ""
echo "Tentando import prometheus manualmente:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')
try:
    from prometheus import router
    print('✅ Import OK')
    print(f'Router prefix: {router.prefix}')
    print(f'Router tem {len(router.routes)} rotas')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
PYEOF
```

### Opção 3: Reiniciar Container (Sem Reiniciar Pod)

```bash
# Matar processo Python principal para forçar reload
# Isso fará o container recriar o processo (se houver restart policy)
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Ver PID do processo principal
PID=$(kubectl exec -n trisla $POD_NAME -c $CONTAINER -- pgrep -f "uvicorn\|python.*main")

# Enviar SIGHUP (se suportado) ou reiniciar container
# kubectl delete pod $POD_NAME -n trisla  # Reinicia o pod (perderá arquivos novamente!)
```

---

## 🎯 Melhor Solução: Verificar Erro e Testar Import

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# 1. Ver logs completos desde início
echo "1️⃣ Logs desde início do pod:"
kubectl logs -n trisla $POD_NAME -c $CONTAINER --since=10m | grep -i -E "prometheus|router|error|exception" | tail -20
echo ""

# 2. Testar import direto
echo "2️⃣ Testando import prometheus:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')
print("Tentando importar prometheus...")
try:
    from prometheus import router
    print('✅ Import OK')
    print(f'Router prefix: {router.prefix}')
    print(f'Rotas: {len(router.routes)}')
    for route in router.routes:
        print(f'  - {route.path}')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
PYEOF
echo ""

# 3. Se import funcionar, verificar se app inclui router
echo "3️⃣ Testando se app tem router:"
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
import sys
sys.path.insert(0, '/app')

# Simular o que main.py faz
from fastapi import FastAPI
app = FastAPI()

# Tentar incluir router
try:
    from prometheus import router as prometheus_router
    app.include_router(prometheus_router)
    print('✅ Router incluído no app')
    print(f'Rotas no app: {len(app.routes)}')
    for route in app.routes:
        if 'prometheus' in route.path:
            print(f'  ✅ {route.path}')
except Exception as e:
    print(f'❌ Erro ao incluir router: {e}')
    import traceback
    traceback.print_exc()
PYEOF
```

---

## 🔄 Se Import Falhar (httpx não disponível)

O problema pode ser que `httpx` não está disponível e o import falha silenciosamente no `main.py`. Vamos verificar:

```bash
# Ver se httpx está disponível
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "import httpx" 2>&1

# Se falhar, modificar prometheus.py para usar urllib (built-in)
```




