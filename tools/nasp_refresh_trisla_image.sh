#!/bin/bash
# =============================================================
# TriSLA NASP — Image Refresh & Redeploy Utility
# Autor: Abel Lisboa
# Atualizado: 2025-10-27
# =============================================================

set -euo pipefail
NAMESPACE="trisla"
RELEASE="trisla-portal"
GHCR_USER="${GHCR_USER:-abelisboa}"
GHCR_TOKEN="${GHCR_TOKEN:-}"
CHART_PATH="./helm/trisla-portal"
VALUES_PATH="./docs/config-examples/values-nasp.yaml"

# Cores ANSI
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
BLUE='\033[1;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 TriSLA NASP Refresh Utility${NC}"
echo "------------------------------------------------------------"

# 1️⃣ Verificação inicial
if ! command -v nerdctl >/dev/null 2>&1; then
  echo -e "${RED}❌ nerdctl não encontrado. Execute em um node NASP com containerd.${NC}"
  exit 1
fi
if ! command -v helm >/dev/null 2>&1; then
  echo -e "${RED}❌ Helm não encontrado. Instale helm antes de prosseguir.${NC}"
  exit 1
fi
if [[ -z "$GHCR_TOKEN" ]]; then
  echo -e "${YELLOW}⚠️  GHCR_TOKEN não definido. Use: export GHCR_TOKEN=<seu_token_GHCR>${NC}"
  exit 1
fi

# 2️⃣ Limpar containers travados
echo -e "${YELLOW}🧹 Limpando containers antigos do trisla-api...${NC}"
OLD_CONTAINERS=$(sudo nerdctl -n k8s.io ps -a --format '{{.ID}} {{.Image}}' | grep trisla-api | awk '{print $1}' || true)
if [[ -n "$OLD_CONTAINERS" ]]; then
  echo "$OLD_CONTAINERS" | xargs -r sudo nerdctl -n k8s.io rm -f || true
else
  echo "Nenhum container trisla-api ativo encontrado."
fi

# 3️⃣ Limpar imagem antiga
echo -e "${YELLOW}🧽 Removendo imagem antiga ghcr.io/${GHCR_USER}/trisla-api:latest...${NC}"
sudo nerdctl -n k8s.io rmi -f ghcr.io/${GHCR_USER}/trisla-api:latest 2>/dev/null || true
sudo crictl rmi ghcr.io/${GHCR_USER}/trisla-api:latest 2>/dev/null || true
sudo crictl rmi --prune 2>/dev/null || true

# 4️⃣ Login no GHCR
echo -e "${BLUE}🔐 Autenticando no GitHub Container Registry...${NC}"
sudo nerdctl -n k8s.io login ghcr.io -u "${GHCR_USER}" -p "${GHCR_TOKEN}"

# 5️⃣ Reinstalar o Helm chart com imagemPullPolicy=Always
echo -e "${BLUE}🔄 Atualizando TriSLA Portal via Helm...${NC}"
helm upgrade --install "$RELEASE" "$CHART_PATH" \
  -n "$NAMESPACE" \
  -f "$VALUES_PATH" \
  --set backend.imagePullPolicy=Always \
  --timeout 10m0s --atomic --cleanup-on-fail --create-namespace

# 6️⃣ Aguardar pod ficar pronto
echo -e "${YELLOW}⏳ Aguardando pod iniciar...${NC}"
kubectl wait --for=condition=Ready pod -l app=trisla-portal -n "$NAMESPACE" --timeout=300s

# 7️⃣ Exibir status do pod e imagem usada
echo "------------------------------------------------------------"
kubectl get pods -n "$NAMESPACE" -o wide
echo "------------------------------------------------------------"
sudo nerdctl -n k8s.io images | grep trisla-api || echo -e "${YELLOW}⚠️ Nenhuma imagem local encontrada (pode ter sido carregada via CRI).${NC}"

# 8️⃣ Teste funcional da API
echo -e "${BLUE}🧪 Testando endpoint /api/v1/health...${NC}"
HEALTH=$(curl -s --max-time 8 http://localhost:30800/api/v1/health)
if [[ "$HEALTH" == *"TriSLA Portal API running"* ]]; then
  echo -e "${GREEN}✅ API operacional — resposta:${NC} $HEALTH"
else
  echo -e "${RED}❌ API não respondeu corretamente. Conteúdo recebido:${NC}"
  echo "$HEALTH"
  echo
  echo "Últimos logs do container:"
  kubectl logs -n "$NAMESPACE" -l app=trisla-portal -c trisla-api --tail=40
  exit 1
fi

# 9️⃣ Descobrir NodePort e IP do Node
NODE_IP=$(hostname -I | awk '{print $1}')
FRONTEND_PORT=$(kubectl get svc -n "$NAMESPACE" trisla-portal -o jsonpath='{.spec.ports[?(@.name=="frontend")].nodePort}')
BACKEND_PORT=$(kubectl get svc -n "$NAMESPACE" trisla-portal -o jsonpath='{.spec.ports[?(@.name=="backend")].nodePort}')

echo "------------------------------------------------------------"
echo -e "${GREEN}🎯 TriSLA Portal atualizado com sucesso no NASP!${NC}"
echo -e "🌐 Frontend: ${BLUE}http://${NODE_IP}:${FRONTEND_PORT}/${NC}"
echo -e "⚙️  Backend:  ${BLUE}http://${NODE_IP}:${BACKEND_PORT}/api/v1/health${NC}"
echo "------------------------------------------------------------"
