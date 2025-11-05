#!/bin/bash
set -e

export FABRIC_CFG_PATH=${PWD}/config
export CHANNEL_NAME=trisla-channel

echo "Creating channel $CHANNEL_NAME..."

# Create channel
peer channel create -o orderer.example.com:7050 -c $CHANNEL_NAME -f ./config/channel.tx --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

# Join peers to channel
peer channel join -b ${CHANNEL_NAME}.block

echo "Channel $CHANNEL_NAME created successfully!"
