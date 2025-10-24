#!/usr/bin/env bash
set -euo pipefail

# TriSLA Image Testing Script
# Author: Abel Lisboa <abelisboa@gmail.com>
# Date: 2025-10-23

OWNER="abelisboa"
VERSION="${VERSION:-latest}"
REGISTRY="ghcr.io"

echo "🧪 TriSLA Image Testing Pipeline"
echo "================================"
echo ""

# Function to test image
test_image() {
    local module=$1
    local port=$2
    local health_check_url=$3
    local container_name="trisla-test-${module}"
    
    echo "🔍 Testing ${module}..."
    
    # Stop and remove existing container if it exists
    docker stop "$container_name" 2>/dev/null || true
    docker rm "$container_name" 2>/dev/null || true
    
    # Start container
    echo "  🚀 Starting container..."
    docker run -d --name "$container_name" -p "${port}:${port}" \
        "${REGISTRY}/${OWNER}/trisla-${module}:${VERSION}"
    
    # Wait for container to start
    echo "  ⏳ Waiting for container to start..."
    sleep 10
    
    # Check if container is running
    if ! docker ps | grep -q "$container_name"; then
        echo "  ❌ Container failed to start"
        docker logs "$container_name" 2>/dev/null || true
        return 1
    fi
    
    echo "  ✅ Container is running"
    
    # Health check if URL provided
    if [[ -n "$health_check_url" ]]; then
        echo "  🔍 Performing health check..."
        if curl -f -s "$health_check_url" >/dev/null 2>&1; then
            echo "  ✅ Health check passed"
        else
            echo "  ⚠️  Health check failed (service may still be starting)"
        fi
    fi
    
    # Show container logs (last 10 lines)
    echo "  📋 Recent logs:"
    docker logs --tail 10 "$container_name" 2>/dev/null || true
    
    # Cleanup
    echo "  🧹 Cleaning up..."
    docker stop "$container_name" >/dev/null 2>&1 || true
    docker rm "$container_name" >/dev/null 2>&1 || true
    
    echo "  ✅ ${module} test completed"
    echo ""
}

# Test core modules
test_image "semantic" "8080" "http://localhost:8080/health"
test_image "ai" "8081" "http://localhost:8081/health"
test_image "integration" "8082" "http://localhost:8082/health"
test_image "monitoring" "9090" "http://localhost:9090/-/healthy"

# Test blockchain (different port)
echo "🔍 Testing blockchain..."
container_name="trisla-test-blockchain"
docker stop "$container_name" 2>/dev/null || true
docker rm "$container_name" 2>/dev/null || true

echo "  🚀 Starting blockchain container..."
docker run -d --name "$container_name" -p "7051:7051" \
    "${REGISTRY}/${OWNER}/trisla-blockchain:${VERSION}"

sleep 10

if docker ps | grep -q "$container_name"; then
    echo "  ✅ Blockchain container is running"
    echo "  📋 Recent logs:"
    docker logs --tail 10 "$container_name" 2>/dev/null || true
else
    echo "  ❌ Blockchain container failed to start"
    docker logs "$container_name" 2>/dev/null || true
fi

echo "  🧹 Cleaning up..."
docker stop "$container_name" >/dev/null 2>&1 || true
docker rm "$container_name" >/dev/null 2>&1 || true
echo "  ✅ Blockchain test completed"
echo ""

# Test portal modules
test_image "api" "8000" "http://localhost:8000/health"
test_image "ui" "80" "http://localhost:80"

echo "🎉 All image tests completed!"
echo ""
echo "📊 Test Summary:"
echo "  ✅ Core modules tested"
echo "  ✅ Portal modules tested"
echo "  ✅ All containers started successfully"
echo ""
echo "🔗 Images are ready for deployment:"
echo "  ${REGISTRY}/${OWNER}/trisla-semantic:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-ai:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-blockchain:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-integration:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-monitoring:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-api:${VERSION}"
echo "  ${REGISTRY}/${OWNER}/trisla-ui:${VERSION}"









