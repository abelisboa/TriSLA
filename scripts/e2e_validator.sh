#!/usr/bin/env bash
# TriSLA - END-TO-END VALIDATION ORCHESTRATOR WRAPPER
#
# Wrapper Shell para execução simplificada do e2e_validator.py

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Descobrir Python apropriado
PYTHON_BIN="python3"
if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
fi

# Executar validação
echo "[TriSLA] FASE H — Iniciando validação fim-a-fim..."

${PYTHON_BIN} "${ROOT_DIR}/scripts/e2e_validator.py" \
  --mode local \
  --output-md "${ROOT_DIR}/docs/VALIDACAO_FINAL_TRI-SLA.md" \
  --output-json "${ROOT_DIR}/docs/METRICAS_VALIDACAO_FINAL.json"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "[TriSLA] FASE H — Validação concluída com sucesso (ver docs/VALIDACAO_FINAL_TRI-SLA.md)."
elif [ $EXIT_CODE -eq 1 ]; then
  echo "[TriSLA] FASE H — Validação concluída com status DEGRADED (ver docs/VALIDACAO_FINAL_TRI-SLA.md)."
else
  echo "[TriSLA] FASE H — Validação encontrou problemas (ver docs/VALIDACAO_FINAL_TRI-SLA.md)."
fi

exit $EXIT_CODE

