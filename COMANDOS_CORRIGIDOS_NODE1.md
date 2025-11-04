# ✅ Comandos Corrigidos - Use Base64

## Problema Detectado

O arquivo foi criado mas com **0 bytes** porque o heredoc não passou o conteúdo corretamente.

---

## ✅ Solução: Use Base64

Execute no node1:

```bash
cd ~/gtp5g/trisla-portal

# 1. Identificar pod
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')
echo "Pod: $POD_NAME | Container: $CONTAINER"

# 2. Codificar arquivo em base64
echo "📦 Codificando arquivo..."
BASE64_DATA=$(base64 -w 0 apps/api/prometheus.py)

# 3. Criar no pod usando base64
echo "📤 Copiando para o pod..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << PYEOF
import base64
import os

os.makedirs('/app/apps/api', exist_ok=True)

b64_data = '''$BASE64_DATA'''
content = base64.b64decode(b64_data).decode('utf-8')

with open('/app/apps/api/prometheus.py', 'w') as f:
    f.write(content)

print(f"✅ Arquivo criado: {len(content)} bytes")
PYEOF

# 4. Verificar
echo ""
echo "🔍 Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/apps/api/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -10 /app/apps/api/prometheus.py
```

---

## 🔧 Método Alternativo: Usar arquivo temporário

Se base64 não funcionar:

```bash
# Criar arquivo temporário no pod e depois copiar conteúdo linha por linha
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- bash -c "
  mkdir -p /app/apps/api
  cat > /app/apps/api/prometheus.py << 'ENDOFFILE'
$(cat apps/api/prometheus.py)
ENDOFFILE
"

# Verificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/apps/api/prometheus.py
```

---

## 🚀 OU Execute o Script

```bash
chmod +x COPIAR_PROMETHEUS_CORRETO.sh
./COPIAR_PROMETHEUS_CORRETO.sh
```

---

## ⚠️ Se ainda der problema: Usar Python direto

Execute Python interativamente:

```bash
# Copiar conteúdo completo para uma variável
PROM_CONTENT=$(cat apps/api/prometheus.py)

# Executar Python no pod
kubectl exec -it -n trisla $POD_NAME -c $CONTAINER -- python3

# Dentro do Python:
# import os
# os.makedirs('/app/apps/api', exist_ok=True)
# content = '''<cole o conteúdo aqui>'''
# with open('/app/apps/api/prometheus.py', 'w') as f:
#     f.write(content)
```

---

## 📝 Verificar depois de copiar

```bash
# Ver tamanho
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- wc -l /app/apps/api/prometheus.py
# Deve ter mais de 100 linhas

# Ver primeiras linhas
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -20 /app/apps/api/prometheus.py

# Ver últimas linhas
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- tail -10 /app/apps/api/prometheus.py
```




