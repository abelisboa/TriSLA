#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
free_port(){ local p="$1"; if lsof -i :"$p" >/dev/null 2>&1; then fuser -k "${p}/tcp" || true; sleep 1; fi }
free_port 5000; free_port 5173
echo "🚀 Iniciando TriSLA Dashboard v3.0 (backend + frontend)"

# Instalar dependências do backend
echo "📦 Instalando dependências do backend..."
python3 -m pip install --user -r backend/requirements.txt >/dev/null

# Verificar se config.yaml existe, se não, copiar do exemplo
if [ ! -f backend/config.yaml ]; then
  echo "📄 Criando arquivo de configuração padrão..."
  cp backend/config.yaml.example backend/config.yaml
fi

# Iniciar o backend
echo "🔄 Iniciando backend..."
( cd backend && uvicorn main:app --host 0.0.0.0 --port 5000 & echo $! > ../.backend.pid ) &
sleep 2

# Iniciar o frontend
echo "🔄 Iniciando frontend..."
cd frontend
if [ ! -d node_modules ]; then 
  echo "📦 Instalando dependências do frontend..."
  npm install --silent
fi
( npm run dev -- --host --port 5173 & echo $! > ../.frontend.pid ) &
sleep 2
cd ..

echo "✅ TriSLA Dashboard v3.0 iniciado com sucesso!"
echo "🔗 UI: http://localhost:5173   |   API: http://localhost:5000"
echo "📊 Prometheus: $PROMETHEUS_URL (configurado em backend/config.yaml)"
echo "🤖 SEM-NSMF: $SEM_NSMF_URL (configurado em backend/config.yaml)"

trap 'kill -9 $(cat .backend.pid .frontend.pid 2>/dev/null) >/dev/null 2>&1 || true; rm -f .backend.pid .frontend.pid' INT TERM
wait