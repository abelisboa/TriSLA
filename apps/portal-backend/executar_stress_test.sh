#!/bin/bash
# Script para executar o stress test completo no Linux/Mac/WSL

echo "========================================"
echo "STRESS TEST COMPLETO - TRI SLA"
echo "Capítulo 6 - Considerações Preliminares"
echo "========================================"
echo

cd "$(dirname "$0")"

echo "Verificando Python..."
python3 --version || python --version
if [ $? -ne 0 ]; then
    echo "ERRO: Python não encontrado!"
    exit 1
fi

echo
echo "Executando orquestrador..."
python3 tools/stress_test_orchestrator.py || python tools/stress_test_orchestrator.py

echo
echo "========================================"
echo "Execução concluída!"
echo "========================================"
echo
echo "Verifique os arquivos gerados:"
echo "- backend/STRESS_TEST_REPORT.md"
echo "- backend/stress_test_report.json"
echo "- backend/figures/*.png"
echo "- backend/stress_test_orchestrator.log"
echo




