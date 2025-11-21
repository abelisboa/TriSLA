#!/bin/bash
# ============================================
# TriSLA - Iniciar Ambiente Local Completo
# ============================================

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     TriSLA - Iniciando Ambiente Local Completo          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está disponível
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não está instalado."
    exit 1
fi

# Usar docker compose (v2) ou docker-compose (v1)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "📦 Construindo imagens Docker..."
$DOCKER_COMPOSE build

echo ""
echo "🚀 Iniciando todos os serviços..."
$DOCKER_COMPOSE up -d

echo ""
echo "⏳ Aguardando serviços iniciarem (30 segundos)..."
sleep 30

echo ""
echo "📊 Verificando status dos serviços..."
$DOCKER_COMPOSE ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Ambiente TriSLA iniciado com sucesso!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Endpoints disponíveis:"
echo "   • UI Dashboard:        http://localhost:80"
echo "   • SEM-CSMF:            http://localhost:8080"
echo "   • ML-NSMF:             http://localhost:8081"
echo "   • Decision Engine:     http://localhost:8082"
echo "   • BC-NSSMF:            http://localhost:8083"
echo "   • SLA-Agent Layer:      http://localhost:8084"
echo "   • NASP Adapter:        http://localhost:8085 (MOCK)"
echo "   • Prometheus:          http://localhost:9090"
echo "   • Grafana:             http://localhost:3000 (admin/admin)"
echo "   • Kafka:                localhost:29092"
echo ""
echo "📝 Comandos úteis:"
echo "   • Ver logs:            $DOCKER_COMPOSE logs -f [serviço]"
echo "   • Parar serviços:     $DOCKER_COMPOSE down"
echo "   • Reiniciar serviço:  $DOCKER_COMPOSE restart [serviço]"
echo "   • Status:             $DOCKER_COMPOSE ps"
echo ""
echo "🧪 Para executar testes:"
echo "   • Testes unitários:   pytest tests/unit/ -v"
echo "   • Testes integração:   pytest tests/integration/ -v"
echo "   • Validação local:    ./scripts/validate-local.ps1"
echo ""

