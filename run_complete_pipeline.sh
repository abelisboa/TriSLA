#!/usr/bin/env bash
set -euo pipefail

# TriSLA Complete Pipeline Execution Script
# Author: Abel Lisboa <abelisboa@gmail.com>
# Date: 2025-10-23

echo "🚀 TriSLA Complete Pipeline Execution"
echo "====================================="
echo ""

# Configuration
OWNER="abelisboa"
VERSION="${VERSION:-$(date +%Y%m%d-%H%M%S)}"
REGISTRY="ghcr.io"

echo "📋 Configuration:"
echo "  Owner: ${OWNER}"
echo "  Version: ${VERSION}"
echo "  Registry: ${REGISTRY}"
echo ""

# Step 1: Setup
echo "🔧 Step 1: Docker & GHCR Setup"
echo "==============================="
if [[ -f "setup_docker_ghcr.sh" ]]; then
    chmod +x setup_docker_ghcr.sh
    ./setup_docker_ghcr.sh
else
    echo "⚠️  Setup script not found, skipping..."
fi

# Step 2: Build
echo ""
echo "🔨 Step 2: Building All Images"
echo "=============================="
export VERSION="$VERSION"
chmod +x build_all.sh
./build_all.sh

# Step 3: Test
echo ""
echo "🧪 Step 3: Testing Images"
echo "========================"
chmod +x test_images.sh
./test_images.sh

# Step 4: Push
echo ""
echo "📤 Step 4: Pushing to GHCR"
echo "=========================="
chmod +x push_all.sh
./push_all.sh

echo ""
echo "🎉 TriSLA Complete Pipeline Finished Successfully!"
echo ""
echo "📊 Summary:"
echo "  ✅ All 7 modules built"
echo "  ✅ All images tested"
echo "  ✅ All images pushed to GHCR"
echo ""
echo "🔗 Published Images:"
echo "  ${REGISTRY}/${OWNER}/trisla-semantic:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-ai:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-blockchain:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-integration:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-monitoring:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-api:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-ui:${VERSION}"
















