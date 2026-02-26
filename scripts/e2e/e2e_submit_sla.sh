#!/bin/bash

###############################################################
# TriSLA – E2E SLA Submit Test (SSOT)
# Fluxo oficial via Portal Backend
# NÃO cria SLA diretamente em módulos internos
# NÃO altera ambiente
# Apenas valida pipeline completo
###############################################################

set -e

NAMESPACE="trisla"
PORTAL_SERVICE="trisla-portal-backend:8001"
INTENT_TEXT="cirurgia remota com latencia ultra baixa"
SERVICE_TYPE="URLLC"
TENANT="default"

echo ""
echo "=============================================="
echo "TriSLA E2E – SLA SUBMIT TEST"
echo "Namespace : $NAMESPACE"
echo "Portal    : $PORTAL_SERVICE"
echo "Service   : $SERVICE_TYPE"
echo "Intent    : $INTENT_TEXT"
echo "=============================================="
echo ""

echo "🔎 Verificando se namespace existe..."
kubectl get ns $NAMESPACE >/dev/null

echo "🔎 Verificando Portal Backend..."
kubectl get deploy trisla-portal-backend -n $NAMESPACE >/dev/null

echo ""
echo "🚀 Executando requisição E2E..."
echo ""

kubectl run -n $NAMESPACE e2e-submit --rm -i --restart=Never \
  --image=curlimages/curl:8.6.0 -- \
  sh -c "
  curl -sS -X POST http://$PORTAL_SERVICE/api/v1/sla/submit \
  -H 'Content-Type: application/json' \
  -d '{
        \"template_id\": \"default\",
        \"form_values\": {
            \"service_type\": \"$SERVICE_TYPE\",
            \"intent\": \"$INTENT_TEXT\"
        },
        \"tenant_id\": \"$TENANT\"
      }'
"

echo ""
echo ""
echo "✅ E2E execution finished."
echo ""
echo "Se ACCEPT:"
echo "  - Deve existir sla_id"
echo "  - Deve existir blockchain_tx_hash"
echo "  - Deve existir block_number"
echo ""
echo "Se falhar:"
echo "  - Verificar campo 'phase'"
echo "  - Verificar 'reason'"
echo ""
echo "=============================================="
