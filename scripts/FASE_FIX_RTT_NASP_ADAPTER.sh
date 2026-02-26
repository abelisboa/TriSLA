#!/usr/bin/env bash
set -euo pipefail

BASE="/home/porvir5g/gtp5g/trisla"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_DIR="$BASE/evidencias_guardiao_deterministico"
LOG_FILE="$LOG_DIR/FASE_FIX_RTT_${TS}.log"

TAG="v3.9.27"
IMG="ghcr.io/abelisboa/trisla-nasp-adapter:${TAG}"

mkdir -p "$LOG_DIR"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "==========================================="
echo "FASE FIX — RTT Definitivo no NASP Adapter"
echo "==========================================="
echo "Base: $BASE"
echo "Tag:  $TAG"
echo "Imagem: $IMG"
echo "Log: $LOG_FILE"
echo

cd "$BASE/apps/nasp-adapter"

echo "PASSO 1 — Verificar se RTT já está integrado"
if grep -q 'out\["rtt_p95_ms"\]' src/metrics_collector.py; then
  echo "RTT já integrado. Abortando para evitar duplicação."
  exit 1
fi

echo "PASSO 2 — Aplicando patch controlado no metrics_collector.py"

python3 << 'PY'
import re
path = "src/metrics_collector.py"

with open(path, "r") as f:
    content = f.read()

pattern = r'(if v is not None:\n\s*out\["ue_count"\] = int\(v\)\n)'
replacement = r'\1\n        # RTT real via Blackbox\n        rtt = _collect_transport_rtt_prometheus()\n        if rtt is not None:\n            out["rtt_p95_ms"] = round(float(rtt), 3)\n'

if re.search(pattern, content):
    content = re.sub(pattern, replacement, content)
    with open(path, "w") as f:
        f.write(content)
    print("Patch aplicado com sucesso.")
else:
    print("ERRO: bloco esperado não encontrado.")
    exit(1)
PY

echo "PASSO 3 — Validar sintaxe Python"
python3 -m py_compile src/metrics_collector.py
echo "OK: syntax valid"

echo "PASSO 4 — Build imagem"
podman build -t "$IMG" .

echo "PASSO 5 — Push imagem"
podman push "$IMG"

echo "PASSO 6 — Deploy via Helm"
cd "$BASE"
helm upgrade trisla helm/trisla -n trisla \
  --set naspAdapter.image.tag="$TAG"

echo "PASSO 7 — Aguardar rollout"
kubectl rollout status -n trisla deploy/trisla-nasp-adapter --timeout=180s

echo "PASSO 8 — Confirmar imagem ativa"
kubectl get pod -n trisla -l app=trisla-nasp-adapter \
  -o jsonpath='{.items[0].spec.containers[0].image}{"\n"}'

echo "PASSO 9 — Testar endpoint multidomain"
kubectl run curl-md --rm -i --restart=Never -n trisla \
  --image=curlimages/curl --command -- \
  curl -s http://trisla-nasp-adapter:8085/api/v1/metrics/multidomain

echo
echo "==========================================="
echo "FIX RTT CONCLUÍDO — Validar JSON acima"
echo "==========================================="
