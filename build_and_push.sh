#!/bin/bash
set -e

echo "Building and publishing TriSLA Docker images to GHCR..."

# Login to GHCR
docker login ghcr.io -u abelisboa

# Build and push semantic module
echo "Building trisla-semantic..."
docker build -t ghcr.io/abelisboa/trisla-semantic:latest ./apps/semantic
docker push ghcr.io/abelisboa/trisla-semantic:latest

# Build and push AI module
echo "Building trisla-ai..."
docker build -t ghcr.io/abelisboa/trisla-ai:latest ./apps/ai
docker push ghcr.io/abelisboa/trisla-ai:latest

# Build and push blockchain module
echo "Building trisla-blockchain..."
docker build -t ghcr.io/abelisboa/trisla-blockchain:latest ./apps/blockchain
docker push ghcr.io/abelisboa/trisla-blockchain:latest

# Build and push monitoring module
echo "Building trisla-monitoring..."
docker build -t ghcr.io/abelisboa/trisla-monitoring:latest ./apps/monitoring
docker push ghcr.io/abelisboa/trisla-monitoring:latest

echo "All TriSLA images built and published successfully!"
