#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# TriSLA Pipeline Test Script
# Testa o pipeline completo: Intent → SEM-CSMF → Decision Engine
# ============================================================

NAMESPACE="trisla"
LOG_FILE="/tmp/trisla-pipeline-test.log"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "============================================================"
log "TriSLA Pipeline Test - Iniciando"
log "============================================================"

# 1. Descobrir IPs e portas dos serviços
log "Descobrindo IPs e portas dos serviços..."

SEM_IP=$(kubectl -n "$NAMESPACE" get svc trisla-sem-csmf -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
SEM_PORT=$(kubectl -n "$NAMESPACE" get svc trisla-sem-csmf -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "8080")

DE_IP=$(kubectl -n "$NAMESPACE" get svc trisla-decision-engine -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
DE_PORT=$(kubectl -n "$NAMESPACE" get svc trisla-decision-engine -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "8082")

if [ -z "$SEM_IP" ] || [ -z "$DE_IP" ]; then
    log "❌ ERRO: Não foi possível obter IPs dos serviços"
    exit 1
fi

log "  SEM-CSMF: $SEM_IP:$SEM_PORT"
log "  Decision Engine: $DE_IP:$DE_PORT"

# 2. Criar intenção completa
log ""
log "Criando intenção no SEM-CSMF..."

INTENT_ID="intent-test-$(date +%s)"
INTENT_PAYLOAD=$(cat <<JSON
{
  "intent_id": "$INTENT_ID",
  "intent": "cirurgia remota",
  "service_type": "URLLC",
  "sla_requirements": {
    "latency": "10ms",
    "reliability": 0.999,
    "bandwidth": "100Mbps"
  },
  "context": {
    "tenant": "hospital-x",
    "location": "OR-1",
    "priority": "high"
  }
}
JSON
)

log "  Payload: $INTENT_PAYLOAD"

INTENT_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "http://$SEM_IP:$SEM_PORT/api/v1/intents" \
  -H "Content-Type: application/json" \
  -d "$INTENT_PAYLOAD" \
  --max-time 10 2>&1) || {
    log "❌ ERRO: Falha ao enviar intent ao SEM-CSMF"
    exit 1
}

HTTP_CODE=$(echo "$INTENT_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
INTENT_BODY=$(echo "$INTENT_RESPONSE" | sed '/HTTP_CODE:/d')

log "  Resposta HTTP: $HTTP_CODE"
log "  Corpo da resposta:"
echo "$INTENT_BODY" | jq . 2>/dev/null || echo "$INTENT_BODY" | tee -a "$LOG_FILE"

# Salvar resposta
echo "$INTENT_BODY" > /tmp/trisla-intent-response.json

# 3. Extrair intent_id e nest_id (se existir)
if command -v jq >/dev/null 2>&1; then
    EXTRACTED_INTENT_ID=$(echo "$INTENT_BODY" | jq -r '.intent_id // .id // empty' 2>/dev/null || echo "")
    NEST_ID=$(echo "$INTENT_BODY" | jq -r '.nest_id // .network_slice_id // empty' 2>/dev/null || echo "")
    
    if [ -z "$EXTRACTED_INTENT_ID" ]; then
        EXTRACTED_INTENT_ID="$INTENT_ID"
    fi
    
    log ""
    log "Intent ID extraído: $EXTRACTED_INTENT_ID"
    if [ -n "$NEST_ID" ]; then
        log "NEST ID extraído: $NEST_ID"
    fi
else
    log "⚠️ jq não disponível, usando intent_id original: $INTENT_ID"
    EXTRACTED_INTENT_ID="$INTENT_ID"
fi

# 4. Chamar Decision Engine
log ""
log "Chamando Decision Engine para decidir sobre o intent..."

DECISION_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "http://$DE_IP:$DE_PORT/api/v1/decide/intent/$EXTRACTED_INTENT_ID" \
  -H "Content-Type: application/json" \
  -d '{}' \
  --max-time 10 2>&1) || {
    log "⚠️ Aviso: Falha ao chamar Decision Engine (pode ser esperado se o endpoint for diferente)"
    DECISION_RESPONSE=""
}

if [ -n "$DECISION_RESPONSE" ]; then
    DE_HTTP_CODE=$(echo "$DECISION_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
    DE_BODY=$(echo "$DECISION_RESPONSE" | sed '/HTTP_CODE:/d')
    
    log "  Resposta HTTP: $DE_HTTP_CODE"
    log "  Corpo da resposta:"
    echo "$DE_BODY" | jq . 2>/dev/null || echo "$DE_BODY" | tee -a "$LOG_FILE"
    
    # Salvar resposta
    echo "$DE_BODY" > /tmp/trisla-decision-response.json
    
    # Extrair campos principais
    if command -v jq >/dev/null 2>&1; then
        DECISION_ID=$(echo "$DE_BODY" | jq -r '.decision_id // .id // empty' 2>/dev/null || echo "")
        ACTION=$(echo "$DE_BODY" | jq -r '.action // .decision // empty' 2>/dev/null || echo "")
        CONFIDENCE=$(echo "$DE_BODY" | jq -r '.confidence // .score // empty' 2>/dev/null || echo "")
        REASONING=$(echo "$DE_BODY" | jq -r '.reasoning // .reason // .explanation // empty' 2>/dev/null || echo "")
        
        log ""
        log "============================================================"
        log "RESUMO DA DECISÃO"
        log "============================================================"
        log "  Decision ID: $DECISION_ID"
        log "  Action: $ACTION"
        log "  Confidence: $CONFIDENCE"
        log "  Reasoning: $REASONING"
    fi
fi

log ""
log "============================================================"
log "Teste do pipeline concluído"
log "============================================================"
log "Arquivos salvos:"
log "  - /tmp/trisla-intent-response.json"
log "  - /tmp/trisla-decision-response.json"
log "  - $LOG_FILE"
