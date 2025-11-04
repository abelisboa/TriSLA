#!/bin/bash
set -e
echo "🚀 Running TriSLA Portal UI/API upgrade automation..."

cd apps/ui
npm install
cd ../../
docker compose build ui api worker
docker compose up -d
echo "✅ All containers started."
docker ps
curl http://localhost:8000/api/v1/health
