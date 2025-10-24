#!/usr/bin/env bash
set -euo pipefail
pushd "$(dirname "$0")/.."

CC_NAME=sla_chaincode
CC_PATH=chaincode/sla_chaincode
CC_LANG=golang
CC_VERSION=1.0
CC_SEQUENCE=1

echo "➤ Empacotando chaincode..."
docker exec cli bash -lc "
cd /artifacts && peer lifecycle chaincode package ${CC_NAME}.tar.gz \
  --path /${CC_PATH} --lang ${CC_LANG} --label ${CC_NAME}_${CC_VERSION}
"

echo "➤ Instalando chaincode no peer0.org1..."
docker exec cli bash -lc "
peer lifecycle chaincode install /artifacts/${CC_NAME}.tar.gz
PKG_ID=\$(peer lifecycle chaincode queryinstalled | sed -n 's/Package ID: \\(.*\\), Label:.*$/\\1/p')
echo \"PKG_ID=\$PKG_ID\" >/artifacts/pkgid.env
"

echo "➤ Aprovando para Org1..."
docker exec cli bash -lc '
source /artifacts/pkgid.env
peer lifecycle chaincode approveformyorg -o orderer.example.com:7050 \
  --channelID trisla-channel --name '${CC_NAME}' --version '${CC_VERSION}' \
  --package-id $PKG_ID --sequence '${CC_SEQUENCE}' --tls \
  --cafile /etc/hyperledger/production/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt
peer lifecycle chaincode checkcommitreadiness --channelID trisla-channel --name '${CC_NAME}' --version '${CC_VERSION}' --sequence '${CC_SEQUENCE}' --output json
peer lifecycle chaincode commit -o orderer.example.com:7050 --channelID trisla-channel \
  --name '${CC_NAME}' --version '${CC_VERSION}' --sequence '${CC_SEQUENCE}' \
  --tls --cafile /etc/hyperledger/production/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt \
  --peerAddresses peer0.org1.example.com:7051 \
  --tlsRootCertFiles /etc/hyperledger/production/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
peer lifecycle chaincode querycommitted --channelID trisla-channel --name '${CC_NAME}'
'

echo "➤ Chaincode implantado."
popd
