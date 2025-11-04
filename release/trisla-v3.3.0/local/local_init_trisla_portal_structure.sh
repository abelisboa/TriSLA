#!/bin/bash
# ============================================================
# Script: local_init_trisla_portal_structure.sh
# Objetivo: Criar a estrutura completa do TriSLA Portal
# Autor: Abel Lisboa (TriSLA@NASP)
# ============================================================

set -e
BASE_DIR="$(dirname "$(pwd)")"

echo "🚀 Iniciando criação da estrutura TriSLA Portal em: $BASE_DIR"

# 1. Estrutura principal
mkdir -p $BASE_DIR/apps/api
mkdir -p $BASE_DIR/apps/ui
mkdir -p $BASE_DIR/helm/trisla-portal/templates

# ------------------------------------------------------------
# 2. Backend (FastAPI)
# ------------------------------------------------------------
cat <<'EOF' > $BASE_DIR/apps/api/main.py
from fastapi import FastAPI

app = FastAPI(title="TriSLA API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "TriSLA API running successfully!"}

@app.get("/status")
def status():
    return {"status": "OK", "module": "SEM-NSMF", "description": "Semantic interface operational"}
EOF

cat <<'EOF' > $BASE_DIR/apps/api/requirements.txt
fastapi
uvicorn
pydantic
requests
EOF

# ------------------------------------------------------------
# 3. Frontend (React + Vite)
# ------------------------------------------------------------
cat <<'EOF' > $BASE_DIR/apps/ui/package.json
{
  "name": "trisla-portal",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "vite": "^5.1.0"
  }
}
EOF

cat <<'EOF' > $BASE_DIR/apps/ui/index.html
<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <title>TriSLA Portal</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/main.jsx"></script>
  </body>
</html>
EOF

cat <<'EOF' > $BASE_DIR/apps/ui/main.jsx
import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <div style={{ textAlign: "center", marginTop: "10%" }}>
      <h1>TriSLA Portal</h1>
      <p>Interface de gerenciamento de SLAs em redes 5G/O-RAN</p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
EOF

# ------------------------------------------------------------
# 4. Helm Chart
# ------------------------------------------------------------
cat <<'EOF' > $BASE_DIR/helm/trisla-portal/Chart.yaml
apiVersion: v2
name: trisla-portal
version: 0.1.0
description: Helm chart para implantação do TriSLA Portal (Frontend + Backend)
EOF

cat <<'EOF' > $BASE_DIR/helm/trisla-portal/values.yaml
backend:
  image: trisla/api:latest
  port: 8000

frontend:
  image: trisla/ui:latest
  port: 3000
EOF

cat <<'EOF' > $BASE_DIR/helm/trisla-portal/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trisla-portal
spec:
  replicas: 1
  selector:
    matchLabels:
      app: trisla-portal
  template:
    metadata:
      labels:
        app: trisla-portal
    spec:
      containers:
      - name: trisla-api
        image: trisla/api:latest
        ports:
        - containerPort: 8000
      - name: trisla-ui
        image: trisla/ui:latest
        ports:
        - containerPort: 3000
EOF

echo "✅ Estrutura TriSLA Portal criada com sucesso!"
echo "📁 Localização: $BASE_DIR"
