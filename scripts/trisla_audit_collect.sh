#!/usr/bin/env bash
set -euo pipefail

#############################################
# TriSLA FULL AUDIT COLLECTOR (NASP SAFE)
# Local padrão:
#   /home/porvir5g/gtp5g/trisla/scripts
#
# Saída padrão:
#   ../evidencias_auditoria/
#############################################

# -------- CONFIG --------
BASE_DIR="/home/porvir5g/gtp5g/trisla"
OUTPUT_BASE="${BASE_DIR}/evidencias_auditoria"

NS="${1:-trisla}"
REL="${2:-trisla}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUTPUT_BASE}/${REL}_${NS}_${TS}"

mkdir -p "${OUT}"/{00_meta,01_k8s,02_describe,03_events,04_logs,05_helm,06_rbac,07_crd_cr,08_net_tests,09_images,10_diff,11_env}

echo "=================================================="
echo "TriSLA AUDIT START"
echo "Namespace : ${NS}"
echo "Release   : ${REL}"
echo "Output    : ${OUT}"
echo "=================================================="

# ---------- Helpers ----------
run() {
  echo "RUN: $*" >> "${OUT}/00_meta/run.log"
  bash -c "$*" >> "${OUT}/00_meta/run.log" 2>&1 || true
}

# ---------- META ----------
run "kubectl version --short"
run "helm version"
run "kubectl config current-context"
run "date -u"

# ---------- SNAPSHOT K8S ----------
run "kubectl get all -n ${NS} -o wide > ${OUT}/01_k8s/all_wide.txt"
run "kubectl get deploy,rs,po,svc,ep,ing,cm,sa,pvc -n ${NS} -o yaml > ${OUT}/01_k8s/objects.yaml"
run "kubectl get secret -n ${NS} -o name > ${OUT}/01_k8s/secrets_list.txt"

# ---------- DESCRIBE ----------
run "kubectl describe deploy -n ${NS} > ${OUT}/02_describe/deploy.txt"
run "kubectl describe po -n ${NS} > ${OUT}/02_describe/pods.txt"
run "kubectl describe svc -n ${NS} > ${OUT}/02_describe/services.txt"

# ---------- EVENTS ----------
run "kubectl get events -n ${NS} --sort-by=.lastTimestamp > ${OUT}/03_events/events.txt"

# ---------- LOGS ----------
PODS=$(kubectl get po -n ${NS} -o jsonpath='{.items[*].metadata.name}')

for p in $PODS; do
  kubectl logs -n ${NS} "$p" --since=30m > "${OUT}/04_logs/${p}.log" 2>/dev/null || true
  kubectl logs -n ${NS} "$p" --previous > "${OUT}/04_logs/${p}_previous.log" 2>/dev/null || true
done

# ---------- HELM ----------
run "helm list -n ${NS} > ${OUT}/05_helm/helm_list.txt"
run "helm status ${REL} -n ${NS} > ${OUT}/05_helm/status.txt"
run "helm history ${REL} -n ${NS} > ${OUT}/05_helm/history.txt"
run "helm get values ${REL} -n ${NS} -a > ${OUT}/05_helm/values.yaml"
run "helm get manifest ${REL} -n ${NS} > ${OUT}/05_helm/manifest.yaml"

# ---------- RBAC ----------
run "kubectl get role,rolebinding -n ${NS} -o yaml > ${OUT}/06_rbac/ns_rbac.yaml"
run "kubectl get clusterrole,clusterrolebinding -o yaml > ${OUT}/06_rbac/cluster_rbac.yaml"

# ---------- CRDs ----------
run "kubectl get crd | grep trisla > ${OUT}/07_crd_cr/crds.txt"
run "kubectl get networksliceinstances.trisla.io -n ${NS} -o yaml > ${OUT}/07_crd_cr/nsi.yaml"
run "kubectl get networkslicesubnetinstances.trisla.io -n ${NS} -o yaml > ${OUT}/07_crd_cr/nssi.yaml"

# ---------- IMAGES ----------
run "kubectl get pods -n ${NS} -o jsonpath='{range .items[*]}{.metadata.name}{\" => \"}{range .spec.containers[*]}{.image}{\"\\n\"}{end}{end}' > ${OUT}/09_images/pods_images.txt"

# ---------- CONNECTIVITY TEST ----------
cat > "${OUT}/08_net_tests/nsi_test.json" <<EOF
{
  "nsiId": "audit-check",
  "service_type": "URLLC",
  "sla": { "latencia_maxima_ms": 10 }
}
EOF

kubectl run curl-audit \
  -n ${NS} \
  --rm -i --restart=Never \
  --image=curlimages/curl:8.6.0 \
  -- sh -c "
    echo '=== HEALTH NASP ==='
    curl -s http://trisla-nasp-adapter:8085/health
    echo
    echo '=== INSTANTIATE TEST ==='
    curl -s -X POST http://trisla-nasp-adapter:8085/api/v1/nsi/instantiate \
      -H 'Content-Type: application/json' \
      --data-binary @- <<JSON
$(cat ${OUT}/08_net_tests/nsi_test.json)
JSON
  " > "${OUT}/08_net_tests/http_tests.txt" 2>&1 || true

# ---------- ENV FILTER ----------
CRITICAL=("trisla-portal-backend" "trisla-decision-engine" "trisla-nasp-adapter")

for d in "${CRITICAL[@]}"; do
  POD=$(kubectl get po -n ${NS} | grep ${d} | awk '{print $1}' | head -n1)
  if [ ! -z "$POD" ]; then
    kubectl exec -n ${NS} "$POD" -- printenv 2>/dev/null | \
      grep -E 'NASP_|TRISLA_|PROD|SIMUL|MODE|GATE' \
      > "${OUT}/11_env/${d}_env.txt" || true
  fi
done

# ---------- PACKAGE ----------
tar -czf "${OUT}.tar.gz" -C "${OUTPUT_BASE}" "$(basename ${OUT})"

echo
echo "=================================================="
echo "AUDIT COMPLETED"
echo "Folder : ${OUT}"
echo "Tarball: ${OUT}.tar.gz"
echo "=================================================="
