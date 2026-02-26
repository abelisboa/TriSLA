#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
EXPECTED_VERSION="${EXPECTED_VERSION:-v3.11.2}"
REGISTRY="${REGISTRY:-ghcr.io/abelisboa}"

# Em ambientes reais, BESU costuma ter ciclo próprio (você já usa v3.11.0)
BESU_VERSION="${BESU_VERSION:-v3.11.0}"

VALUES_FILE="${VALUES_FILE:-helm/trisla/values.yaml}"
CHART_DIR="${CHART_DIR:-helm/trisla}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_autofix_${TS}"

mkdir -p "${OUT_DIR}"

echo "======================================================"
echo "TRISLA AUTO FIX IMAGES v2"
echo "Namespace         : ${NS}"
echo "Expected Version  : ${EXPECTED_VERSION}"
echo "Besu Version      : ${BESU_VERSION}"
echo "Registry          : ${REGISTRY}"
echo "Values            : ${VALUES_FILE}"
echo "Chart             : ${CHART_DIR}"
echo "Timestamp         : ${TS}"
echo "Output            : ${OUT_DIR}"
echo "======================================================"
echo

if [[ ! -f "${VALUES_FILE}" ]]; then
  echo "ABORT: values.yaml não encontrado em ${VALUES_FILE}"
  exit 2
fi

cp "${VALUES_FILE}" "${VALUES_FILE}.backup.${TS}"
echo "Backup criado: ${VALUES_FILE}.backup.${TS}"
echo

# ------------------------------------------------------------
# Helpers: substituição por bloco (range) para evitar "sed nuker"
# ------------------------------------------------------------
# Substitui a linha 'repository:' dentro do bloco de um serviço.
# Ex: service_key=semCsmf  repo_value=trisla-sem-csmf
set_repo_in_block() {
  local service_key="$1"
  local repo_value="$2"
  # Entre "^service_key:" e o próximo "^[^ ]" (novo top-level), troca repository:
  perl -0777 -i -pe "s/(^${service_key}:\n(?:.*\n)*?^\s*image:\n(?:.*\n)*?^\s*repository:\s*).*(\n)/\$1${repo_value}\$2/mg" "${VALUES_FILE}"
}

# Substitui a linha 'tag:' dentro do bloco de um serviço (apenas dentro de image:)
set_tag_in_block() {
  local service_key="$1"
  local tag_value="$2"
  perl -0777 -i -pe "s/(^${service_key}:\n(?:.*\n)*?^\s*image:\n(?:.*\n)*?^\s*tag:\s*).*(\n)/\$1${tag_value}\$2/mg" "${VALUES_FILE}"
}

# Para blocos onde o chart pode usar "imageTag" ou formatos alternativos
set_kv_in_block_fallback() {
  local service_key="$1"
  local key="$2"
  local value="$3"
  perl -0777 -i -pe "s/(^${service_key}:\n(?:.*\n)*?^\s*${key}:\s*).*(\n)/\$1${value}\$2/mg" "${VALUES_FILE}"
}

# Garante global.imageRegistry
perl -0777 -i -pe "s/(^global:\n(?:.*\n)*?^\s*imageRegistry:\s*).*(\n)/\$1${REGISTRY}\$2/mg" "${VALUES_FILE}"

# ------------------------------------------------------------
# FASE 1 — Fixar Kafka e iperf3 de forma determinística
# ------------------------------------------------------------
echo "FASE 1 — Fixando dependências externas determinísticas"
echo "------------------------------------------------------"

# Kafka: o seu chart pode usar kafka.image.repository/tag OU kafka.imageTag
# Tentamos os formatos mais comuns sem destruir o resto do YAML.
set_repo_in_block "kafka" "apache/kafka"
set_tag_in_block  "kafka" "3.6.1"
set_kv_in_block_fallback "kafka" "imageTag" "3.6.1"

# iperf3 normalmente vem de chart/deploy próprio; se existir bloco, ajusta
# (Se não existir, não falha; apenas não altera nada.)
set_repo_in_block "iperf3" "networkstatic/iperf3" || true
set_tag_in_block  "iperf3" "3.16" || true

echo "OK: Kafka=3.6.1 e iperf3=3.16 (quando aplicável no values)."
echo

