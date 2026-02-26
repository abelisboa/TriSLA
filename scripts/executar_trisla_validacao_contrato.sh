#!/bin/bash
# Script para executar Solicitação Controlada de SLAs ACCEPT para Validação Contratual (TriSLA)

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
PORTAL_URL="http://192.168.10.16:32002"
OUTPUT_DIR="logs/trisla_validacao_contrato_$(date +%Y%m%d_%H%M%S)"
NAMESPACE="trisla"

mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TriSLA - Validação Contratual${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Diretório de evidências: ${GREEN}$OUTPUT_DIR${NC}"
echo ""

submit_sla() {
    local sla_name=$1
    local payload=$2
    local output_file="$OUTPUT_DIR/${sla_name}_response.json"
    
    echo -e "${YELLOW}[$sla_name]${NC} Submetendo SLA..."
    echo "$payload" > "$OUTPUT_DIR/${sla_name}_request.json"
    
    local response=$(curl -s -w "\n%{http_code}" -X POST "$PORTAL_URL/api/v1/sla/submit" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    echo "$body" > "$output_file"
    
    echo -e "  HTTP Status: ${BLUE}$http_code${NC}"
    echo -e "  Resposta salva em: ${GREEN}$output_file${NC}"
    
    if echo "$body" | grep -qi "accept\|confirmed"; then
        echo -e "  ${GREEN}✓ ACCEPT/CONFIRMED detectado${NC}"
    else
        echo -e "  ${RED}✗ Não é ACCEPT${NC}"
    fi
    echo ""
}

collect_logs() {
    local sla_name=$1
    echo -e "${YELLOW}[$sla_name]${NC} Coletando logs..."
    
    local de_pod=$(kubectl get pods -n "$NAMESPACE" -l app=trisla-decision-engine -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    if [ -n "$de_pod" ]; then
        kubectl logs -n "$NAMESPACE" "$de_pod" --tail=100 > "$OUTPUT_DIR/${sla_name}_decision_engine.log" 2>&1 || true
    fi
    
    local bc_pod=$(kubectl get pods -n "$NAMESPACE" -l app=trisla-bc-nssmf -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    if [ -n "$bc_pod" ]; then
        kubectl logs -n "$NAMESPACE" "$bc_pod" --tail=100 > "$OUTPUT_DIR/${sla_name}_bc_nssmf.log" 2>&1 || true
    fi
    
    local besu_pod=$(kubectl get pods -n "$NAMESPACE" -l app=trisla-besu -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    if [ -n "$besu_pod" ]; then
        kubectl logs -n "$NAMESPACE" "$besu_pod" --tail=100 > "$OUTPUT_DIR/${sla_name}_besu.log" 2>&1 || true
    fi
    echo ""
}

wait_for_decision() {
    local sla_name=$1
    echo -e "${YELLOW}[$sla_name]${NC} Aguardando processamento (5s)..."
    sleep 5
    echo ""
}

# Verificar ambiente
echo -e "${BLUE}Verificando ambiente...${NC}"
if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    echo -e "${RED}ERRO: Namespace $NAMESPACE não encontrado!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Namespace $NAMESPACE encontrado${NC}"
echo ""

# SLA eMBB #1
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SLA eMBB #1${NC}"
EMBB1_PAYLOAD='{"template_id":"template:eMBB","intent":"eMBB_controlado_validacao_contrato_01","tenant_id":"default","form_values":{"service_type":"eMBB","latency_max_ms":50,"throughput_min_mbps":50,"availability_target":99.0}}'
submit_sla "embb_01" "$EMBB1_PAYLOAD"
wait_for_decision "embb_01"
collect_logs "embb_01"

# SLA eMBB #2
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SLA eMBB #2${NC}"
EMBB2_PAYLOAD='{"template_id":"template:eMBB","intent":"eMBB_controlado_validacao_contrato_02","tenant_id":"default","form_values":{"service_type":"eMBB","latency_max_ms":60,"throughput_min_mbps":40,"availability_target":98.5}}'
submit_sla "embb_02" "$EMBB2_PAYLOAD"
wait_for_decision "embb_02"
collect_logs "embb_02"

# SLA URLLC #1
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SLA URLLC #1${NC}"
URLLC1_PAYLOAD='{"template_id":"template:URLLC","intent":"URLLC_controlado_validacao_contrato_01","tenant_id":"default","form_values":{"service_type":"URLLC","latency_max_ms":15,"reliability_target":99.9,"jitter_max_ms":5}}'
submit_sla "urllc_01" "$URLLC1_PAYLOAD"
wait_for_decision "urllc_01"
collect_logs "urllc_01"

# SLA URLLC #2
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SLA URLLC #2${NC}"
URLLC2_PAYLOAD='{"template_id":"template:URLLC","intent":"URLLC_controlado_validacao_contrato_02","tenant_id":"default","form_values":{"service_type":"URLLC","latency_max_ms":20,"reliability_target":99.8,"jitter_max_ms":6}}'
submit_sla "urllc_02" "$URLLC2_PAYLOAD"
wait_for_decision "urllc_02"
collect_logs "urllc_02"

# SLA mMTC #1
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SLA mMTC #1${NC}"
mMTC1_PAYLOAD='{"template_id":"template:mMTC","intent":"mMTC_controlado_validacao_contrato_01","tenant_id":"default","form_values":{"service_type":"mMTC","device_density":1000,"latency_max_ms":200,"availability_target":97.0}}'
submit_sla "mmtc_01" "$mMTC1_PAYLOAD"
wait_for_decision "mmtc_01"
collect_logs "mmtc_01"

# SLA mMTC #2
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SLA mMTC #2${NC}"
mMTC2_PAYLOAD='{"template_id":"template:mMTC","intent":"mMTC_controlado_validacao_contrato_02","tenant_id":"default","form_values":{"service_type":"mMTC","device_density":800,"latency_max_ms":250,"availability_target":96.5}}'
submit_sla "mmtc_02" "$mMTC2_PAYLOAD"
wait_for_decision "mmtc_02"
collect_logs "mmtc_02"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Resumo da Execução${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Diretório de evidências: ${GREEN}$OUTPUT_DIR${NC}"
echo -e "${GREEN}✓ Execução concluída!${NC}"
echo ""
