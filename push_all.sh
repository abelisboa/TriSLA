#!/usr/bin/env bash
set -euo pipefail

# TriSLA Complete Push Pipeline
# Author: Abel Lisboa <abelisboa@gmail.com>
# Date: 2025-10-23

OWNER="abelisboa"
VERSION="${VERSION:-latest}"
REGISTRY="ghcr.io"

echo "🚀 Starting TriSLA Complete Push Pipeline"
echo "📦 Registry: ${REGISTRY}/${OWNER}"
echo "🏷️  Version: ${VERSION}"
echo ""

# Function to push image
push_image() {
    local module=$1
    
    echo "📤 Pushing ${module}..."
    docker push ${REGISTRY}/${OWNER}/trisla-${module}:${VERSION}
    docker push ${REGISTRY}/${OWNER}/trisla-${module}:latest
    
    echo "✅ ${module} pushed successfully"
    echo ""
}

# Core TriSLA Modules
push_image "semantic"
push_image "ai"
push_image "blockchain"
push_image "integration"
push_image "monitoring"

# Portal Modules
push_image "api"
push_image "ui"

echo "🎉 All TriSLA modules pushed successfully!"
echo ""
echo "🔗 Published Images:"
echo "  ${REGISTRY}/${OWNER}/trisla-semantic:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-ai:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-blockchain:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-integration:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-monitoring:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-api:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-ui:${VERSION}"
