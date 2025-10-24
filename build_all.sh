#!/usr/bin/env bash
set -euo pipefail

# TriSLA Complete Build Pipeline
# Author: Abel Lisboa <abelisboa@gmail.com>
# Date: 2025-10-23

OWNER="abelisboa"
VERSION="${VERSION:-latest}"
REGISTRY="ghcr.io"

echo "🚀 Starting TriSLA Complete Build Pipeline"
echo "📦 Registry: ${REGISTRY}/${OWNER}"
echo "🏷️  Version: ${VERSION}"
echo ""

# Function to build and tag image
build_image() {
    local module=$1
    local path=$2
    local port=$3
    
    echo "🔨 Building ${module}..."
    docker build -t ${REGISTRY}/${OWNER}/trisla-${module}:${VERSION} ${path}
    docker tag ${REGISTRY}/${OWNER}/trisla-${module}:${VERSION} ${REGISTRY}/${OWNER}/trisla-${module}:latest
    
    echo "✅ ${module} built successfully"
    echo ""
}

# Core TriSLA Modules
build_image "semantic" "src/semantic" "8080"
build_image "ai" "src/ai" "8080"
build_image "blockchain" "src/blockchain" "7051"
build_image "integration" "src/integration" "8080"
build_image "monitoring" "src/monitoring" "9090"

# Portal Modules
build_image "api" "trisla-portal/apps/api" "8000"
build_image "ui" "trisla-portal/apps/ui" "80"

echo "🎉 All TriSLA modules built successfully!"
echo ""
echo "📋 Built Images:"
docker images | grep "ghcr.io/${OWNER}/trisla-"
echo ""
echo "🔍 To test images locally:"
echo "  docker run -p 8080:8080 ghcr.io/${OWNER}/trisla-semantic:${VERSION}"
echo "  docker run -p 8080:8080 ghcr.io/${OWNER}/trisla-ai:${VERSION}"
echo "  docker run -p 8080:8080 ghcr.io/${OWNER}/trisla-integration:${VERSION}"
echo "  docker run -p 7051:7051 ghcr.io/${OWNER}/trisla-blockchain:${VERSION}"
echo "  docker run -p 9090:9090 ghcr.io/${OWNER}/trisla-monitoring:${VERSION}"
echo "  docker run -p 8000:8000 ghcr.io/${OWNER}/trisla-api:${VERSION}"
echo "  docker run -p 80:80 ghcr.io/${OWNER}/trisla-ui:${VERSION}"
