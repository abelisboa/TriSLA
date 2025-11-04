#!/usr/bin/env bash
# ============================================================
# Fix Port Conflict - TriSLA Dashboard v3.2.4
# Resolve conflitos de porta (5000, 5174)
# ============================================================

set -e

echo "======================================================"
echo "🔧 Fix Port Conflict - TriSLA Dashboard v3.2.4"
echo "======================================================"
echo ""

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down 2>/dev/null || true

# Verificar e parar containers individuais
for container in trisla-dashboard-backend trisla-dashboard-frontend; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "   Parando: ${container}"
        docker stop "${container}" 2>/dev/null || true
        docker rm "${container}" 2>/dev/null || true
    fi
done

echo ""
echo "✅ Containers parados"
echo ""

# Verificar portas (Linux/WSL)
if command -v lsof &> /dev/null; then
    echo "🔍 Verificando uso de portas..."
    if lsof -ti:5000 &> /dev/null; then
        echo "⚠️  Porta 5000 em uso"
        echo "   Processos:"
        lsof -ti:5000 | while read pid; do
            ps -p "$pid" -o pid,cmd 2>/dev/null || true
        done
        echo ""
        read -p "Deseja matar processos na porta 5000? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            lsof -ti:5000 | xargs kill -9 2>/dev/null || true
            echo "✅ Processos na porta 5000 finalizados"
        fi
    else
        echo "✅ Porta 5000 livre"
    fi
    
    if lsof -ti:5174 &> /dev/null; then
        echo "⚠️  Porta 5174 em uso"
        echo "   Processos:"
        lsof -ti:5174 | while read pid; do
            ps -p "$pid" -o pid,cmd 2>/dev/null || true
        done
        echo ""
        read -p "Deseja matar processos na porta 5174? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            lsof -ti:5174 | xargs kill -9 2>/dev/null || true
            echo "✅ Processos na porta 5174 finalizados"
        fi
    else
        echo "✅ Porta 5174 livre"
    fi
elif command -v netstat &> /dev/null; then
    echo "🔍 Verificando uso de portas (netstat)..."
    if netstat -tuln | grep -q ":5000"; then
        echo "⚠️  Porta 5000 em uso"
        netstat -tulnp | grep ":5000" || true
    else
        echo "✅ Porta 5000 livre"
    fi
    
    if netstat -tuln | grep -q ":5174"; then
        echo "⚠️  Porta 5174 em uso"
        netstat -tulnp | grep ":5174" || true
    else
        echo "✅ Porta 5174 livre"
    fi
else
    echo "⚠️  Ferramentas de verificação de porta não encontradas"
    echo "   Use manualmente: lsof -i:5000 ou netstat -tuln | grep 5000"
fi

echo ""
echo "======================================================"
echo "✅ Limpeza concluída"
echo "======================================================"
echo ""
echo "Agora você pode executar:"
echo "  docker-compose up -d"
echo ""

