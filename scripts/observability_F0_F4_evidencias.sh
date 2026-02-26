#!/usr/bin/env bash
set -euo pipefail

############################################
# TriSLA Observability — FASE 0–4
# Versão determinística NASP (kube-prometheus-stack)
############################################

TRISLA_NS="trisla"
MON_NS="monitoring"
CORE_NS="ns-1274485"
OPEN5GS_NS="open5gs"

# Prometheus oficial do cluster NASP
PROM_SVC="prometheus-kube-prometheus-prometheus"
PROM_PORT="9090"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
ROOT="/home/porvir5g/gtp5g/trisla"
EVID="$ROOT/evidencias_observability_F0_F4_$TS"

mkdir -p "$EVID"

log(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }

PF_PID=""
cleanup() {
  if [[ -n "${PF_PID}" ]]; then
    kill "${PF_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo "==============================================="
echo "TriSLA Observability — FASE 0–4 (NASP)"
echo "TRISLA_NS=$TRISLA_NS"
echo "PROMETHEUS=$PROM_SVC:$PROM_PORT"
echo "Evidence: $(basename "$EVID")"
echo "==============================================="

############################################
# FASE 0 — Snapshot + Gate
############################################

log "[FASE 0] Snapshot + Gate"

kubectl version --short > "$EVID/FASE0_k8s_version.txt" || true
kubectl get nodes -o wide > "$EVID/FASE0_nodes.txt" || true
kubectl -n "$TRISLA_NS" get pods -o wide > "$EVID/FASE0_trisla_pods.txt" || true

if kubectl -n "$TRISLA_NS" get pods | egrep -qi 'CrashLoopBackOff|ImagePullBackOff|ErrImagePull'; then
  kubectl -n "$TRISLA_NS" get pods -o wide | tee "$EVID/FASE0_gate_errors.txt"
  echo "FATAL: Namespace com erro crítico."
  exit 1
fi

log "[FASE 0] OK"

############################################
# FASE 1 — Framework Matrix
############################################

log "[FASE 1] Detectando frameworks"

python3 - <<'PY' "$ROOT/apps" "$EVID/FASE1_framework_matrix.tsv"
import os,sys,re
apps=sys.argv[1]
out=sys.argv[2]
pat_fastapi=re.compile(r'from\s+fastapi|FastAPI\s*\(')
pat_flask=re.compile(r'from\s+flask')
rows=[]
for svc in sorted(os.listdir(apps)):
    sp=os.path.join(apps,svc)
    if not os.path.isdir(sp): continue
    fw="unknown"
    for root,_,files in os.walk(sp):
        for fn in files:
            if fn.endswith(".py"):
                data=open(os.path.join(root,fn),"r",encoding="utf-8",errors="ignore").read()
                if pat_fastapi.search(data):
                    fw="fastapi"; break
                if pat_flask.search(data):
                    fw="flask"; break
        if fw!="unknown": break
    rows.append((svc,fw))
with open(out,"w") as f:
    f.write("service\tframework\n")
    for r in rows:
        f.write(f"{r[0]}\t{r[1]}\n")
PY

############################################
# FASE 2 — Kubernetes Metrics
############################################

log "[FASE 2] Kubernetes Metrics"

kubectl top pods -n "$TRISLA_NS" > "$EVID/FASE2_trisla_top.txt" 2>&1 || true
kubectl top nodes > "$EVID/FASE2_nodes_top.txt" 2>&1 || true

############################################
# FASE 3 — Prometheus Metrics (determinístico)
############################################

log "[FASE 3] Prometheus Metrics"

kubectl -n "$MON_NS" port-forward "svc/$PROM_SVC" 19090:$PROM_PORT > "$EVID/FASE3_portforward.log" 2>&1 &
PF_PID=$!
sleep 3

curl -fsS "http://localhost:19090/api/v1/label/__name__/values" \
  > "$EVID/FASE3_metric_names_raw.json" \
  2> "$EVID/FASE3_curl_error.txt" || true

kill "$PF_PID" >/dev/null 2>&1 || true
PF_PID=""

python3 - <<'PY' "$EVID/FASE3_metric_names_raw.json" "$EVID/FASE3_metric_names.json"
import sys,json
raw=open(sys.argv[1],"r",encoding="utf-8",errors="ignore").read().strip()
if raw.startswith("UTC:"):
    raw="\n".join(raw.splitlines()[1:])
try:
    data=json.loads(raw)
except Exception as e:
    data={"status":"error","error":str(e),"data":[]}
open(sys.argv[2],"w").write(json.dumps(data,indent=2))
PY

############################################
# FASE 4 — Core 5G / Open5GS
############################################

log "[FASE 4] Core 5G"

kubectl -n "$CORE_NS" get pods -o wide > "$EVID/FASE4_core_pods.txt" 2>&1 || true
kubectl -n "$CORE_NS" top pods > "$EVID/FASE4_core_top.txt" 2>&1 || true

kubectl -n "$OPEN5GS_NS" get pods -o wide > "$EVID/FASE4_open5gs_pods.txt" 2>&1 || true
kubectl -n "$OPEN5GS_NS" top pods > "$EVID/FASE4_open5gs_top.txt" 2>&1 || true

############################################
# Final
############################################

log "Evidências geradas em $(basename "$EVID")"
echo "$(basename "$EVID")"
