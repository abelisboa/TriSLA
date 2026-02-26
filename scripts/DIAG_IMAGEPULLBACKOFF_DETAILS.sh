#!/usr/bin/env bash
set -euo pipefail

NS="${NS:-trisla}"
OUT_DIR="${OUT_DIR:-./evidencias_imagepull_diag/$(date -u +%Y%m%dT%H%M%SZ)}"

mkdir -p "$OUT_DIR"

echo "=========================================================="
echo "DIAG ImagePullBackOff — Detalhes completos (auditável)"
echo "Namespace: $NS"
echo "Evidências: $OUT_DIR"
echo "=========================================================="

echo "[1/4] Listando pods em ImagePullBackOff"
kubectl -n "$NS" get pods | tee "$OUT_DIR/pods.txt"

echo
echo "[2/4] Coletando describe completo dos pods em ImagePullBackOff"
PODS="$(kubectl -n "$NS" get pods | awk '$3=="ImagePullBackOff"{print $1}')"
if [ -z "${PODS:-}" ]; then
  echo "Nenhum pod em ImagePullBackOff encontrado."
  exit 0
fi

for p in $PODS; do
  echo "---- POD: $p ----" | tee -a "$OUT_DIR/describe_summary.txt"
  kubectl -n "$NS" describe pod "$p" > "$OUT_DIR/describe_${p}.txt"
  # Extrai as linhas mais relevantes (erro real)
  grep -nE "Image:|Reason:|Failed|ErrImagePull|Back-off pulling image|unauthorized|forbidden|denied|manifest unknown|timeout|TLS|i/o timeout" \
    "$OUT_DIR/describe_${p}.txt" \
    | tee -a "$OUT_DIR/describe_summary.txt" || true
  echo | tee -a "$OUT_DIR/describe_summary.txt"
done

echo
echo "[3/4] Verificando ServiceAccounts e imagePullSecrets efetivos"
kubectl -n "$NS" get sa -o wide > "$OUT_DIR/serviceaccounts.txt" || true
kubectl -n "$NS" get sa default -o yaml > "$OUT_DIR/sa_default.yaml" || true

echo
echo "[4/4] Verificando secret ghcr-secret (existência e tipo, sem vazar conteúdo)"
kubectl -n "$NS" get secret ghcr-secret -o yaml > "$OUT_DIR/secret_ghcr_secret.yaml" || true
grep -nE "name:|type:|dockerconfigjson" "$OUT_DIR/secret_ghcr_secret.yaml" > "$OUT_DIR/secret_ghcr_secret_summary.txt" || true

echo "=========================================================="
echo "DIAG concluído."
echo "Resumo: $OUT_DIR/describe_summary.txt"
echo "=========================================================="
