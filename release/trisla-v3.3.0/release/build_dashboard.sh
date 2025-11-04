#!/bin/bash

echo "🚀 Building TriSLA Dashboard v3.2.4..."

docker build -t ghcr.io/abelisboa/trisla-dashboard-frontend:3.2.4 ./apps/dashboard/frontend

docker build -t ghcr.io/abelisboa/trisla-dashboard-backend:latest ./apps/dashboard/backend

echo "✅ Dashboard images built successfully"


