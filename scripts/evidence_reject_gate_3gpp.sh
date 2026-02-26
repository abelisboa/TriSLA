#!/usr/bin/env bash
# PROMPT_SREJECT_EVIDENCE_v1.0 — Provar REJECT do Decision Engine (sem depender do Portal)
# Uso: executar dentro do cluster (namespace trisla) ou com port-forward do DE.
# Pré-condição: decisionEngine.gate3gpp.enabled=true e Gate em FAIL (ex.: naspAdapter.gate3gpp.upfMaxSessions=0).
# Saída esperada: HTTP 200, body com "action":"REJECT" e "reasoning" contendo "3GPP_GATE_FAIL".

set -e
DE_URL="${DE_URL:-http://trisla-decision-engine:8082}"
INTENT_ID="ev-reject-$(date +%s)"

PAYLOAD=$(cat <<EOF
{
  "intent_id": "${INTENT_ID}",
  "nest_id": "nest-${INTENT_ID}",
  "intent": {
    "intent_id": "${INTENT_ID}",
    "tenant_id": "default",
    "service_type": "eMBB",
    "sla_requirements": {}
  },
  "nest": {
    "nest_id": "nest-${INTENT_ID}",
    "intent_id": "${INTENT_ID}",
    "network_slices": [],
    "resources": {},
    "status": "generated"
  },
  "context": {}
}
EOF
)

echo "=== PROMPT_SREJECT_EVIDENCE: POST $DE_URL/evaluate (intent_id=$INTENT_ID) ==="
RESP=$(curl -s -w "\n%{http_code}" -X POST "$DE_URL/evaluate" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")
HTTP_BODY=$(echo "$RESP" | head -n -1)
HTTP_CODE=$(echo "$RESP" | tail -n 1)

echo "HTTP $HTTP_CODE"
echo "$HTTP_BODY" | jq . 2>/dev/null || echo "$HTTP_BODY"

ACTION=$(echo "$HTTP_BODY" | jq -r '.action // empty')
REASONING=$(echo "$HTTP_BODY" | jq -r '.reasoning // empty')

if [ "$ACTION" = "REJECT" ] && echo "$REASONING" | grep -q "3GPP_GATE_FAIL"; then
  echo "✅ EVIDENCE PASS: REJECT with 3GPP_GATE_FAIL (sem depender do Portal)"
  exit 0
else
  echo "❌ EVIDENCE FAIL: expected action=REJECT and reasoning containing 3GPP_GATE_FAIL; got action=$ACTION"
  exit 1
fi
