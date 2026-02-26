#!/bin/bash
# PROMPT S34.1 — Recuperação Obrigatória do ML-NSMF
# Validação dos gates (FASE 1 + FASE 5) no node006.
# Executar: ssh node006 'cd /home/porvir5g/gtp5g/trisla && ./scripts/run_s34_1_validation.sh'

set -euo pipefail
NS="${NAMESPACE:-trisla}"
API_URL="${API_URL:-http://192.168.10.16:32002/api/v1/sla/submit}"
REPORT_DIR="/home/porvir5g/gtp5g/trisla/evidencias_s34_1_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$REPORT_DIR"

log() { echo "[$(date -Iseconds)] $*" | tee -a "$REPORT_DIR/run.log"; }
ok() { log "✅ $*"; }
fail() { log "❌ $*"; }
warn() { log "⚠️ $*"; }

echo "=========================================="
echo "PROMPT S34.1 — Recuperação Obrigatória do ML-NSMF"
echo "Validação gates (node006)"
echo "=========================================="
log "Report: $REPORT_DIR"

# --- Confirmação ambiente ---
log "Hostname: $(hostname)"
log "PWD: $(pwd)"
[[ "$(pwd)" == *"/trisla"* ]] || { fail "Executar em /home/porvir5g/gtp5g/trisla"; exit 1; }

# --- Pods ---
log "Pods críticos:"
kubectl get pods -n "$NS" | grep -E "decision-engine|ml-nsmf|portal-backend|kafka" | tee -a "$REPORT_DIR/run.log" || true
kubectl get deploy -n "$NS" trisla-ml-nsmf trisla-decision-engine -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.template.spec.containers[0].image}{"\n"}{end}' | tee -a "$REPORT_DIR/run.log"

# --- FASE 1 — Gate Modelo/Scaler ---
log ""
log "--- FASE 1 — Gate Modelo Obrigatório ---"
ML_LOGS=$(kubectl logs -n "$NS" deploy/trisla-ml-nsmf --tail=5000 2>&1)
echo "$ML_LOGS" > "$REPORT_DIR/ml_nsmf_logs.txt"

GATE1_OK=0
echo "$ML_LOGS" | grep -q "\[ML\] Loading trained model" && { ok "Log: [ML] Loading trained model"; GATE1_OK=$((GATE1_OK+1)); } || fail "Ausente: [ML] Loading trained model"
echo "$ML_LOGS" | grep -q "\[ML\] Model loaded successfully" && { ok "Log: [ML] Model loaded successfully"; GATE1_OK=$((GATE1_OK+1)); } || fail "Ausente: [ML] Model loaded successfully"
echo "$ML_LOGS" | grep -q "\[ML\] Scaler loaded successfully" && { ok "Log: [ML] Scaler loaded successfully"; GATE1_OK=$((GATE1_OK+1)); } || fail "Ausente: [ML] Scaler loaded successfully"

if echo "$ML_LOGS" | grep -q "Scaler não disponível\|normalização básica\|numpy._core"; then
  fail "Fallback scaler detectado (proibido pelo S34.1)"
  GATE1_OK=0
fi

if [ "$GATE1_OK" -lt 3 ]; then
  fail "FASE 1 GATE FALHOU: modelo/scaler não conformes com S34.1"
else
  ok "FASE 1 GATE APROVADO"
fi

# --- FASE 5 — Teste controlado (3 SLAs) ---
log ""
log "--- FASE 5 — Teste controlado (3 SLAs distintos) ---"
SUBMIT_OK=0
URLLC_FILE="$REPORT_DIR/sla_urllc.json"
EMBB_FILE="$REPORT_DIR/sla_embb.json"
MMTC_FILE="$REPORT_DIR/sla_mmtc.json"

submit_sla() {
  local f=$2
  local payload=$3
  curl -s -X POST "$API_URL" -H "Content-Type: application/json" -d "$payload" > "$f" 2>&1 || true
}

submit_sla URLLC "$URLLC_FILE" '{"template_id":"template:URLLC","form_values":{"service_type":"URLLC","latency_ms":5,"reliability":0.999},"tenant_id":"default"}'
submit_sla eMBB  "$EMBB_FILE"  '{"template_id":"template:eMBB","form_values":{"service_type":"eMBB","throughput_dl_mbps":100,"throughput_ul_mbps":50},"tenant_id":"default"}'
submit_sla mMTC  "$MMTC_FILE"  '{"template_id":"template:mMTC","form_values":{"service_type":"mMTC","device_density":1000},"tenant_id":"default"}'

for f in "$URLLC_FILE" "$EMBB_FILE" "$MMTC_FILE"; do
  [ -s "$f" ] && jq -e . "$f" >/dev/null 2>&1 && { ok "SLA $(basename "$f" .json): submetido"; SUBMIT_OK=$((SUBMIT_OK+1)); } || fail "SLA $(basename "$f"): falha ou vazio"
done

# --- risk_score distinto, XAI preenchido ---
risk_a=$(jq -r '.risk_score // .sla_compliance // "N/A"' "$URLLC_FILE" 2>/dev/null)
risk_b=$(jq -r '.risk_score // .sla_compliance // "N/A"' "$EMBB_FILE" 2>/dev/null)
risk_c=$(jq -r '.risk_score // .sla_compliance // "N/A"' "$MMTC_FILE" 2>/dev/null)
log "risk_score / sla_compliance: URLLC=$risk_a eMBB=$risk_b mMTC=$risk_c"

XAI_URLLC=$(jq -r '.xai // .explanation // {}' "$URLLC_FILE" 2>/dev/null)
if [ "$XAI_URLLC" = "{}" ] || [ -z "$XAI_URLLC" ]; then
  fail "XAI vazio ou ausente (proibido S34.1)"
else
  ok "XAI presente em resposta"
fi

# --- Gate final ---
log ""
log "--- Gate final S34.1 ---"
log "  Modelo carregado:      $([ $GATE1_OK -ge 3 ] && echo '✔' || echo '✗')"
log "  Métricas reais:        (verificar logs ML-NSMF)"
log "  Inferência variável:   risk_score acima"
log "  XAI completo:          $([ "$XAI_URLLC" != '{}' ] && echo '✔' || echo '✗')"
log "  Kafka/SLA-Agent:       (verificar módulos)"

log ""
log "Report salvo em: $REPORT_DIR"
echo "=========================================="
