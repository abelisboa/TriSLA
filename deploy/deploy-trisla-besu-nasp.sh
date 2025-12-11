#!/usr/bin/env bash
# Script de deploy do TriSLA BESU no NASP
# FASE 3: Deploy NASP

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 [TriSLA] Deploy do BESU no NASP"
echo "=================================="
echo ""

# Verificar pré-requisitos
echo "📋 [TriSLA] Verificando pré-requisitos..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ ERRO: kubectl não está instalado"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ ERRO: helm não está instalado"
    exit 1
fi

# Verificar acesso ao cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ ERRO: Não há acesso ao cluster Kubernetes"
    exit 1
fi

echo "✅ [TriSLA] Pré-requisitos OK"
echo ""

# Verificar namespace
NAMESPACE="trisla"
echo "📋 [TriSLA] Verificando namespace '$NAMESPACE'..."
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "⚠️  [TriSLA] Namespace '$NAMESPACE' não existe. Criando..."
    kubectl create namespace "$NAMESPACE"
fi
echo ""

# Atualizar dependências do Helm
echo "📦 [TriSLA] Atualizando dependências do Helm..."
cd "$REPO_ROOT"
helm dependency update helm/trisla || {
    echo "❌ ERRO: Falha ao atualizar dependências"
    exit 1
}
echo "✅ [TriSLA] Dependências atualizadas"
echo ""

# Validar Helm chart
echo "📋 [TriSLA] Validando Helm chart..."
helm lint helm/trisla || {
    echo "❌ ERRO: Helm chart inválido"
    exit 1
}
echo "✅ [TriSLA] Helm chart válido"
echo ""

# Renderizar templates (dry-run)
echo "📋 [TriSLA] Renderizando templates (dry-run)..."
helm template trisla ./helm/trisla \
    -f ./helm/trisla/values-nasp.yaml \
    --debug > /dev/null || {
    echo "❌ ERRO: Falha ao renderizar templates"
    exit 1
}
echo "✅ [TriSLA] Templates renderizados com sucesso"
echo ""

# Aplicar deploy
echo "🚀 [TriSLA] Aplicando deploy do TriSLA (incluindo BESU)..."
helm upgrade --install trisla ./helm/trisla \
    -n "$NAMESPACE" \
    -f ./helm/trisla/values-nasp.yaml \
    --create-namespace \
    --cleanup-on-fail \
    --wait \
    --timeout 10m \
    --debug

echo ""
echo "✅ [TriSLA] Deploy aplicado"
echo ""

# Aguardar pods ficarem prontos
echo "⏳ [TriSLA] Aguardando pods do BESU ficarem prontos..."
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/component=besu \
    -n "$NAMESPACE" \
    --timeout=5m || {
    echo "⚠️  [TriSLA] Timeout aguardando pods. Verificando status..."
    kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/component=besu
}
echo ""

