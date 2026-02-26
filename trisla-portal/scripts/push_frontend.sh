#!/bin/bash
set -e

IMAGE="ghcr.io/abelisboa/trisla-portal-frontend:latest"

echo "📤 Pushing frontend image..."
docker push $IMAGE
echo "✅ Push complete."
