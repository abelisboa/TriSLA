#!/bin/bash
# TriSLA Portal Build Script

set -e

echo "🚀 Iniciando reconstrução completa do TriSLA Portal..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🚧 Building containers..."
docker compose build

echo "✅ Build completed."

echo "🚀 Starting containers..."
docker compose up -d
sleep 5

echo "🧪 Checking health..."
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "✅ API is responding"
else
    echo "❌ API not responding"
fi

echo "✅ Setup completed. Check http://localhost:5173"
