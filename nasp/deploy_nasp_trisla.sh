#!/bin/bash
# ============================================================
# TriSLA NASP Deployment Script (node1)
# Autor: Abel Lisboa
# Data: $(date +%Y-%m-%d)
# Descrição:
#   Deploy automatizado e verificação do TriSLA Portal
#   em ambiente NASP (limpo ou existente).
# ============================================================

set -e

NAMESPACE="trisla"
APP_NAME="trisla-portal"
GHCR_USER="${GHCR_USER:-abelisboa}"
LOG_FILE="/tmp/deploy_trisla_portal_$(date +%Y%m%d_%H%M%S).log"

echo "🚀 [1/6] Preparando ambiente para deploy do TriSLA Portal..."
echo "------------------------------------------------------------"

# 1️⃣ Verificação inicial
echo "📋 Checando ferramentas necessárias..."
for cmd in git kubectl helm ansible curl; do
  if ! command -v $cmd &>/dev/null; then
    echo "❌ Erro: comando '$cmd' não encontrado no PATH. Instale antes de continuar."
    exit 1
  fi
done

# 2️⃣ Confirmar acesso ao cluster
if ! kubectl get nodes &>/dev/null; then
  echo "❌ Erro: kubectl não consegue acessar o cluster Kubernetes."
  exit 1
fi

echo "✅ Ambiente Kubernetes detectado:"
kubectl get nodes -o wide | tee -a "$LOG_FILE"
echo "------------------------------------------------------------"

# 3️⃣ Atualizar repositório
echo "🔄 Atualizando repositório TriSLA-Portal..."
cd ~/gtp5g/trisla-portal
git fetch --all
git reset --hard origin/main
echo "✅ Repositório atualizado."
echo "------------------------------------------------------------"

# 4️⃣ Executar deploy Ansible
echo "🛰️ [2/6] Executando playbook Ansible..."
if [ -z "$GHCR_TOKEN" ]; then
  echo "⚠️  Aviso: variável GHCR_TOKEN não definida. Exporte antes de rodar:"
  echo "     export GHCR_TOKEN=<seu_token_ghcr>"
  exit 1
fi

ansible-playbook ansible/deploy_trisla_portal.yml | tee -a "$LOG_FILE"
echo "------------------------------------------------------------"

# 5️⃣ Verificação pós-deploy
echo "🔍 [3/6] Verificando status dos pods e serviços..."
sleep 10
kubectl get pods -n "$NAMESPACE" -o wide | tee -a "$LOG_FILE"
kubectl get svc -n "$NAMESPACE" | tee -a "$LOG_FILE"

# Esperar até que os pods fiquem prontos
echo "⏳ Aguardando pods ficarem prontos..."
kubectl wait --for=condition=Ready pods -l app=$APP_NAME -n "$NAMESPACE" --timeout=180s || {
  echo "⚠️  Alguns pods não ficaram prontos dentro do tempo limite."
}

echo "------------------------------------------------------------"

# 6️⃣ Testes de endpoints
echo "🧠 [4/6] Testando endpoints públicos..."
BACKEND_URL="http://localhost:30800/api/v1/health"
FRONTEND_URL="http://localhost:30173/"

echo "🌐 Testando API Backend: $BACKEND_URL"
curl -s "$BACKEND_URL" || echo "⚠️ API não respondeu."

echo "🌐 Testando Frontend: $FRONTEND_URL"
curl -sI "$FRONTEND_URL" | head -n1 || echo "⚠️ Frontend não respondeu."

echo "------------------------------------------------------------"

# 7️⃣ Diagnóstico pós-deploy
if [ -f tools/tri-doctor.sh ]; then
  echo "🧪 [5/6] Executando TriSLA Doctor (diagnóstico final)..."
  chmod +x tools/tri-doctor.sh
  tools/tri-doctor.sh .
else
  echo "⚠️  tri-doctor.sh não encontrado. Pulei diagnóstico final."
fi

echo "------------------------------------------------------------"

# 8️⃣ Finalização
echo "✅ [6/6] Deploy completo!"
echo "📜 Log detalhado salvo em: $LOG_FILE"
echo "------------------------------------------------------------"

kubectl get pods -n "$NAMESPACE" -o wide
echo "🚀 TriSLA Portal pronto para uso!"
