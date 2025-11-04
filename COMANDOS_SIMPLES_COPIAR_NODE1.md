# ✅ Comandos Simples para Copiar no node1

## 🎯 Método Mais Simples: Base64

Execute estes comandos no node1:

```bash
cd ~/gtp5g/trisla-portal

# 1. Identificar pod
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')
echo "Pod: $POD_NAME | Container: $CONTAINER"

# 2. Verificar onde está main.py
echo "Verificando estrutura..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "main.py" -type f 2>/dev/null

# 3. Determinar diretório correto
# Se encontrar /app/apps/api/main.py, usar /app/apps/api
# Se encontrar /app/main.py, usar /app
# Se não encontrar, tentar criar /app/apps/api

# 4. Copiar arquivo usando base64 (mais confiável que kubectl cp)
echo "Codificando arquivo..."
BASE64_CONTENT=$(cat apps/api/prometheus.py | base64 -w 0)

# 5. Criar no pod (tentar /app/apps/api primeiro)
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- bash -c "
  mkdir -p /app/apps/api 2>/dev/null || mkdir -p /app/api 2>/dev/null || true
  echo '$BASE64_CONTENT' | base64 -d > /app/apps/api/prometheus.py 2>/dev/null || \
  echo '$BASE64_CONTENT' | base64 -d > /app/api/prometheus.py 2>/dev/null || \
  echo '$BASE64_CONTENT' | base64 -d > /app/prometheus.py
"

# 6. Verificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "prometheus.py" -type f
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py 2>/dev/null || \
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/api/prometheus.py 2>/dev/null || \
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
```

---

## 🔧 Método Alternativo: Criar Arquivo Diretamente (Mais Fácil)

Se base64 der problema, criar diretamente no pod:

```bash
POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Copiar conteúdo local para variável
PROMETHEUS_CONTENT=$(cat apps/api/prometheus.py)

# Criar no pod (escapando corretamente)
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << PYSCRIPT
import os
os.makedirs('/app/apps/api', exist_ok=True)

content = '''$PROMETHEUS_CONTENT'''

with open('/app/apps/api/prometheus.py', 'w') as f:
    f.write(content)

print("Arquivo criado!")
PYSCRIPT
```

---

## 📝 Solução Mais Robusta: Script Completo

Execute o script:

```bash
chmod +x COPIAR_PROMETHEUS_POD_SIMPLES.sh
./COPIAR_PROMETHEUS_POD_SIMPLES.sh
```

O script vai:
1. ✅ Verificar estrutura do pod automaticamente
2. ✅ Criar diretórios se necessário
3. ✅ Copiar arquivo no local correto
4. ✅ Verificar instalação de httpx
5. ✅ Verificar se main.py precisa atualização

---

## ⚠️ Se Nada Funcionar: Rebuild Imagem

Como último recurso, fazer rebuild da imagem com o novo código:

```bash
# 1. Adicionar httpx ao requirements.txt
echo "httpx" >> apps/api/requirements.txt

# 2. Build nova imagem
cd apps/api
docker build -t ghcr.io/abelisboa/trisla-api:prometheus .
docker push ghcr.io/abelisboa/trisla-api:prometheus

# 3. Atualizar deployment
kubectl set image deployment/trisla-portal -n trisla \
  backend=ghcr.io/abelisboa/trisla-api:prometheus

# 4. Aguardar rollout
kubectl rollout status deployment/trisla-portal -n trisla
```




