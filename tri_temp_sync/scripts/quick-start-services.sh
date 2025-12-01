#!/usr/bin/env bash
# Script rápido para iniciar apenas os serviços essenciais (sem rebuild completo)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRISLA_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$TRISLA_ROOT"

echo "[TriSLA Quick Start] Iniciando serviços essenciais..."

# Ativar venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "[TriSLA Quick Start] ❌ .venv não encontrado. Execute TRISLA_AUTO_RUN.sh primeiro."
    exit 1
fi

# Verificar se Besu está rodando
if ! curl -s --max-time 2 -X POST --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' http://127.0.0.1:8545 > /dev/null 2>&1; then
    echo "[TriSLA Quick Start] Iniciando Besu..."
    bash scripts/blockchain/rebuild_besu.sh > /dev/null 2>&1
    sleep 10
fi

# Iniciar SEM-CSMF
echo "[TriSLA Quick Start] Iniciando SEM-CSMF..."
cd apps/sem-csmf/src
python main.py > ../../../trisla_build.log 2>&1 &
SEM_PID=$!
cd ../../..
sleep 5

# Iniciar ML-NSMF
echo "[TriSLA Quick Start] Iniciando ML-NSMF..."
cd apps/ml-nsmf/src
python main.py > ../../../trisla_build.log 2>&1 &
ML_PID=$!
cd ../../..
sleep 5

# Iniciar Decision Engine
echo "[TriSLA Quick Start] Iniciando Decision Engine..."
cd apps/decision-engine/src
python main.py > ../../../trisla_build.log 2>&1 &
DE_PID=$!
cd ../../..
sleep 5

echo "[TriSLA Quick Start] ✅ Serviços iniciados:"
echo "  - SEM-CSMF (PID: $SEM_PID) - http://127.0.0.1:8080"
echo "  - ML-NSMF (PID: $ML_PID) - http://127.0.0.1:8081"
echo "  - Decision Engine (PID: $DE_PID) - http://127.0.0.1:8082"

