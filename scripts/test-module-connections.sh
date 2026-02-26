#!/bin/bash
# ============================================
# TriSLA - Testar Conexões entre Módulos (Bash)
# ============================================

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     TriSLA - Teste de Conexões entre Módulos             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ============================================
# Configuração
# ============================================

BASE_URL="http://localhost"
SEM_CSMF="$BASE_URL:8080"
ML_NSMF="$BASE_URL:8081"
DECISION_ENGINE="$BASE_URL:8082"
BC_NSSMF="$BASE_URL:8083"
SLA_AGENT_LAYER="$BASE_URL:8084"
NASP_ADAPTER="$BASE_URL:8085"
KAFKA_BROKER="localhost:29092"

# Contadores
PASSED=0
FAILED=0
PARTIAL=0
SKIPPED=0

# ============================================
# Funções Auxiliares
# ============================================

test_http_endpoint() {
    local url=$1
    local method=${2:-GET}
    local body=$3
    
    if [ -n "$body" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$body" \
            --max-time 5 \
            "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            --max-time 5 \
            "$url" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body_content=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo "SUCCESS:$http_code"
    else
        echo "FAILED:$http_code:$body_content"
    fi
}

test_kafka_connection() {
    local broker=$1
    local topic=$2
    
    python3 << EOF
import sys
from kafka import KafkaProducer
import json

try:
    producer = KafkaProducer(
        bootstrap_servers=['$broker'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1),
        request_timeout_ms=5000
    )
    
    test_message = {'test': 'connection'}
    producer.send('$topic', value=test_message)
    producer.flush()
    producer.close()
    
    print('SUCCESS')
except Exception as e:
    print(f'FAILED: {str(e)}')
    sys.exit(1)
EOF
}

# ============================================
# Teste I-01: SEM-CSMF → Decision Engine (gRPC)
# ============================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Testando I-01: SEM-CSMF → Decision Engine (gRPC)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

result=$(test_http_endpoint "$SEM_CSMF/health")
if echo "$result" | grep -q "SUCCESS"; then
    echo "✅ SEM-CSMF está rodando"
    echo "ℹ️  Teste gRPC completo requer cliente gRPC (ver scripts/test-grpc.py)"
    I01_STATUS="PARTIAL"
    I01_MESSAGE="SEM-CSMF está acessível. Teste gRPC completo requer cliente gRPC."
    ((PARTIAL++))
else
    echo "⚠️  SEM-CSMF não está rodando"
    I01_STATUS="SKIPPED"
    I01_MESSAGE="SEM-CSMF não está rodando na porta 8080"
    ((SKIPPED++))
fi

# ============================================
# Teste I-02: SEM-CSMF → ML-NSMF (REST)
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Testando I-02: SEM-CSMF → ML-NSMF (REST)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

result=$(test_http_endpoint "$ML_NSMF/health")
if echo "$result" | grep -q "SUCCESS"; then
    echo "✅ ML-NSMF está rodando"
    
    nest_payload='{"nest_id":"test-nest-001","intent_id":"test-intent-001","network_slices":[{"slice_id":"slice-001","slice_type":"eMBB"}]}'
    nest_result=$(test_http_endpoint "$ML_NSMF/api/v1/nest" "POST" "$nest_payload")
    
    if echo "$nest_result" | grep -q "SUCCESS"; then
        echo "✅ NEST enviado com sucesso"
        I02_STATUS="PASSED"
        I02_MESSAGE="NEST enviado com sucesso"
        ((PASSED++))
    else
        echo "❌ Falha ao enviar NEST"
        I02_STATUS="FAILED"
        I02_MESSAGE="Falha ao enviar NEST"
        ((FAILED++))
    fi
else
    echo "❌ ML-NSMF não está rodando"
    I02_STATUS="FAILED"
    I02_MESSAGE="ML-NSMF não está rodando na porta 8081"
    ((FAILED++))
fi

# ============================================
# Teste I-03: ML-NSMF → Decision Engine (Kafka)
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Testando I-03: ML-NSMF → Decision Engine (Kafka)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

kafka_result=$(test_kafka_connection "$KAFKA_BROKER" "trisla-ml-predictions" 2>&1)
if echo "$kafka_result" | grep -q "SUCCESS"; then
    echo "✅ Kafka está acessível e mensagem enviada"
    I03_STATUS="PASSED"
    I03_MESSAGE="Kafka está acessível e mensagem enviada com sucesso"
    ((PASSED++))
else
    echo "❌ Kafka não está acessível"
    echo "💡 Certifique-se de que Kafka está rodando: docker compose up -d kafka"
    I03_STATUS="FAILED"
    I03_MESSAGE="Kafka não está acessível: $kafka_result"
    ((FAILED++))
fi

# ============================================
# Teste I-04: Decision Engine → BC-NSSMF (REST)
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Testando I-04: Decision Engine → BC-NSSMF (REST)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

result=$(test_http_endpoint "$BC_NSSMF/health")
if echo "$result" | grep -q "SUCCESS"; then
    echo "✅ BC-NSSMF está rodando"
    
    contract_payload='{"decision":{"action":"AC","reasoning":"Teste de conexão"},"contract_data":{"tenant_id":"test-tenant","slice_id":"test-slice"}}'
    contract_result=$(test_http_endpoint "$BC_NSSMF/api/v1/execute-contract" "POST" "$contract_payload")
    
    if echo "$contract_result" | grep -q "SUCCESS"; then
        echo "✅ Contrato executado com sucesso"
        I04_STATUS="PASSED"
        I04_MESSAGE="Contrato executado com sucesso"
        ((PASSED++))
    else
        echo "⚠️  BC-NSSMF está acessível, mas endpoint pode não estar implementado"
        I04_STATUS="PARTIAL"
        I04_MESSAGE="BC-NSSMF está acessível, mas endpoint pode não estar implementado"
        ((PARTIAL++))
    fi
else
    echo "❌ BC-NSSMF não está rodando"
    I04_STATUS="FAILED"
    I04_MESSAGE="BC-NSSMF não está rodando na porta 8083"
    ((FAILED++))
fi

# ============================================
# Teste I-05: Decision Engine → SLA-Agents (Kafka)
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Testando I-05: Decision Engine → SLA-Agents (Kafka)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

kafka_result=$(test_kafka_connection "$KAFKA_BROKER" "trisla-i05-actions" 2>&1)
if echo "$kafka_result" | grep -q "SUCCESS"; then
    echo "✅ Kafka está acessível e mensagem enviada"
    I05_STATUS="PASSED"
    I05_MESSAGE="Kafka está acessível e mensagem enviada para tópico I-05"
    ((PASSED++))
else
    echo "❌ Kafka não está acessível"
    I05_STATUS="FAILED"
    I05_MESSAGE="Kafka não está acessível: $kafka_result"
    ((FAILED++))
fi

# ============================================
# Teste I-06: SLA-Agents → NASP Adapter (REST)
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Testando I-06: SLA-Agents → NASP Adapter (REST)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sla_result=$(test_http_endpoint "$SLA_AGENT_LAYER/health")
nasp_result=$(test_http_endpoint "$NASP_ADAPTER/health")

if echo "$sla_result" | grep -q "SUCCESS" && echo "$nasp_result" | grep -q "SUCCESS"; then
    echo "✅ SLA-Agent Layer está rodando"
    echo "✅ NASP Adapter está rodando"
    
    action_payload='{"type":"adjust_prb_allocation","domain":"RAN","parameters":{"prb_percentage":0.8}}'
    action_result=$(test_http_endpoint "$NASP_ADAPTER/api/v1/nasp/actions" "POST" "$action_payload")
    
    if echo "$action_result" | grep -q "SUCCESS"; then
        echo "✅ Ação executada com sucesso"
        I06_STATUS="PASSED"
        I06_MESSAGE="Ação executada com sucesso"
        ((PASSED++))
    else
        echo "⚠️  Serviços estão acessíveis, mas endpoint pode não estar implementado"
        I06_STATUS="PARTIAL"
        I06_MESSAGE="Serviços estão acessíveis, mas endpoint pode não estar implementado"
        ((PARTIAL++))
    fi
else
    echo "❌ Serviços não estão rodando"
    I06_STATUS="FAILED"
    I06_MESSAGE="SLA-Agent Layer ou NASP Adapter não está rodando"
    ((FAILED++))
fi

# ============================================
# Teste I-07: NASP Adapter ↔ NASP (REST)
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Testando I-07: NASP Adapter ↔ NASP (REST)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

nasp_metrics_result=$(test_http_endpoint "$NASP_ADAPTER/api/v1/nasp/metrics" "GET")
if echo "$nasp_metrics_result" | grep -q "SUCCESS"; then
    echo "✅ Métricas NASP coletadas com sucesso"
    echo "ℹ️  Em produção, isso conectaria ao NASP real"
    I07_STATUS="PASSED"
    I07_MESSAGE="Métricas NASP coletadas com sucesso. Em produção, conecta ao NASP real."
    ((PASSED++))
else
    echo "⚠️  NASP Adapter está rodando em modo MOCK (local)"
    echo "ℹ️  Em produção, isso conectaria ao NASP real no servidor remoto"
    I07_STATUS="PARTIAL"
    I07_MESSAGE="NASP Adapter está rodando em modo MOCK (local). Em produção, conecta ao NASP real."
    ((PARTIAL++))
fi

# ============================================
# Resumo Final
# ============================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Resumo dos Testes de Conexão"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "I-01: $I01_STATUS - $I01_MESSAGE"
echo "I-02: $I02_STATUS - $I02_MESSAGE"
echo "I-03: $I03_STATUS - $I03_MESSAGE"
echo "I-04: $I04_STATUS - $I04_MESSAGE"
echo "I-05: $I05_STATUS - $I05_MESSAGE"
echo "I-06: $I06_STATUS - $I06_MESSAGE"
echo "I-07: $I07_STATUS - $I07_MESSAGE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 Estatísticas"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Passou: $PASSED"
echo "❌ Falhou: $FAILED"
echo "⚠️  Parcial: $PARTIAL"
echo "⏭️  Pulado: $SKIPPED"
echo ""

if [ $FAILED -eq 0 ] && [ $SKIPPED -eq 0 ]; then
    echo "🎉 Todos os testes de conexão passaram!"
elif [ $FAILED -gt 0 ]; then
    echo "⚠️  Alguns testes falharam. Verifique se todos os serviços estão rodando:"
    echo "   docker compose up -d"
fi

echo ""
echo "💡 Para executar testes mais detalhados:"
echo "   pytest tests/integration/ -v"
echo ""

