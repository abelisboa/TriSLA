#!/bin/bash
# =============================================================
# 🚀 TriSLA WU-003 — Integration & Observability Validation
# Autor: Abel José Rodrigues Lisboa | UNISINOS 2025
# =============================================================

NAMESPACE="trisla-nsp"
EVID_DIR="/home/porvir5g/gtp5g/trisla-nsp/docs/evidencias/$(date +%Y%m%d_%H%M)"
mkdir -p "$EVID_DIR"

echo "=============================================================="
echo "▶️ [1/6] Verificando pods e services..."
echo "=============================================================="
kubectl get pods -n $NAMESPACE -o wide | tee "$EVID_DIR/pods.txt"
kubectl get svc  -n $NAMESPACE -o wide | tee "$EVID_DIR/services.txt"

echo
echo "=============================================================="
echo "▶️ [2/6] Testando conexões internas Integration → Semantic / AI"
echo "=============================================================="
INTEGRATION_POD=$(kubectl get pod -n $NAMESPACE -l app=trisla-integration-layer -o jsonpath='{.items[0].metadata.name}')

kubectl -n $NAMESPACE exec -it $INTEGRATION_POD -- sh -c '
  apk add --no-cache curl >/dev/null 2>&1 || (apt-get update && apt-get install -y curl)
  echo ">> Testing Semantic..."
  curl -s -o /dev/null -w "Semantic: %{http_code}\n" http://trisla-semantic-svc:8080/health || echo "Semantic unreachable"
  echo ">> Testing AI..."
  curl -s -o /dev/null -w "AI: %{http_code}\n" http://trisla-ai-svc:8080/health || echo "AI unreachable"
' | tee "$EVID_DIR/service_connectivity.txt"

echo
echo "=============================================================="
echo "▶️ [3/6] Coletando logs dos módulos TriSLA"
echo "=============================================================="
for d in trisla-semantic-layer trisla-ai-layer trisla-integration-layer trisla-blockchain-layer trisla-monitoring-layer; do
  echo "===== Logs $d =====" | tee -a "$EVID_DIR/logs.txt"
  kubectl -n $NAMESPACE logs deploy/$d --tail=200 >> "$EVID_DIR/logs.txt" 2>&1
  echo -e "\n" >> "$EVID_DIR/logs.txt"
done

echo
echo "=============================================================="
echo "▶️ [4/6] Verificando targets do Prometheus (Monitoring Layer)"
echo "=============================================================="
MONITORING_POD=$(kubectl get pod -n $NAMESPACE -l app=trisla-monitoring-layer -o jsonpath='{.items[0].metadata.name}')
kubectl -n $NAMESPACE exec -it $MONITORING_POD -- wget -qO- http://localhost:9090/api/v1/targets > "$EVID_DIR/prometheus_targets.json"
grep -q '"health":"up"' "$EVID_DIR/prometheus_targets.json" && echo "✅ Targets UP" || echo "⚠️ Alguns targets estão DOWN"

echo
echo "=============================================================="
echo "▶️ [5/6] Salvando resumo final"
echo "=============================================================="
kubectl get pods -n $NAMESPACE | grep trisla | tee "$EVID_DIR/final_status.txt"
echo "Evidências salvas em: $EVID_DIR"

echo
echo "=============================================================="
echo "▶️ [6/6] Gerando resumo Markdown automático"
echo "=============================================================="
cat <<EOF > "$EVID_DIR/Resumo_WU-003.md"
# 🧩 WU-003 — Integração e Observabilidade TriSLA@NASP

## 📅 Data de execução
$(date)

## ✅ Pods em execução
\`\`\`
$(kubectl get pods -n $NAMESPACE)
\`\`\`

## 🌐 Conectividade Integration → Semantic/AI
\`\`\`
$(cat $EVID_DIR/service_connectivity.txt)
\`\`\`

## 📊 Logs coletados
Salvos em: $EVID_DIR/logs.txt

## 📈 Prometheus Targets
Arquivo: $EVID_DIR/prometheus_targets.json

## 📘 Autor
Abel José Rodrigues Lisboa — UNISINOS 2025
EOF

echo "✅ Script concluído com sucesso!"
echo "📁 Consulte evidências em: $EVID_DIR"
