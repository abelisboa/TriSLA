#!/bin/bash
set -euo pipefail

ROOT="$(pwd)"
NAMESPACE="trisla"
CHART_DIR="$ROOT/helm/trisla"
VALUES_FILE="$CHART_DIR/values-nasp.yaml"

echo "==============================================================="
echo " 🚀 TRISLA — PIPELINE COMPLETA: BUILD LOCAL + LOAD + DEPLOY NASP"
echo "==============================================================="

# ---------------------------------------------------------------
# Modo rollback manual, se chamado como:
#   ./trisla_devops_nasp_full.sh rollback
# ---------------------------------------------------------------
if [[ "${1-}" == "rollback" ]]; then
  echo ""
  echo "➡ MODO ROLLBACK MANUAL ATIVADO"
  echo "   Obtendo histórico do release 'trisla'..."
  helm history trisla -n "$NAMESPACE" || {
    echo "❌ Não foi possível obter o histórico do Helm. Release existe?"
    exit 1
  }

  LAST_REVISION=$(helm history trisla -n "$NAMESPACE" --output json \
    | grep '"revision"' | tail -n1 | sed 's/[^0-9]//g' || true)

  if [[ -z "$LAST_REVISION" ]]; then
    echo "❌ Não foi possível determinar a última revisão."
    exit 1
  fi

  echo "➡ Aplicando rollback para revisão: $LAST_REVISION"
  helm rollback trisla "$LAST_REVISION" -n "$NAMESPACE"
  echo "✅ Rollback concluído."
  exit 0
fi

# ---------------------------------------------------------------
# Verificações iniciais
# ---------------------------------------------------------------
echo ""
echo "➡ Etapa 0 — Verificando ferramentas obrigatórias..."

