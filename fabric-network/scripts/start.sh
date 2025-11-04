#!/bin/bash
set -e

export FABRIC_CFG_PATH=${PWD}/config
export CHANNEL_NAME=trisla-channel

echo "Starting Hyperledger Fabric network for TriSLA..."

# Start network
docker-compose -f docker-compose.yaml up -d

echo "Waiting for network to be ready..."
sleep 10

# Create channel
./scripts/createChannel.sh

# Deploy chaincode
./scripts/deployCC.sh

echo "TriSLA Fabric network is ready!"
