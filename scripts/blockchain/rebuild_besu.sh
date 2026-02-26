#!/usr/bin/env bash
set -e
set -o pipefail

# Verificar e tentar iniciar Docker
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$SCRIPT_DIR/check_docker.sh" ]; then
    bash "$SCRIPT_DIR/check_docker.sh" || {
        echo "❌ ERRO: Docker não está disponível. Abortando."
        exit 1
    }
else
    # Fallback: verificação simples
    if ! command -v docker &> /dev/null; then
        echo "❌ ERRO: Docker não está instalado ou não está no PATH."
        exit 1
    fi
    
    if ! docker ps &> /dev/null; then
        echo "❌ ERRO: Docker não está rodando. Inicie o Docker Desktop e tente novamente."
        exit 1
    fi
fi

echo "[TriSLA] Limpando ambiente BESU…"
docker rm -f besu-dev 2>/dev/null || true
docker volume rm besu-data 2>/dev/null || true

echo "[TriSLA] Subindo Hyperledger Besu em modo DEV com todas as flags corretas…"
docker run -d --name besu-dev \
  -p 8545:8545 \
  -p 8546:8546 \
  -p 30303:30303 \
  hyperledger/besu:latest \
  --network=dev \
  --rpc-http-enabled=true \
  --rpc-http-host=0.0.0.0 \
  --rpc-http-port=8545 \
  --rpc-http-api=ETH,NET,WEB3,ADMIN,DEBUG \
  --rpc-http-cors-origins="*" \
  --host-allowlist="*" \
  --miner-enabled=true \
  --miner-coinbase=0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1 \
  --miner-extra-data=0x00 \
  --data-path=/opt/besu/data

echo "[TriSLA] Aguardando inicialização do Besu (20s)…"
sleep 20

echo "[TriSLA] Validando RPC (10 tentativas)…"
RPC_OK=false
for i in {1..10}; do
  RESP=$(curl -s -X POST \
    --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
    http://127.0.0.1:8545 2>/dev/null || echo "")
  
  if echo "$RESP" | grep -q "result"; then
    echo "[TriSLA] 🟩 RPC OK — Besu online."
    RPC_OK=true
    break
  fi
  
  echo "[TriSLA] Esperando RPC… Tentativa $i/10"
  sleep 4
done

if [ "$RPC_OK" = false ]; then
  echo "[TriSLA] ⚠️  RPC não respondeu após 10 tentativas."
  echo "[TriSLA] Verificando logs do container..."
  docker logs besu-dev --tail 30 2>/dev/null || echo "[TriSLA] Não foi possível acessar logs do container."
  echo "[TriSLA] Verificando se o container está rodando..."
  docker ps --filter "name=besu-dev" || echo "[TriSLA] Container não está rodando."
fi

echo
echo "[TriSLA] rebuild_besu.sh finalizado."
