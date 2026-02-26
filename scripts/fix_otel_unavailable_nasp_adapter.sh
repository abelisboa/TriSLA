#!/usr/bin/env bash
set -euo pipefail

NS="trisla"
SVC="trisla-otel-collector"
DEP="trisla-nasp-adapter"

echo "=================================================="
echo "TriSLA — FIX OTLP UNAVAILABLE (NASP Adapter -> OTel Collector)"
echo "Namespace : $NS"
echo "Service   : $SVC:4317"
echo "Target    : deploy/$DEP"
echo "=================================================="

echo "1) Verificando Service/Endpoints..."
kubectl -n "$NS" get svc "$SVC" -o wide
kubectl -n "$NS" get endpoints "$SVC" -o wide || true

echo "2) Verificando Pod do Collector..."
kubectl -n "$NS" get pods -l app="$SVC" -o wide || true

echo "3) Verificando conectividade a partir do NASP Adapter..."
POD=$(kubectl -n "$NS" get pod -l app="$DEP" -o jsonpath='{.items[0].metadata.name}')
echo "POD=$POD"

kubectl -n "$NS" exec -it "$POD" -- sh -lc '
  echo "---- ENV OTLP/OTEL ----"
  printenv | egrep "OTLP|OTEL" || true
  echo "---- DNS ----"
  (command -v nslookup >/dev/null && nslookup '"$SVC"') || true
  echo "---- TCP 4317 ----"
  (command -v nc >/dev/null && nc -zv '"$SVC"' 4317) || echo "WARN: nc not available or failed"
' || true

echo "4) Aplicando envs para OTLP gRPC insecure (compatível OTLP_* e OTEL_* )..."
kubectl -n "$NS" set env deployment/"$DEP" \
  OTLP_ENABLED=true \
  OTLP_ENDPOINT="http://$SVC:4317" \
  OTLP_INSECURE=true \
  OTLP_PROTOCOL=grpc \
  OTEL_EXPORTER_OTLP_INSECURE=true \
  OTEL_EXPORTER_OTLP_PROTOCOL=grpc \
  OTEL_EXPORTER_OTLP_ENDPOINT="$SVC:4317"

echo "5) Rollout..."
kubectl -n "$NS" rollout status deployment/"$DEP"

echo "6) Validação rápida de erro UNAVAILABLE (últimas linhas)..."
kubectl -n "$NS" logs deployment/"$DEP" --tail=120 | grep -i "UNAVAILABLE" || echo "OK: sem UNAVAILABLE nas últimas 120 linhas."

echo "=================================================="
echo "✅ Concluído."
echo "Próximo passo: gerar tráfego (instantiate) para confirmar spans chegando no Collector."
echo "=================================================="
