#!/usr/bin/env bash
set -euo pipefail

pushd "$(dirname "$0")/.."

echo "➤ Limpando pastas organizations/ e artifacts/"
rm -rf organizations artifacts/*.block artifacts/*.tx
mkdir -p organizations/fabric-ca/org1

echo "➤ Subindo CA..."
docker compose -f docker-compose.yaml up -d ca.org1.example.com
sleep 3

echo "➤ Emitindo identidades Org1 (admin/enroll, peer0, tls)..."
docker run --rm -v $(pwd)/organizations:/orgs --network fabric hyperledger/fabric-ca:1.5 \
  sh -c '
  FABRIC_CA_CLIENT_HOME=/orgs/peerOrganizations/org1.example.com
  fabric-ca-client enroll -u https://admin:adminpw@ca.org1.example.com:7054 --tls.certfiles /etc/hyperledger/fabric-ca-server/ca-cert.pem
' || true

echo "⚠️ (Atalho dev) Gerar material do orderer e TLS via exemplos test-network (simplificado)"
# Em ambientes reais, usar Fabric-CA também para Orderer. Aqui assumimos material pré-existente ou gerado via pipeline CI.

echo "➤ Gerando genesis.block e channel.tx (configtxgen dentro de fabric-tools)"
docker run --rm -v $(pwd):/workspace -w /workspace \
  hyperledger/fabric-tools:2.5 sh -c '
  mkdir -p artifacts
  configtxgen -configPath ./config -profile TriSLAOrdererGenesis -channelID system-channel -outputBlock ./artifacts/genesis.block
  configtxgen -configPath ./config -profile TriSLAChannel -outputCreateChannelTx ./artifacts/channel.tx -channelID trisla-channel
'

echo "➤ Subindo Orderer, CouchDB e Peer..."
docker compose -f docker-compose.yaml up -d orderer.example.com couchdb0 peer0.org1.example.com cli

echo "➤ Rede básica subida."
popd
