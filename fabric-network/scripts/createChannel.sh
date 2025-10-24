#!/usr/bin/env bash
set -euo pipefail
pushd "$(dirname "$0")/.."

echo "➤ Criando canal trisla-channel..."
docker exec cli bash -lc '
export CORE_PEER_LOCALMSPID=Org1MSP
export CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/production/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=peer0.org1.example.com:7051
export CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/production/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt

peer channel create -o orderer.example.com:7050 \
  -c trisla-channel \
  -f /artifacts/channel.tx \
  --outputBlock /artifacts/trisla.block \
  --tls --cafile /etc/hyperledger/production/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt

peer channel join -b /artifacts/trisla.block
peer channel update -o orderer.example.com:7050 -c trisla-channel \
  -f /artifacts/Org1MSPanchors.tx --tls \
  --cafile /etc/hyperledger/production/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt || true
'
popd
