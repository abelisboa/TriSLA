#!/bin/bash
set -e

export FABRIC_CFG_PATH=${PWD}/config
export CHANNEL_NAME=trisla-channel
export CC_NAME=sla_chaincode
export CC_VERSION=1.0

echo "Deploying TriSLA chaincode..."

# Package chaincode
peer lifecycle chaincode package ${CC_NAME}.tar.gz --path ./chaincode/sla_chaincode --lang golang --label ${CC_NAME}_${CC_VERSION}

# Install chaincode
peer lifecycle chaincode install ${CC_NAME}.tar.gz

# Approve chaincode
peer lifecycle chaincode approveformyorg -o orderer.example.com:7050 --channelID $CHANNEL_NAME --name $CC_NAME --version $CC_VERSION --package-id ${CC_NAME}_${CC_VERSION} --sequence 1 --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

# Commit chaincode
peer lifecycle chaincode commit -o orderer.example.com:7050 --channelID $CHANNEL_NAME --name $CC_NAME --version $CC_VERSION --sequence 1 --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt

echo "TriSLA chaincode deployed successfully!"
