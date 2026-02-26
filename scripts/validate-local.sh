#!/bin/bash
# ============================================
# Script: Validação e Testes Locais do TriSLA
# ============================================
# Executa validações e testes que podem ser feitos na máquina local
# ============================================

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     TriSLA - Validação e Testes Locais                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Diretório base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

# Função para verificar se um serviço está rodando
check_service() {
    local service=$1
    local port=$2
    
    if command -v nc >/dev/null 2>&1; then
        if nc -z localhost "$port" 2>/dev/null; then
            echo -e "${GREEN}✅${NC} $service está rodando na porta $port"
            return 0
        else
            echo -e "${YELLOW}⚠️${NC} $service não está rodando na porta $port"
            return 1
        fi
    elif command -v curl >/dev/null 2>&1; then
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
            echo -e "${GREEN}✅${NC} $service está rodando na porta $port"
            return 0
        else
            echo -e "${YELLOW}⚠️${NC} $service não está rodando na porta $port"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️${NC} Não foi possível verificar $service (nc/curl não disponível)"
        return 1
    fi
}

# 1. Verificar Health dos Módulos
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Verificando Health dos Módulos"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

check_service "SEM-CSMF" 8080
check_service "ML-NSMF" 8081
check_service "Decision Engine" 8082
check_service "BC-NSSMF" 8083
check_service "SLA-Agent Layer" 8084
check_service "NASP Adapter" 8085

echo ""

# 2. Testar Endpoints de Health
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Testando Endpoints de Health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_health_endpoint() {
    local module=$1
    local port=$2
    local url="http://localhost:$port/health"
    
    echo "Testando $module ($url)..."
    if response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        
        if [ "$http_code" = "200" ]; then
            echo -e "${GREEN}✅${NC} $module: $body"
            echo ""
            return 0
        else
            echo -e "${RED}❌${NC} $module retornou HTTP $http_code"
            echo ""
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️${NC} $module não está acessível"
        echo ""
        return 1
    fi
}

test_health_endpoint "SEM-CSMF" 8080
test_health_endpoint "ML-NSMF" 8081
test_health_endpoint "Decision Engine" 8082
test_health_endpoint "BC-NSSMF" 8083
test_health_endpoint "SLA-Agent Layer" 8084
test_health_endpoint "NASP Adapter" 8085

# 3. Testar Interfaces I-01 a I-07
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Testando Interfaces I-01 a I-07"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Executando testes de integração..."
if [ -f "tests/integration/test_interfaces.py" ]; then
    if command -v pytest >/dev/null 2>&1; then
        pytest tests/integration/test_interfaces.py -v || echo -e "${YELLOW}⚠️${NC} Alguns testes falharam (pode ser esperado se serviços não estiverem rodando)"
    else
        echo -e "${YELLOW}⚠️${NC} pytest não está instalado. Instale com: pip install pytest"
    fi
else
    echo -e "${YELLOW}⚠️${NC} Arquivo de testes não encontrado: tests/integration/test_interfaces.py"
fi

echo ""

# 4. Verificar OTLP Collector
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Verificando OTLP Collector"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

check_service "OTLP Collector" 4317
check_service "OTLP Collector (HTTP)" 4318

if [ -f "monitoring/otel-collector/config.yaml" ]; then
    echo -e "${GREEN}✅${NC} Configuração do OTLP Collector encontrada"
else
    echo -e "${YELLOW}⚠️${NC} Configuração do OTLP Collector não encontrada"
fi

echo ""

# 5. Verificar Métricas TriSLA
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Verificando Métricas TriSLA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

check_service "Prometheus" 9090

if [ -f "monitoring/prometheus/prometheus.yml" ]; then
    echo -e "${GREEN}✅${NC} Configuração do Prometheus encontrada"
else
    echo -e "${YELLOW}⚠️${NC} Configuração do Prometheus não encontrada"
fi

if [ -f "monitoring/prometheus/rules/slo-rules.yml" ]; then
    echo -e "${GREEN}✅${NC} Regras SLO do Prometheus encontradas"
else
    echo -e "${YELLOW}⚠️${NC} Regras SLO do Prometheus não encontradas"
fi

echo ""

# 6. Verificar Traces
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Verificando Traces"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar se há traces sendo coletados (requer OTLP Collector rodando)
if check_service "OTLP Collector" 4317; then
    echo -e "${GREEN}✅${NC} OTLP Collector está disponível para receber traces"
else
    echo -e "${YELLOW}⚠️${NC} OTLP Collector não está disponível"
fi

echo ""

# 7. Verificar SLO Reports
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Verificando SLO Reports"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "monitoring/slo-reports/generator.py" ]; then
    echo -e "${GREEN}✅${NC} Gerador de SLO Reports encontrado"
    
    if command -v python3 >/dev/null 2>&1; then
        echo "Testando gerador de SLO Reports..."
        cd monitoring/slo-reports
        if python3 -c "import generator" 2>/dev/null; then
            echo -e "${GREEN}✅${NC} Gerador de SLO Reports está funcional"
        else
            echo -e "${YELLOW}⚠️${NC} Gerador de SLO Reports tem dependências faltando"
        fi
        cd "$BASE_DIR"
    else
        echo -e "${YELLOW}⚠️${NC} Python3 não está instalado"
    fi
else
    echo -e "${YELLOW}⚠️${NC} Gerador de SLO Reports não encontrado"
fi

echo ""

# 8. Verificar Logs do SLO Reporter
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  Verificando Logs do SLO Reporter"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "monitoring/slo-reports" ]; then
    if [ -f "monitoring/slo-reports/generator.py" ]; then
        echo -e "${GREEN}✅${NC} Script do SLO Reporter encontrado"
        echo "Para ver logs do SLO Reporter, execute:"
        echo "  python3 monitoring/slo-reports/generator.py"
    else
        echo -e "${YELLOW}⚠️${NC} Script do SLO Reporter não encontrado"
    fi
else
    echo -e "${YELLOW}⚠️${NC} Diretório de SLO Reports não encontrado"
fi

echo ""

# Resumo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Resumo da Validação"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Para executar testes completos, certifique-se de que:"
echo "  1. Todos os módulos estão rodando (ou use Docker Compose)"
echo "  2. OTLP Collector está configurado e rodando"
echo "  3. Prometheus está configurado e rodando"
echo "  4. Kafka está disponível (para testes de interfaces I-03, I-04, I-05)"
echo ""
echo "Para iniciar todos os serviços localmente:"
echo "  docker-compose up -d"
echo ""
echo "Para executar testes automatizados:"
echo "  pytest tests/ -v"
echo ""

