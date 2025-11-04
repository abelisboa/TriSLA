#!/bin/bash
# Copiar arquivos usando caminhos completos

# Caminhos locais (WSL)
LOCAL_BASE="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal"

# Node1
NODE1_HOST="porvir5g@192.168.10.16"
NODE1_BASE="/home/porvir5g/gtp5g/trisla-portal"

echo "=========================================="
echo "📤 Copiando com Caminhos Completos"
echo "=========================================="
echo ""

# Arquivo 1: prometheus.py
echo "1️⃣ Copiando: prometheus.py"
LOCAL_FILE="${LOCAL_BASE}/apps/api/prometheus.py"
REMOTE_FILE="${NODE1_BASE}/apps/api/prometheus.py"

if [ -f "$LOCAL_FILE" ]; then
    echo "   Origem: $LOCAL_FILE"
    echo "   Destino: ${NODE1_HOST}:${REMOTE_FILE}"
    
    ssh "${NODE1_HOST}" "mkdir -p $(dirname ${REMOTE_FILE})"
    scp "$LOCAL_FILE" "${NODE1_HOST}:${REMOTE_FILE}"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Sucesso!"
    else
        echo "   ❌ Falha!"
    fi
else
    echo "   ⚠️  Arquivo não encontrado: $LOCAL_FILE"
fi
echo ""

# Arquivo 2: DashboardComplete.jsx
echo "2️⃣ Copiando: DashboardComplete.jsx"
LOCAL_FILE="${LOCAL_BASE}/apps/ui/src/pages/DashboardComplete.jsx"
REMOTE_FILE="${NODE1_BASE}/apps/ui/src/pages/DashboardComplete.jsx"

if [ -f "$LOCAL_FILE" ]; then
    echo "   Origem: $LOCAL_FILE"
    echo "   Destino: ${NODE1_HOST}:${REMOTE_FILE}"
    
    ssh "${NODE1_HOST}" "mkdir -p $(dirname ${REMOTE_FILE})"
    scp "$LOCAL_FILE" "${NODE1_HOST}:${REMOTE_FILE}"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Sucesso!"
    else
        echo "   ❌ Falha!"
    fi
else
    echo "   ⚠️  Arquivo não encontrado: $LOCAL_FILE"
fi
echo ""

# Arquivo 3: SlicesManagement.jsx
echo "3️⃣ Copiando: SlicesManagement.jsx"
LOCAL_FILE="${LOCAL_BASE}/apps/ui/src/pages/SlicesManagement.jsx"
REMOTE_FILE="${NODE1_BASE}/apps/ui/src/pages/SlicesManagement.jsx"

if [ -f "$LOCAL_FILE" ]; then
    echo "   Origem: $LOCAL_FILE"
    echo "   Destino: ${NODE1_HOST}:${REMOTE_FILE}"
    
    ssh "${NODE1_HOST}" "mkdir -p $(dirname ${REMOTE_FILE})"
    scp "$LOCAL_FILE" "${NODE1_HOST}:${REMOTE_FILE}"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Sucesso!"
    else
        echo "   ❌ Falha!"
    fi
else
    echo "   ⚠️  Arquivo não encontrado: $LOCAL_FILE"
fi
echo ""

echo "=========================================="
echo "✅ Cópia concluída!"
echo "=========================================="




