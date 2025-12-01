#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  TRI-SLA A2 — HELM OFFLINE SAFE VALIDATE
#  Modo seguro: NÃO toca no cluster, NÃO executa kubectl/helm upgrade
# ============================================================

ROOT_DIR="/home/porvir5g/gtp5g/trisla"
HELM_DIR="${ROOT_DIR}/helm/trisla"
VALUES_FILE="${HELM_DIR}/values-nasp.yaml"
REPORT="/tmp/TRISLA_HELM_OFFLINE_VALIDATE_REPORT.txt"
RENDER_OUTPUT="/tmp/TRISLA_HELM_OFFLINE_RENDER.yaml"

echo "============================================================" | tee "${REPORT}"
echo "📘 TRI-SLA A2 — HELM OFFLINE SAFE VALIDATE" | tee -a "${REPORT}"
echo "Gerado em: $(date)" | tee -a "${REPORT}"
echo "============================================================" | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

echo "📁 Diretório raiz do projeto: ${ROOT_DIR}" | tee -a "${REPORT}"
echo "📁 Diretório Helm:           ${HELM_DIR}" | tee -a "${REPORT}"
echo "📄 Values file:              ${VALUES_FILE}" | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

cd "${ROOT_DIR}"

# ============================================================
#  FASE 1 — Auditoria offline dos templates
# ============================================================
echo "------------------------------------------------------------" | tee -a "${REPORT}"
echo "🧮 FASE 1 — Auditoria offline dos templates" | tee -a "${REPORT}"
echo "------------------------------------------------------------" | tee -a "${REPORT}"

if [[ ! -d "${HELM_DIR}/templates" ]]; then
  echo "❌ Diretório de templates não encontrado: ${HELM_DIR}/templates" | tee -a "${REPORT}"
  exit 1
fi

echo "📄 Templates encontrados:" | tee -a "${REPORT}"
find "${HELM_DIR}/templates" -maxdepth 1 -type f -name "*.yaml" -or -name "*.yml" | sort | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

echo "📄 Arquivos residuais (*.backup, *.orig, *.old):" | tee -a "${REPORT}"
RESIDUAIS=$(find "${HELM_DIR}/templates" -maxdepth 1 -type f \( -name "*.backup" -o -name "*.orig" -o -name "*.old" \) | sort || true)
if [[ -z "${RESIDUAIS}" ]]; then
  echo "✅ Nenhum arquivo residual encontrado." | tee -a "${REPORT}"
else
  echo "${RESIDUAIS}" | tee -a "${REPORT}"
  echo "⚠️  Recomenda-se remover estes arquivos ANTES de um helm upgrade." | tee -a "${REPORT}"
fi
echo "" | tee -a "${REPORT}"

# ============================================================
#  FASE 2 — Verificação básica de selectors/labels
# ============================================================
echo "------------------------------------------------------------" | tee -a "${REPORT}"
echo "🏷️  FASE 2 — Verificação básica de selectors/labels" | tee -a "${REPORT}"
echo "------------------------------------------------------------" | tee -a "${REPORT}"

echo "🔍 Procurando por padrões 'app: trisla-*' nos templates..." | tee -a "${REPORT}"
grep -R --line-number --no-messages "app: trisla-" "${HELM_DIR}/templates" || true | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

echo "🔍 Verificando uso de helpers de selector problemáticos..." | tee -a "${REPORT}"
grep -R --line-number --no-messages "selectorLabels" "${HELM_DIR}/templates" || true | tee -a "${REPORT}"
grep -R --line-number --no-messages "merge . " "${HELM_DIR}/templates" || true | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

# ============================================================
#  FASE 3 — Validação offline com helm template
# ============================================================
echo "------------------------------------------------------------" | tee -a "${REPORT}"
echo "🧪 FASE 3 — Validação offline com helm template" | tee -a "${REPORT}"
echo "------------------------------------------------------------" | tee -a "${REPORT}"

if [[ ! -f "${VALUES_FILE}" ]]; then
  echo "❌ Arquivo de values não encontrado: ${VALUES_FILE}" | tee -a "${REPORT}"
  exit 1
fi

echo "▶️ Executando: helm template (offline)" | tee -a "${REPORT}"
if helm template trisla "${HELM_DIR}" -f "${VALUES_FILE}" > "${RENDER_OUTPUT}"; then
  echo "✅ helm template executado com sucesso." | tee -a "${REPORT}"
  echo "📄 Render completo salvo em: ${RENDER_OUTPUT}" | tee -a "${REPORT}"
else
  echo "❌ ERRO: helm template falhou." | tee -a "${REPORT}"
  exit 1
fi
echo "" | tee -a "${REPORT}"

TOTAL_LINHAS=$(wc -l < "${RENDER_OUTPUT}" || echo 0)
TOTAL_SERVICES=$(grep -c "^kind: Service" "${RENDER_OUTPUT}" || echo 0)
TOTAL_DEPLOYMENTS=$(grep -c "^kind: Deployment" "${RENDER_OUTPUT}" || echo 0)
TOTAL_INGRESS=$(grep -c "^kind: Ingress" "${RENDER_OUTPUT}" || echo 0)

echo "📏 Estatísticas do manifest renderizado:" | tee -a "${REPORT}"
echo "   ▸ Linhas totais:     ${TOTAL_LINHAS}" | tee -a "${REPORT}"
echo "   ▸ Services:          ${TOTAL_SERVICES}" | tee -a "${REPORT}"
echo "   ▸ Deployments:       ${TOTAL_DEPLOYMENTS}" | tee -a "${REPORT}"
echo "   ▸ Ingress:           ${TOTAL_INGRESS}" | tee -a "${REPORT}"
echo "" | tee -a "${REPORT}"

# ============================================================
#  FASE 4 — Resumo final
# ============================================================
echo "------------------------------------------------------------" | tee -a "${REPORT}"
echo "📘 FASE 4 — Resumo final" | tee -a "${REPORT}"
echo "------------------------------------------------------------" | tee -a "${REPORT}"
echo "Validação offline concluída sem modificar o cluster." | tee -a "${REPORT}"
echo "Relatório salvo em: ${REPORT}" | tee -a "${REPORT}"
echo "============================================================" | tee -a "${REPORT}"

