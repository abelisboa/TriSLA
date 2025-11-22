#!/usr/bin/env bash
# Script para iniciar ambiente E2E local completo do TriSLA
# Inicia infraestrutura, NASP Adapter e módulos TriSLA na ordem correta

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "============================================================"
echo "🚀 Iniciando Ambiente E2E Local - TriSLA"
echo "============================================================"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para verificar saúde de serviço
check_health() {
    local service=$1
    local url=$2
    local max_attempts=${3:-30}
    local attempt=0
    
    echo -e "${YELLOW}⏳ Aguardando $service ficar saudável...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service está saudável${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo -e "${RED}❌ $service não ficou saudável após $max_attempts tentativas${NC}"
    return 1
}

# 1. Subir infraestrutura básica
echo ""
echo "============================================================"
echo "1️⃣ Subindo infraestrutura básica..."
echo "============================================================"

docker compose up -d zookeeper kafka postgres

echo "⏳ Aguardando Zookeeper e Kafka..."
sleep 10

# Verificar Kafka
if docker exec trisla-kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Kafka está pronto${NC}"
else
    echo -e "${RED}❌ Kafka não está pronto${NC}"
    exit 1
fi

# 2. Subir observabilidade
echo ""
echo "============================================================"
echo "2️⃣ Subindo stack de observabilidade..."
echo "============================================================"

docker compose up -d prometheus grafana otlp-collector

# Verificar Prometheus
check_health "Prometheus" "http://localhost:9090/-/healthy" 15 || true

# Verificar Grafana
check_health "Grafana" "http://localhost:3000/api/health" 15 || true

# 3. Subir Besu (Blockchain)
echo ""
echo "============================================================"
echo "3️⃣ Subindo Besu (Ethereum Permissionado)..."
echo "============================================================"

docker compose up -d besu-dev

# Verificar Besu
check_health "Besu" "http://localhost:8545" 20 || true

# Aguardar Besu inicializar completamente
echo "⏳ Aguardando Besu inicializar completamente..."
sleep 15

# Verificar se Besu está respondendo
if curl -sf -X POST http://localhost:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Besu está respondendo${NC}"
else
    echo -e "${YELLOW}⚠️ Besu pode não estar totalmente pronto, mas continuando...${NC}"
fi

# 4. Subir NASP Adapter (modo real/mocked controlado)
echo ""
echo "============================================================"
echo "4️⃣ Subindo NASP Adapter..."
echo "============================================================"

docker compose up -d nasp-adapter mock-nasp-ran mock-nasp-transport mock-nasp-core

# Verificar NASP Adapter
check_health "NASP Adapter" "http://localhost:8085/health" 15 || true

# 5. Subir módulos TriSLA na ordem correta
echo ""
echo "============================================================"
echo "5️⃣ Subindo módulos TriSLA..."
echo "============================================================"

# Ordem de inicialização baseada em dependências:
# 1. SEM-CSMF (base, não depende de outros módulos TriSLA)
echo "📦 Iniciando SEM-CSMF..."
docker compose up -d sem-csmf
check_health "SEM-CSMF" "http://localhost:8080/health" 20 || true

# 2. ML-NSMF (depende de Kafka, recebe I-02 de SEM-CSMF)
echo "📦 Iniciando ML-NSMF..."
docker compose up -d ml-nsmf
check_health "ML-NSMF" "http://localhost:8081/health" 20 || true

# 3. Decision Engine (depende de SEM-CSMF via gRPC I-01, recebe I-03 de ML-NSMF)
echo "📦 Iniciando Decision Engine..."
docker compose up -d decision-engine
check_health "Decision Engine" "http://localhost:8082/health" 20 || true

# 4. BC-NSSMF (depende de Besu, recebe I-04 de Decision Engine)
echo "📦 Iniciando BC-NSSMF..."
docker compose up -d bc-nssmf
check_health "BC-NSSMF" "http://localhost:8083/health" 20 || true

# 5. SLA-Agent Layer (depende de NASP Adapter, recebe I-05 de Decision Engine)
echo "📦 Iniciando SLA-Agent Layer..."
docker compose up -d sla-agent-layer
check_health "SLA-Agent Layer" "http://localhost:8084/health" 20 || true

# 6. Criar tópicos Kafka necessários
echo ""
echo "============================================================"
echo "6️⃣ Criando tópicos Kafka..."
echo "============================================================"

KAFKA_TOPICS=(
    "I-02-intent-to-ml"
    "I-03-ml-predictions"
    "trisla-i04-decisions"
    "trisla-i05-actions"
    "trisla-i06-agent-events"
    "trisla-i07-agent-actions"
)

for topic in "${KAFKA_TOPICS[@]}"; do
    if docker exec trisla-kafka kafka-topics --create \
        --topic "$topic" \
        --bootstrap-server localhost:9092 \
        --if-not-exists \
        --partitions 1 \
        --replication-factor 1 2>/dev/null; then
        echo -e "${GREEN}✅ Tópico $topic criado${NC}"
    else
        echo -e "${YELLOW}⚠️ Tópico $topic já existe ou erro ao criar${NC}"
    fi
done

# 7. Verificação final
echo ""
echo "============================================================"
echo "7️⃣ Verificação final de saúde..."
echo "============================================================"

SERVICES=(
    "SEM-CSMF:http://localhost:8080/health"
    "ML-NSMF:http://localhost:8081/health"
    "Decision Engine:http://localhost:8082/health"
    "BC-NSSMF:http://localhost:8083/health"
    "SLA-Agent Layer:http://localhost:8084/health"
    "NASP Adapter:http://localhost:8085/health"
)

ALL_HEALTHY=true
for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_name service_url <<< "$service_info"
    if check_health "$service_name" "$service_url" 5; then
        echo -e "${GREEN}✅ $service_name: OK${NC}"
    else
        echo -e "${RED}❌ $service_name: FALHOU${NC}"
        ALL_HEALTHY=false
    fi
done

# 8. Resumo
echo ""
echo "============================================================"
echo "📊 Resumo do Ambiente E2E"
echo "============================================================"

echo ""
echo "Serviços rodando:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✅ Ambiente E2E iniciado com sucesso!${NC}"
    echo ""
    echo "Endpoints disponíveis:"
    echo "  - SEM-CSMF:        http://localhost:8080"
    echo "  - ML-NSMF:          http://localhost:8081"
    echo "  - Decision Engine:  http://localhost:8082"
    echo "  - BC-NSSMF:         http://localhost:8083"
    echo "  - SLA-Agent Layer: http://localhost:8084"
    echo "  - NASP Adapter:     http://localhost:8085"
    echo "  - Prometheus:       http://localhost:9090"
    echo "  - Grafana:          http://localhost:3000 (admin/admin)"
    echo "  - Besu RPC:         http://localhost:8545"
    echo ""
    echo "Para executar testes E2E:"
    echo "  pytest tests/e2e/test_trisla_e2e.py -v"
    echo ""
    echo "Para parar o ambiente:"
    echo "  docker compose down"
else
    echo -e "${YELLOW}⚠️ Alguns serviços podem não estar totalmente saudáveis${NC}"
    echo "Verifique os logs com: docker compose logs [service-name]"
fi

echo ""
echo "============================================================"


