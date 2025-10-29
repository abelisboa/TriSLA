#!/usr/bin/env bash
set -euo pipefail
: "${GHCR_USER?Set GHCR_USER}"; : "${GHCR_TOKEN?Set GHCR_TOKEN}"

echo "🔐 Logging into GHCR..."
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

echo "🐳 Building images..."
docker compose build api ui

echo "📤 Pushing images..."
docker compose push api ui

echo "✅ Build & push concluídos."
