#!/bin/bash
# Copiar arquivos via jump host - acesso node006 sem senha

# Configuração
JUMP_HOST="porvir5g@ppgca.unisinos.br"
TARGET_HOST="porvir5g@node006"  # Especificar usuário explicitamente
LOCAL_BASE="/mnt/c/Users/USER/Documents/trisla-deploy/trisla-portal"
REMOTE_BASE="/home/porvir5g/gtp5g/trisla-portal"

echo "=========================================="
echo "📤 Copiando via Jump Host (sem senha node006)"
echo "=========================================="
echo ""

# Função para copiar via jump host
copy_via_jump() {
    local local_file="$1"
    local remote_file="$2"
    local description="$3"
    
    echo "📤 Copiando: $description"
    echo "   Origem: $local_file"
    echo "   Destino: ${TARGET_HOST}:${remote_file}"
    
    # Criar diretório remoto via jump host (especificar usuário)
    ssh -J "${JUMP_HOST}" "${TARGET_HOST}" "mkdir -p $(dirname ${remote_file})"
    
    # Copiar arquivo via jump host (especificar usuário)
    scp -o ProxyJump="${JUMP_HOST}" \
        -o StrictHostKeyChecking=no \
        "$local_file" "${TARGET_HOST}:${remote_file}"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Sucesso!"
        return 0
    else
        echo "   ❌ Falha!"
        return 1
    fi
}

# Arquivo 1: prometheus.py
copy_via_jump \
    "${LOCAL_BASE}/apps/api/prometheus.py" \
    "${REMOTE_BASE}/apps/api/prometheus.py" \
    "Backend API Prometheus"
echo ""

# Arquivo 2: DashboardComplete.jsx
copy_via_jump \
    "${LOCAL_BASE}/apps/ui/src/pages/DashboardComplete.jsx" \
    "${REMOTE_BASE}/apps/ui/src/pages/DashboardComplete.jsx" \
    "Dashboard Completo"
echo ""

# Arquivo 3: SlicesManagement.jsx
copy_via_jump \
    "${LOCAL_BASE}/apps/ui/src/pages/SlicesManagement.jsx" \
    "${REMOTE_BASE}/apps/ui/src/pages/SlicesManagement.jsx" \
    "Gestão de Slices"
echo ""

echo "=========================================="
echo "✅ Cópia concluída!"
echo "=========================================="




