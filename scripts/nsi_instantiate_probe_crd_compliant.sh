#!/bin/bash
set -euo pipefail

NS="${1:-trisla}"
BASE="/home/porvir5g/gtp5g/trisla"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${BASE}/evidencias_nsi_validation/nsi_probe_crd_${TS}"
mkdir -p "${OUT}"

PF_PID=""
cleanup() {
  if [[ -n "${PF_PID}" ]]; then
    kill "${PF_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo "===========================================" | tee "${OUT}/run.log"
echo "TriSLA NSI PROBE (CRD-COMPLIANT)" | tee -a "${OUT}/run.log"
echo "Namespace : ${NS}" | tee -a "${OUT}/run.log"
echo "Output    : ${OUT}" | tee -a "${OUT}/run.log"
echo "===========================================" | tee -a "${OUT}/run.log"

echo "1) Port-forward NASP Adapter..." | tee -a "${OUT}/run.log"
kubectl -n "${NS}" port-forward deploy/trisla-nasp-adapter 18085:8085 >"${OUT}/portforward.log" 2>&1 &
PF_PID="$!"
sleep 2

echo "2) Health..." | tee -a "${OUT}/run.log"
curl -sS "http://127.0.0.1:18085/health" | tee "${OUT}/health.json"
echo "" | tee -a "${OUT}/run.log"

# ID RFC1123 lowercase garantido (sem Z maiúsculo)
NSI_ID="probe-urllc-${TS,,}"   # ,,: lowercase
# Também evitar qualquer caracter estranho (extra hardening)
NSI_ID="$(echo "${NSI_ID}" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9.-]+/-/g' | sed -E 's/^-+//; s/-+$//')"

cat > "${OUT}/payload.json" <<EOF
{
  "nsiId": "${NSI_ID}",
  "serviceProfile": "URLLC",
  "tenantId": "default",
  "sla": { "latency": "10ms" }
}
EOF

echo "3) POST /api/v1/nsi/instantiate (CRD-compliant)..." | tee -a "${OUT}/run.log"
HTTP_CODE="$(curl -sS -o "${OUT}/instantiate_response.json" -w "%{http_code}" \
  -X POST "http://127.0.0.1:18085/api/v1/nsi/instantiate" \
  -H "Content-Type: application/json" \
  --data-binary @"${OUT}/payload.json")"

echo "HTTP=${HTTP_CODE}" | tee -a "${OUT}/run.log"
cat "${OUT}/instantiate_response.json" | tee -a "${OUT}/run.log"
echo "" | tee -a "${OUT}/run.log"

echo "4) Aguarda reconcile..." | tee -a "${OUT}/run.log"
sleep 6

echo "5) Verifica NSI CR..." | tee -a "${OUT}/run.log"
kubectl -n "${NS}" get networksliceinstance "${NSI_ID}" -o yaml > "${OUT}/nsi.yaml" 2>&1 || true
sed -n '1,180p' "${OUT}/nsi.yaml" | tee -a "${OUT}/run.log"
echo "" | tee -a "${OUT}/run.log"

echo "6) Verifica namespace isolado (ns-${NSI_ID})..." | tee -a "${OUT}/run.log"
kubectl get ns "ns-${NSI_ID}" -o yaml > "${OUT}/namespace.yaml" 2>&1 || true
sed -n '1,80p' "${OUT}/namespace.yaml" | tee -a "${OUT}/run.log"
echo "" | tee -a "${OUT}/run.log"

echo "7) ResourceQuota..." | tee -a "${OUT}/run.log"
kubectl -n "ns-${NSI_ID}" get resourcequota -o yaml > "${OUT}/resourcequota.yaml" 2>&1 || true
sed -n '1,160p' "${OUT}/resourcequota.yaml" | tee -a "${OUT}/run.log"
echo "" | tee -a "${OUT}/run.log"

echo "8) Logs recentes do NASP Adapter..." | tee -a "${OUT}/run.log"
kubectl -n "${NS}" logs deploy/trisla-nasp-adapter --since=10m > "${OUT}/nasp_adapter_logs_10m.txt" 2>&1 || true
tail -n 120 "${OUT}/nasp_adapter_logs_10m.txt" | tee -a "${OUT}/run.log"

echo "===========================================" | tee -a "${OUT}/run.log"
echo "COMPLETED" | tee -a "${OUT}/run.log"
echo "NSI_ID   : ${NSI_ID}" | tee -a "${OUT}/run.log"
echo "Evidence : ${OUT}" | tee -a "${OUT}/run.log"
echo "===========================================" | tee -a "${OUT}/run.log"

