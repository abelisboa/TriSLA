#!/bin/bash
# Verificar e completar arquivos no node1

echo "=========================================="
echo "🔍 Verificando Arquivos Criados"
echo "=========================================="
echo ""

# Verificar prometheus.py
echo "1️⃣ Verificando apps/api/prometheus.py..."
if [ -f "apps/api/prometheus.py" ]; then
    LINES=$(wc -l < apps/api/prometheus.py)
    echo "   Arquivo existe com $LINES linhas"
    if [ $LINES -lt 100 ]; then
        echo "   ⚠️  Arquivo parece incompleto (menos de 100 linhas)"
        echo "   Precisa recriar"
    else
        echo "   ✅ Arquivo parece completo"
        tail -5 apps/api/prometheus.py
    fi
else
    echo "   ❌ Arquivo não encontrado"
fi
echo ""

# Verificar main.py
echo "2️⃣ Verificando router no apps/api/main.py..."
if grep -q "prometheus_router" apps/api/main.py; then
    echo "   ✅ Router encontrado"
    grep -A 3 "prometheus_router" apps/api/main.py | head -5
else
    echo "   ❌ Router não encontrado"
fi
echo ""

# Verificar se API está rodando
echo "3️⃣ Verificando se API está acessível..."
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ API está rodando"
else
    echo "   ⚠️  API não está acessível em localhost:8000"
    echo "   Precisa iniciar/reiniciar o serviço"
fi
echo ""

echo "=========================================="
echo "✅ Verificação completa"
echo "=========================================="