command -v podman >/dev/null 2>&1 || { echo "❌ 'podman' não encontrado."; exit 1; }
command -v helm   >/dev/null 2>&1 || { echo "❌ 'helm' não encontrado.";   exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ 'kubectl' não encontrado."; exit 1; }

if [[ ! -d "$CHART_DIR" ]]; then
  echo "❌ Chart Helm não encontrado em: $CHART_DIR"
  exit 1
fi

if [[ ! -f "$VALUES_FILE" ]]; then
  echo "❌ values-nasp.yaml não encontrado em: $VALUES_FILE"
  exit 1
fi

echo "✅ Ferramentas e arquivos básicos presentes."

# ---------------------------------------------------------------
# Definição dos módulos e diretórios de build
# Ajuste os caminhos 'apps/...'
# ---------------------------------------------------------------
declare -A MODULES
MODULES["bc-nssmf"]="apps/bc-nssmf"
MODULES["decision-engine"]="apps/decision-engine"
MODULES["ml-nsmf"]="apps/ml-nsmf"
MODULES["nasp-adapter"]="apps/nasp-adapter"
MODULES["sem-csmf"]="apps/sem-csmf"
MODULES["sla-agent-layer"]="apps/sla-agent-layer"
MODULES["ui-dashboard"]="apps/ui-dashboard"

echo ""
echo "➡ Etapa 1 — Build LOCAL das imagens com podman"
echo "   (tag: localhost/trisla-<serviço>:local)"
echo "---------------------------------------------------------------"

for NAME in "${!MODULES[@]}"; do
  CONTEXT="${MODULES[$NAME]}"
  IMAGE="localhost/trisla-${NAME}:local"

  echo ""
  echo "📦 Serviço: $NAME"
  echo "   → Contexto: $CONTEXT"
  echo "   → Imagem:  $IMAGE"

  if [[ ! -d "$CONTEXT" ]]; then
    echo "   ⚠ Diretório de contexto não encontrado: $CONTEXT"
    echo "     → Pulei este serviço, ajuste o caminho no script se necessário."
    continue
  fi

  podman build -t "$IMAGE" "$CONTEXT"
  echo "   ✅ Build concluído para $IMAGE"
done

# ---------------------------------------------------------------
# Etapa 2 — Load das imagens no containerd (se existir ctr)
# ---------------------------------------------------------------
echo ""
echo "➡ Etapa 2 — Importando imagens para o runtime do Kubernetes (containerd, se disponível)"
echo "---------------------------------------------------------------"

if command -v ctr >/dev/null 2>&1; then
  echo "✅ 'ctr' encontrado — usando containerd namespace k8s.io"

  for NAME in "${!MODULES[@]}"; do
    IMAGE="localhost/trisla-${NAME}:local"
    TAR="/tmp/trisla-${NAME}.tar"

    echo ""
    echo "🛢  Exportando e importando imagem: $IMAGE"
    podman image exists "$IMAGE" || {
      echo "   ⚠ Imagem não existe localmente, pulando: $IMAGE"
      continue
    }

    podman save -o "$TAR" "$IMAGE"
    sudo ctr -n k8s.io images import "$TAR"
    rm -f "$TAR"
    echo "   ✅ Imagem importada no containerd: $IMAGE"
  done
else
  echo "⚠ 'ctr' NÃO encontrado — presumindo que o Kubernetes consegue acessar as imagens do podman diretamente."
  echo "   Se os pods ficarem em ImagePullBackOff, será necessário implementar um registry local ou ajustar o runtime."
fi

# ---------------------------------------------------------------
# Etapa 3 — Ajustar values para usar localhost + tag local
# (reforça o que já fizemos com fix_trisla_helm_global.sh)
# ---------------------------------------------------------------
echo ""
echo "➡ Etapa 3 — Refino do values-nasp.yaml para usar localhost + local"
echo "---------------------------------------------------------------"

# Este bloco é idempotente, apenas reforça o uso de localhost/tag local
for NAME in "${!MODULES[@]}"; do
  KEY=""
  case "$NAME" in
    "bc-nssmf")          KEY="bcNssmf" ;;
    "decision-engine")   KEY="decisionEngine" ;;
    "ml-nsmf")           KEY="mlNsmf" ;;
    "nasp-adapter")      KEY="naspAdapter" ;;
    "sem-csmf")          KEY="semCsmf" ;;
    "sla-agent-layer")   KEY="slaAgentLayer" ;;
    "ui-dashboard")      KEY="uiDashboard" ;;
  esac

  [[ -z "$KEY" ]] && continue

  sed -i "s#\(repository:\s*\).*trisla-$NAME.*#\1\"localhost/trisla-$NAME\"#g" "$VALUES_FILE" || true
  sed -i "s#\(tag:\s*\).*#\1\"local\"#g" "$VALUES_FILE" || true
done

echo "✅ values-nasp.yaml reforçado para usar imagens locais."

# ---------------------------------------------------------------
# Etapa 4 — Deploy via Helm com rollback automático (--atomic)
# ---------------------------------------------------------------
echo ""
echo "➡ Etapa 4 — Deploy/upgrade via Helm no namespace '$NAMESPACE'"
echo "   → Chart:   $CHART_DIR"
echo "   → Values:  $VALUES_FILE"
echo "   → Flags:   --atomic --timeout 10m --create-namespace"
echo "---------------------------------------------------------------"

helm upgrade --install trisla "$CHART_DIR" \
  -n "$NAMESPACE" \
  -f "$VALUES_FILE" \
  --create-namespace \
  --atomic \
  --timeout 10m

echo ""
echo "✅ Helm upgrade/install concluído com sucesso."

# ---------------------------------------------------------------
# Etapa 5 — Verificação de saúde dos pods
# ---------------------------------------------------------------
echo ""
echo "➡ Etapa 5 — Verificando pods no namespace '$NAMESPACE'"
echo "---------------------------------------------------------------"
kubectl get pods -n "$NAMESPACE" -o wide

echo ""
echo "==============================================================="
echo " ✅ PIPELINE COMPLETA EXECUTADA COM SUCESSO"
echo "    → Imagens buildadas localmente com podman"
echo "    → Imagens importadas (se containerd disponível)"
echo "    → Deploy/upgrade Helm com rollback automático (--atomic)"
echo "    → Para rollback manual: ./trisla_devops_nasp_full.sh rollback"
echo "==============================================================="
