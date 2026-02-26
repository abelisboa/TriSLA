#!/bin/bash
set -euo pipefail

BASE_DIR="/home/porvir5g/gtp5g/trisla"
LATEST_DIR=$(ls -dt ${BASE_DIR}/evidencias_crd_schema/nsi_schema_* | head -n 1)
SRC="${LATEST_DIR}/02_openapi_schema.yaml"
CRD_FULL="${LATEST_DIR}/01_crd_full.yaml"
ANALYSIS_DIR="${LATEST_DIR}/analysis"
OUT="${ANALYSIS_DIR}/NSI_SCHEMA_REPORT.txt"

mkdir -p "${ANALYSIS_DIR}"

echo "==================================================" | tee "${OUT}"
echo "TriSLA — NSI CRD SCHEMA REPORT" | tee -a "${OUT}"
echo "Source Dir : ${LATEST_DIR}" | tee -a "${OUT}"
echo "Timestamp  : $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "${OUT}"
echo "==================================================" | tee -a "${OUT}"
echo "" | tee -a "${OUT}"

echo "## 1) CRD: Subresources / Status" | tee -a "${OUT}"
echo "--------------------------------------------------" | tee -a "${OUT}"
if grep -n "subresources" -n "${CRD_FULL}" >/dev/null 2>&1; then
  grep -n "subresources" -n "${CRD_FULL}" | head -n 40 | tee -a "${OUT}" || true
  echo "" | tee -a "${OUT}"
  awk '
    $0 ~ /subresources:/ {p=1}
    p==1 {print}
    p==1 && $0 ~ /^[^[:space:]]/ && NR>1 {exit}
  ' "${CRD_FULL}" | head -n 120 | tee -a "${OUT}" || true
else
  echo "(não encontrado) — provável que status NÃO seja subresource explicitado ou o bloco não está presente." | tee -a "${OUT}"
fi
echo "" | tee -a "${OUT}"

echo "## 2) Required fields (tudo que o schema exige)" | tee -a "${OUT}"
echo "--------------------------------------------------" | tee -a "${OUT}"
if [ -f "${ANALYSIS_DIR}/06_required_fields.txt" ]; then
  cat "${ANALYSIS_DIR}/06_required_fields.txt" | tee -a "${OUT}" || true
else
  grep -n "required:" "${SRC}" | tee -a "${OUT}" || true
fi
echo "" | tee -a "${OUT}"

echo "## 3) SLA occurrences (onde SLA existe no schema)" | tee -a "${OUT}"
echo "--------------------------------------------------" | tee -a "${OUT}"
if [ -f "${ANALYSIS_DIR}/04_sla_occurrences.txt" ]; then
  cat "${ANALYSIS_DIR}/04_sla_occurrences.txt" | tee -a "${OUT}" || true
else
  grep -n "sla:" "${SRC}" | tee -a "${OUT}" || true
fi
echo "" | tee -a "${OUT}"

echo "## 4) Tentativa de extrair o bloco spec.sla (se existir como objeto com properties)" | tee -a "${OUT}"
echo "--------------------------------------------------" | tee -a "${OUT}"
# Extrai trecho ao redor da primeira ocorrência de "sla:"
LINE=$(grep -n "sla:" "${SRC}" | head -n 1 | cut -d: -f1 || true)
if [ -n "${LINE}" ]; then
  START=$((LINE-40)); if [ "${START}" -lt 1 ]; then START=1; fi
  END=$((LINE+160))
  sed -n "${START},${END}p" "${SRC}" | tee -a "${OUT}" || true
else
  echo "(não há 'sla:' no openAPIV3Schema) — SLA pode não ser definido no CRD." | tee -a "${OUT}"
fi
echo "" | tee -a "${OUT}"

echo "## 5) Flags preserve-unknown-fields (indicador se aceita campos livres)" | tee -a "${OUT}"
echo "--------------------------------------------------" | tee -a "${OUT}"
if [ -f "${ANALYSIS_DIR}/05_preserve_flags.txt" ]; then
  cat "${ANALYSIS_DIR}/05_preserve_flags.txt" | tee -a "${OUT}" || true
else
  grep -n "preserve" "${SRC}" | tee -a "${OUT}" || true
fi
echo "" | tee -a "${OUT}"

echo "## 6) Conclusões automáticas (heurísticas seguras)" | tee -a "${OUT}"
echo "--------------------------------------------------" | tee -a "${OUT}"

# Heurística: status no create
if grep -n "subresources:" "${CRD_FULL}" >/dev/null 2>&1 && grep -n "status:" "${CRD_FULL}" | grep -n "subresources" -n >/dev/null 2>&1; then
  echo "- status: CRD parece declarar subresource status (ainda assim: NÃO enviar status no create; deixar controller atualizar)." | tee -a "${OUT}"
else
  echo "- status: não evidenciado como subresource → NÃO enviar status no create (evita warning/erro)." | tee -a "${OUT}"
fi

# Heurística: SLA livre ou fechado
if grep -n "x-kubernetes-preserve-unknown-fields" "${SRC}" >/dev/null 2>&1; then
  echo "- sla: há preserve-unknown-fields em algum ponto → pode aceitar campos livres (confirmar onde)." | tee -a "${OUT}"
else
  echo "- sla: sem preserve-unknown-fields evidente → schema provavelmente FECHADO (campos não listados geram warning/erro)." | tee -a "${OUT}"
fi

echo "- metadata.name: deve ser RFC1123 lowercase (sem letras maiúsculas). Timestamp em 'Z' quebra o schema." | tee -a "${OUT}"

echo "" | tee -a "${OUT}"
echo "==================================================" | tee -a "${OUT}"
echo "Report: ${OUT}" | tee -a "${OUT}"
echo "==================================================" | tee -a "${OUT}"

echo ""
echo "✅ Report gerado em: ${OUT}"
