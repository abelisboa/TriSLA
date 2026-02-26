#!/usr/bin/env bash
# TriSLA - HEARTBEAT LOOP
#
# Executa o scripts/heartbeat.py em loop, registrando logs em logs/heartbeat.log.
# Pode ser iniciado em foreground ou background (ex: via TRISLA_AUTO_RUN.sh).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs"
LOG_FILE="${LOG_DIR}/heartbeat.log"

PYTHON_BIN="python3"
if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
fi

mkdir -p "${LOG_DIR}"

INTERVAL_SECONDS="${HEARTBEAT_INTERVAL_SECONDS:-30}"

echo "[TriSLA HEARTBEAT] Iniciando loop de heartbeat (intervalo=${INTERVAL_SECONDS}s). Log: ${LOG_FILE}"

while true; do
  TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  STATUS_LINE="$(${PYTHON_BIN} "${ROOT_DIR}/scripts/heartbeat.py" 2>&1 || true)"

  # Registrar linha compacta no log
  {
    echo "[$TS] ${STATUS_LINE}"
  } >> "${LOG_FILE}"

  sleep "${INTERVAL_SECONDS}"
done

