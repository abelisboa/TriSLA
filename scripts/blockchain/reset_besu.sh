#!/usr/bin/env bash
set -e
set -o pipefail

cd "$(dirname "$0")/../../blockchain/besu"

echo "[TriSLA] Resetando rede Besu DEV…"
docker compose -f docker-compose-besu.yaml down -v || true
docker compose -f docker-compose-besu.yaml up -d

echo "[TriSLA] Aguardando inicialização…"
sleep 10

echo "[TriSLA] Containers:"
docker ps | grep besu-dev || echo "besu-dev não encontrado."

echo "[TriSLA] Reset concluído."