# Aguardar BESU ficar pronto (eth_blockNumber)
echo "⏳ [TriSLA] Aguardando BESU ficar pronto (eth_blockNumber)..."
MAX_ATTEMPTS=30
ATTEMPT=1
BESU_READY=false

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "   Tentativa $ATTEMPT/$MAX_ATTEMPTS..."
    
    # Port-forward temporário para testar
    BESU_POD=$(kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/component=besu -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    
    if [ -n "$BESU_POD" ]; then
        # Testar RPC dentro do pod
        RESPONSE=$(kubectl -n "$NAMESPACE" exec "$BESU_POD" -- \
            curl -s -X POST http://localhost:8545 \
                -H "Content-Type: application/json" \
                --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' 2>/dev/null || echo "ERRO")
        
        if echo "$RESPONSE" | grep -q "result"; then
            BESU_READY=true
            echo "   ✅ BESU está respondendo!"
            break
        fi
    fi
    
    if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
        sleep 10
    fi
    
    ((ATTEMPT++))
done

if [ "$BESU_READY" = false ]; then
    echo "⚠️  [TriSLA] BESU não respondeu após $MAX_ATTEMPTS tentativas"
else
    echo "✅ [TriSLA] BESU está pronto!"
fi
echo ""

# Verificar status
echo "📊 [TriSLA] Verificando status do deploy..."
kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/component=besu
kubectl -n "$NAMESPACE" get svc -l app.kubernetes.io/component=besu
echo ""

# Verificar logs
echo "📋 [TriSLA] Últimas linhas dos logs do BESU:"
kubectl -n "$NAMESPACE" logs -l app.kubernetes.io/component=besu --tail=20 || true
echo ""

# Testar BC-NSSMF (se disponível)
echo "🔗 [TriSLA] Testando conectividade BC-NSSMF..."
BC_NSSMF_POD=$(kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/name=trisla-bc-nssmf -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -n "$BC_NSSMF_POD" ]; then
    echo "   Testando endpoint BC-NSSMF..."
    kubectl -n "$NAMESPACE" exec "$BC_NSSMF_POD" -- \
        curl -s -X POST http://localhost:8083/api/v1/register-sla \
            -H "Content-Type: application/json" \
            --data '{"test": "besu connectivity"}' || echo "   ⚠️  BC-NSSMF não respondeu"
else
    echo "   ⚠️  BC-NSSMF não está rodando"
fi
echo ""

# Gerar relatório
echo "📝 [TriSLA] Gerando relatório de deploy..."
cat > "$REPO_ROOT/deploy/BESU_DEPLOY_REPORT.md" <<EOF
# BESU Deploy Report - TriSLA NASP

**Data:** $(date +"%Y-%m-%d %H:%M:%S")  
**Namespace:** $NAMESPACE  
**Status:** $([ "$BESU_READY" = true ] && echo "✅ SUCESSO" || echo "⚠️  PARCIAL")

---

## 📋 Resumo do Deploy

### Helm Chart
- **Chart:** trisla (com dependência trisla-besu)
- **Versão BESU:** 23.10.1
- **Namespace:** $NAMESPACE

### Status dos Pods
\`\`\`
$(kubectl -n "$NAMESPACE" get pods -l app.kubernetes.io/component=besu 2>/dev/null || echo "N/A")
\`\`\`

### Status dos Services
\`\`\`
$(kubectl -n "$NAMESPACE" get svc -l app.kubernetes.io/component=besu 2>/dev/null || echo "N/A")
\`\`\`

### Validação RPC
- **eth_blockNumber:** $([ "$BESU_READY" = true ] && echo "✅ OK" || echo "❌ FALHOU")
- **BESU Ready:** $([ "$BESU_READY" = true ] && echo "✅ SIM" || echo "❌ NÃO")

### Integração BC-NSSMF
- **BC-NSSMF Pod:** $([ -n "$BC_NSSMF_POD" ] && echo "✅ Encontrado" || echo "⚠️  Não encontrado")

---

## 🚀 Próximos Passos

1. Verificar logs: \`kubectl -n $NAMESPACE logs -l app.kubernetes.io/component=besu\`
2. Testar RPC: \`kubectl -n $NAMESPACE port-forward svc/trisla-besu 8545:8545\`
3. Validar integração com BC-NSSMF

---

*Relatório gerado automaticamente pelo script deploy-trisla-besu-nasp.sh*
EOF

echo "✅ [TriSLA] Relatório gerado: deploy/BESU_DEPLOY_REPORT.md"
echo ""

echo "✅ [TriSLA] Deploy do BESU no NASP concluído!"
echo ""
echo "📋 [TriSLA] Próximos passos:"
echo "   1. Verificar pods: kubectl -n $NAMESPACE get pods -l app.kubernetes.io/component=besu"
echo "   2. Verificar logs: kubectl -n $NAMESPACE logs -l app.kubernetes.io/component=besu"
echo "   3. Testar RPC: kubectl -n $NAMESPACE port-forward svc/trisla-besu 8545:8545"
echo ""

