#!/usr/bin/env bash
set -euo pipefail

TRISLA_NS="trisla"
ROOT="/home/porvir5g/gtp5g/trisla"

SERVICE_TYPE="${SERVICE_TYPE:-urllc}"
TENANT_ID="${TENANT_ID:-default}"

TS="$(date +%Y%m%d-%H%M%S)"
EVD="$ROOT/evidencias_e2e/${TS}-e2e-portal-to-nasp-full"
mkdir -p "$EVD"

echo "=============================================="
echo "TriSLA E2E FULL – Portal → NASP Instantiation"
echo "Evidence Dir: $EVD"
echo "Service Type: $SERVICE_TYPE"
echo "=============================================="

# --------------------------------------------------
# 1️⃣ Validar Gate 3GPP
# --------------------------------------------------

GATE="$(kubectl get deploy -n trisla trisla-nasp-adapter \
-o jsonpath='{range .spec.template.spec.containers[0].env[*]}{.name}={.value}{"\n"}{end}' \
| awk -F= '/^GATE_3GPP_ENABLED=/{print $2}')"

echo "GATE_3GPP_ENABLED=$GATE" | tee "$EVD/gate_status.txt"

if [[ "$GATE" != "true" ]]; then
  echo "❌ Gate 3GPP não está habilitado"
  exit 1
fi

# --------------------------------------------------
# 2️⃣ Snapshot BEFORE namespaces
# --------------------------------------------------

kubectl get ns | grep '^ns-nsi-' | sort > "$EVD/ns_before.txt" || true

# --------------------------------------------------
# 3️⃣ Port-forward do Portal
# --------------------------------------------------

echo "🔌 Iniciando port-forward..."

kubectl port-forward -n trisla svc/trisla-portal-backend 8001:8001 \
> "$EVD/portforward.log" 2>&1 &

PF_PID=$!
sleep 3

# --------------------------------------------------
# 4️⃣ Montar payload REAL
# --------------------------------------------------

case "$SERVICE_TYPE" in
  urllc)
    FORM_JSON='{"type":"URLLC","latencia_maxima_ms":10,"disponibilidade_percent":99.99,"confiabilidade_percent":99.99,"numero_dispositivos":10}'
    TEMPLATE_ID="template:URLLC"
    ;;
  embb)
    FORM_JSON='{"type":"eMBB","latencia_maxima_ms":50,"disponibilidade_percent":99.9,"confiabilidade_percent":99.9,"throughput_min_dl_mbps":100,"throughput_min_ul_mbps":50}'
    TEMPLATE_ID="template:eMBB"
    ;;
  mmtc)
    FORM_JSON='{"type":"mMTC","latencia_maxima_ms":100,"disponibilidade_percent":95,"confiabilidade_percent":95,"numero_dispositivos":1000}'
    TEMPLATE_ID="template:mMTC"
    ;;
  *)
    echo "❌ SERVICE_TYPE inválido"
    kill $PF_PID
    exit 1
    ;;
esac

cat > "$EVD/submit_request.json" <<EOF
{
  "template_id": "$TEMPLATE_ID",
  "tenant_id": "$TENANT_ID",
  "form_values": $FORM_JSON
}
EOF

# --------------------------------------------------
# 5️⃣ Submit REAL
# --------------------------------------------------

echo "🚀 Executando submit REAL..."

curl -sS -w "\nHTTP_STATUS:%{http_code}\n" \
  -X POST http://localhost:8001/api/v1/sla/submit \
  -H "Content-Type: application/json" \
  --data-binary @"$EVD/submit_request.json" \
  > "$EVD/submit_raw.txt"

HTTP_STATUS=$(grep 'HTTP_STATUS:' "$EVD/submit_raw.txt" | awk -F: '{print $2}')
echo "$HTTP_STATUS" > "$EVD/http_status.txt"

sed '/HTTP_STATUS:/d' "$EVD/submit_raw.txt" > "$EVD/submit_response.json"

kill $PF_PID || true

if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "❌ HTTP diferente de 200"
  exit 1
fi

# --------------------------------------------------
# 6️⃣ Validar resposta
# --------------------------------------------------

python3 <<PY
import json, pathlib, sys
data=json.loads(pathlib.Path("$EVD/submit_response.json").read_text())
summary={
  "status":data.get("status"),
  "decision":data.get("decision"),
  "tx_hash":data.get("tx_hash"),
  "block_number":data.get("block_number"),
  "bc_status":data.get("bc_status"),
  "sla_id":data.get("sla_id"),
  "nest_id":data.get("nest_id")
}
pathlib.Path("$EVD/submit_summary.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

if summary["status"]!="ok":
    sys.exit("FAIL status")
if summary["bc_status"]!="CONFIRMED":
    sys.exit("FAIL blockchain")
PY

# --------------------------------------------------
# 7️⃣ Aguardar instantiation real
# --------------------------------------------------

echo "⏳ Aguardando criação de namespace..."

for i in {1..24}; do
  kubectl get ns | grep '^ns-nsi-' | sort > "$EVD/ns_after.txt" || true
  if ! diff -q "$EVD/ns_before.txt" "$EVD/ns_after.txt" >/dev/null 2>&1; then
    echo "✅ Novo namespace detectado"
    break
  fi
  sleep 5
done

diff -u "$EVD/ns_before.txt" "$EVD/ns_after.txt" > "$EVD/ns_diff.txt" || true

NEW_NS=$(grep '^+' "$EVD/ns_diff.txt" | grep -v '+++' | awk '{print $2}' | head -n1 || true)
echo "NEW_NAMESPACE=$NEW_NS" | tee "$EVD/new_namespace.txt"

if [[ -z "$NEW_NS" ]]; then
  echo "❌ Nenhum NSI criado → Instantiation NÃO ocorreu"
  exit 1
fi

echo "=============================================="
echo "✅ E2E COMPLETO FINALIZADO"
echo "Namespace criado: $NEW_NS"
echo "Evidence: $EVD"
echo "=============================================="