# ------------------------------------------------------------
# FASE 2 — Uniformizar serviços TriSLA (com exceções explícitas)
# ------------------------------------------------------------
echo "FASE 2 — Uniformizando serviços TriSLA"
echo "--------------------------------------"

# Serviços TriSLA que devem seguir EXPECTED_VERSION
TRISLA_SERVICES=(
  "semCsmf:trisla-sem-csmf"
  "mlNsmf:trisla-ml-nsmf"
  "decisionEngine:trisla-decision-engine"
  "bcNssmf:trisla-bc-nssmf"
  "slaAgentLayer:trisla-sla-agent-layer"
  "trafficExporter:trisla-traffic-exporter"
  "uiDashboard:trisla-ui-dashboard"
)

for item in "${TRISLA_SERVICES[@]}"; do
  key="${item%%:*}"
  repo="${item##*:}"
  set_repo_in_block "${key}" "${repo}"
  set_tag_in_block  "${key}" "${EXPECTED_VERSION}"
done

# Exceções (mantém realidade do seu cluster)
# BESU
set_repo_in_block "besu" "trisla-besu"
set_tag_in_block  "besu" "${BESU_VERSION}"

# NASP Adapter (você usa 3.9.28 no cluster; só altere se tiver certeza da existência de v3.11.2)
set_repo_in_block "naspAdapter" "trisla-nasp-adapter"
# Se você quiser forçar uniformidade, exporte NASP_VERSION=v3.11.2 antes de rodar
NASP_VERSION="${NASP_VERSION:-v3.9.28}"
set_tag_in_block "naspAdapter" "${NASP_VERSION}"

echo "OK: TriSLA apps => ${EXPECTED_VERSION} | BESU => ${BESU_VERSION} | NASP => ${NASP_VERSION}"
echo

# ------------------------------------------------------------
# FASE 3 — Helm template sanity (detecta :latest e tags quebradas antes de aplicar)
# ------------------------------------------------------------
echo "FASE 3 — Sanity do render (helm template)"
echo "----------------------------------------"
helm template trisla "${CHART_DIR}" -n "${NS}" -f "${VALUES_FILE}" > "${OUT_DIR}/rendered.yaml"

if grep -qE 'image:\s+.*:latest(\s|$)' "${OUT_DIR}/rendered.yaml"; then
  echo "ABORT: render contém :latest. Veja ${OUT_DIR}/rendered.yaml"
  grep -nE 'image:\s+.*:latest(\s|$)' "${OUT_DIR}/rendered.yaml" | head -n 50
  exit 10
fi

if grep -qE 'image:\s+[^ ]+$' "${OUT_DIR}/rendered.yaml"; then
  echo "WARN: render contém imagem sem tag explícita (verifique se é desejado)."
  grep -nE 'image:\s+[^ ]+$' "${OUT_DIR}/rendered.yaml" | head -n 50
fi

echo "OK: render sem :latest."
echo

# ------------------------------------------------------------
# FASE 4 — Helm upgrade
# ------------------------------------------------------------
echo "FASE 4 — Aplicando Helm upgrade"
echo "-------------------------------"
helm upgrade trisla "${CHART_DIR}" -n "${NS}" -f "${VALUES_FILE}" | tee "${OUT_DIR}/helm_upgrade.log"

echo
echo "FASE 5 — Rollout"
echo "----------------"
kubectl rollout status deploy/trisla-decision-engine -n "${NS}" | tee -a "${OUT_DIR}/rollout.log" || true
kubectl rollout status deploy/trisla-besu -n "${NS}" | tee -a "${OUT_DIR}/rollout.log" || true

echo
echo "FASE 6 — Evidências finais"
echo "--------------------------"
kubectl get deploy -n "${NS}" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.template.spec.containers[*]}{.name}{"="}{.image}{" "}{end}{"\n"}{end}' \
  | sed 's/[[:space:]]\+/ /g' \
  | sort > "${OUT_DIR}/deploy_images.tsv"

kubectl get pods -n "${NS}" -o wide > "${OUT_DIR}/pods.txt"

echo
echo "======================================================"
echo "AUTO FIX v2 FINALIZADO"
echo "Evidências: ${OUT_DIR}"
echo "======================================================"
