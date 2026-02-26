#!/usr/bin/env bash
set -euo pipefail

TRISLA_NS="trisla"
ROOT="/home/porvir5g/gtp5g/trisla"
PORTAL="http://trisla-portal-backend:8001"

# Extrair env reais do NASP Adapter
ENV_DUMP=$(kubectl get deploy -n "$TRISLA_NS" trisla-nasp-adapter \
  -o jsonpath='{range .spec.template.spec.containers[0].env[*]}{.name}={.value}{"\n"}{end}')

PROM_URL=$(echo "$ENV_DUMP" | awk -F= '/^PROMETHEUS_URL=/{print $2}')
CORE_NS=$(echo "$ENV_DUMP" | awk -F= '/^GATE_3GPP_CORE_NAMESPACE=/{print $2}')
UERANSIM_NS=$(echo "$ENV_DUMP" | awk -F= '/^GATE_3GPP_UERANSIM_NAMESPACE=/{print $2}')
GATE=$(echo "$ENV_DUMP" | awk -F= '/^GATE_3GPP_ENABLED=/{print $2}')

SERVICE_TYPE="${SERVICE_TYPE:-urllc}"
TENANT_ID="${TENANT_ID:-default}"

TS="$(date +%Y%m%d-%H%M%S)"
EVD="$ROOT/evidencias_e2e/${TS}-e2e-portal-to-nasp-full"
mkdir -p "$EVD"

echo "=============================================="
echo "TriSLA E2E FULL – Portal → NASP → Observability"
echo "Evidence Dir: $EVD"
echo "Service Type: $SERVICE_TYPE"
echo "=============================================="

# ----------------------------
# 1) PRECHECKS
# ----------------------------

echo "GATE_3GPP_ENABLED=$GATE" | tee "$EVD/gate_status.txt"

if [[ "$GATE" != "true" ]]; then
  echo "❌ Gate 3GPP não habilitado."
  exit 1
fi

if [[ -z "$CORE_NS" || -z "$UERANSIM_NS" ]]; then
  echo "❌ CORE_NS ou UERANSIM_NS vazio."
  exit 1
fi

# Snapshot BEFORE
kubectl get ns | grep '^ns-nsi-' | sort > "$EVD/ns_before.txt" || true
kubectl get pods -n "$CORE_NS" -o wide > "$EVD/core_before.txt"
kubectl get pods -n "$UERANSIM_NS" -o wide > "$EVD/ran_before.txt"

# ----------------------------
# 2) SUBMIT REAL
# ----------------------------

TEMPLATE_ID="template:URLLC"
if [[ "$SERVICE_TYPE" == "embb" ]]; then TEMPLATE_ID="template:eMBB"; fi
if [[ "$SERVICE_TYPE" == "mmtc" ]]; then TEMPLATE_ID="template:mMTC"; fi

SUBMIT_BODY=$(cat <<EOF
{
  "template_id": "${TEMPLATE_ID}",
  "tenant_id": "${TENANT_ID}",
  "form_values": {
    "type": "${SERVICE_TYPE^^}",
    "latencia_maxima_ms": 10,
    "disponibilidade_percent": 99.99,
    "confiabilidade_percent": 99.99,
    "numero_dispositivos": 10
  }
}
EOF
)

echo "$SUBMIT_BODY" > "$EVD/submit_request.json"

echo "🚀 Executando submit real..."

kubectl run portal-submit \
  -n "$TRISLA_NS" \
  --rm \
  --restart=Never \
  --image=curlimages/curl:8.6.0 \
  --command -- \
  sh -c "curl -sS -w '\nHTTP_STATUS:%{http_code}' \
    -X POST ${PORTAL}/api/v1/sla/submit \
    -H 'Content-Type: application/json' \
    -d '$SUBMIT_BODY'" \
  > "$EVD/submit_raw.txt"

HTTP_STATUS=$(grep 'HTTP_STATUS:' "$EVD/submit_raw.txt" | cut -d: -f2)
sed -e 's/HTTP_STATUS:.*//' "$EVD/submit_raw.txt" > "$EVD/submit_response.json"

echo "HTTP_STATUS=$HTTP_STATUS" | tee "$EVD/http_status.txt"

if [[ "$HTTP_STATUS" != "200" ]]; then
  echo "❌ HTTP != 200"
  exit 1
fi

# Validar JSON e Blockchain
python3 <<PY
import json, sys, pathlib
p = pathlib.Path("$EVD/submit_response.json")
data = json.loads(p.read_text())

if data.get("status") != "ok":
    print("FAIL status"); sys.exit(1)

if not (data.get("tx_hash") or data.get("blockchain_tx_hash")):
    print("FAIL sem tx_hash"); sys.exit(2)

if not data.get("block_number"):
    print("FAIL sem block_number"); sys.exit(3)

print("Submit validado:", data.get("decision"))
PY

echo "✅ Submit + Blockchain confirmados."

# ----------------------------
# 3) INSTANTIATION REAL
# ----------------------------

echo "⏳ Aguardando namespace ns-nsi-* novo..."

for i in {1..24}; do
  kubectl get ns | grep '^ns-nsi-' | sort > "$EVD/ns_after.txt" || true
  if ! diff -q "$EVD/ns_before.txt" "$EVD/ns_after.txt" >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

diff -u "$EVD/ns_before.txt" "$EVD/ns_after.txt" > "$EVD/ns_diff.txt" || true

NEW_NS=$(grep '^+' "$EVD/ns_diff.txt" | grep -v '+++' | awk '{print $2}' | head -n 1 || true)

if [[ -z "$NEW_NS" ]]; then
  echo "❌ Nenhum ns-nsi criado."
  exit 1
fi

echo "NSI criado: $NEW_NS" | tee "$EVD/new_namespace.txt"

kubectl get all -n "$NEW_NS" -o wide > "$EVD/nsi_resources.txt"

# ----------------------------
# 4) CORE METRICS (REAL)
# ----------------------------

UPF_POD=$(kubectl get pods -n "$CORE_NS" -o name | grep -i upf | head -n1 | sed 's|pod/||')

kubectl top pod -n "$CORE_NS" "$UPF_POD" > "$EVD/upf_top.txt" || true

# ----------------------------
# 5) RAN PROXY
# ----------------------------

UE_POD=$(kubectl get pods -n "$UERANSIM_NS" -o name | grep -i ue | head -n1 | sed 's|pod/||')

if [[ -n "$UE_POD" ]]; then
  kubectl logs -n "$UERANSIM_NS" "$UE_POD" --tail=2000 > "$EVD/ue_logs.txt"
fi

# ----------------------------
# 6) TRANSPORTE RTT
# ----------------------------

UPF_IP=$(kubectl get pod -n "$CORE_NS" "$UPF_POD" -o jsonpath='{.status.podIP}' 2>/dev/null || true)

if [[ -n "$UPF_IP" ]]; then
  kubectl run -n "$UERANSIM_NS" rtt-probe \
    --rm --restart=Never --image=busybox:1.36.1 \
    --command -- sh -c "ping -c 30 $UPF_IP" \
    > "$EVD/rtt_ping.txt" || true
fi

echo "=============================================="
echo "✅ E2E FULL CONCLUÍDO COM EVIDÊNCIAS REAIS"
echo "Evidence: $EVD"
echo "=============================================="
