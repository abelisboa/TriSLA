#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "ANÁLISE RUNBOOK — SEÇÃO KAFKA"
echo "=========================================================="

RUNBOOK="docs/TRISLA_MASTER_RUNBOOK.md"

if [ ! -f "$RUNBOOK" ]; then
  echo "ERRO: Runbook não encontrado em $(pwd)"
  exit 1
fi

echo
echo "Localizando referências a Kafka no runbook..."
echo "----------------------------------------------------------"
grep -n -i "kafka" "$RUNBOOK" || echo "Nenhuma referência encontrada."

echo
echo "Extraindo bloco contextual (20 linhas antes/depois)..."
echo "----------------------------------------------------------"

LINE=$(grep -n -i "kafka" "$RUNBOOK" | head -n1 | cut -d: -f1 || true)

if [ -n "${LINE:-}" ]; then
  START=$((LINE-20))
  END=$((LINE+20))
  sed -n "${START},${END}p" "$RUNBOOK"
else
  echo "Kafka não documentado explicitamente no runbook."
fi

echo
echo "=========================================================="
echo "FIM DA ANÁLISE RUNBOOK"
echo "=========================================================="
