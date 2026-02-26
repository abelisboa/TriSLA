#!/bin/bash
set -euo pipefail

# FASE 0 — CHECKPOINT + WORKDIR
cd /home/porvir5g/gtp5g/trisla

NS=trisla
TS=$(date +%Y%m%d_%H%M%S)
WORKDIR=/home/porvir5g/gtp5g/trisla/run_s3_13c_kafka_${TS}
mkdir -p "$WORKDIR"
echo "WORKDIR=$WORKDIR"

kubectl get pods -n $NS -o wide | tee "$WORKDIR/pods.txt"
kubectl get svc -n $NS | tee "$WORKDIR/svcs.txt"
kubectl get deploy -n $NS | tee "$WORKDIR/deploys.txt"

# FASE 1 — IDENTIFICAR "ONDE" O EVENTO DEVERIA APARECER
KAFKA_POD=$(kubectl get pods -n $NS | awk '/^kafka/{print $1; exit}')
echo "KAFKA_POD=$KAFKA_POD" | tee "$WORKDIR/kafka_pod.txt"
[ -n "$KAFKA_POD" ] || (echo "ABORT: Kafka pod não encontrado" && exit 1)

kubectl exec -n $NS "$KAFKA_POD" -- bash -lc \
  "/opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list" \
  | tee "$WORKDIR/kafka_topics.txt"

grep -E "trisla-decision-events|trisla-i04-decisions|trisla-i05-actions|trisla-i05-sla-agents|trisla-ml-predictions|trisla-ml-xai" \
  "$WORKDIR/kafka_topics.txt" | tee "$WORKDIR/kafka_topics_relevant.txt" || true

# FASE 2 — VALIDAR SE O DECISION ENGINE ESTÁ COM KAFKA ATIVO
DE_POD=$(kubectl get pods -n $NS -l app=trisla-decision-engine -o jsonpath='{.items[0].metadata.name}')
echo "DE_POD=$DE_POD" | tee "$WORKDIR/de_pod.txt"

kubectl exec -n $NS "$DE_POD" -- printenv | egrep "KAFKA|BROKER|TOPIC" | tee "$WORKDIR/decision_engine_env_kafka.txt" || true

kubectl logs -n $NS "$DE_POD" --since=30m | tee "$WORKDIR/decision_engine_logs_30m.txt" >/dev/null || true

grep -E "Decisão publicada no Kafka|published.*Kafka|send_to_.*|ProducerId|kafka" \
  "$WORKDIR/decision_engine_logs_30m.txt" | tail -n 200 | tee "$WORKDIR/decision_engine_kafka_evidence.txt" || true

# FASE 3 — SUBMIT CONTROLADO + CORRELACIONAR ID
PORTAL_SVC=trisla-portal-backend
NODEPORT=$(kubectl get svc -n $NS $PORTAL_SVC -o jsonpath='{.spec.ports[0].nodePort}')
NODEIP=$(hostname -I | awk '{print $1}')
BASEURL="http://${NODEIP}:${NODEPORT}"
echo "$BASEURL" | tee "$WORKDIR/portal_baseurl.txt"

curl -fsS "$BASEURL/openapi.json" -o "$WORKDIR/portal_openapi.json"
jq -e '.paths["/api/v1/sla/submit"]' "$WORKDIR/portal_openapi.json" >/dev/null

cat > "$WORKDIR/sla_submit.json" <<'JSON'
{
  "template_id": "template:eMBB",
  "form_values": {
    "service_type": "eMBB",
    "throughput": "50",
    "latency": "50"
  }
}
JSON

curl -fsS -X POST "$BASEURL/api/v1/sla/submit" \
  -H "Content-Type: application/json" \
  -d @"$WORKDIR/sla_submit.json" \
  | tee "$WORKDIR/sla_submit_response.json" >/dev/null

python3 - <<PY | tee "$WORKDIR/intent_id.txt"
import json
d=json.load(open("$WORKDIR/sla_submit_response.json"))
for k in ["intent_id","sla_id","id","nest_id"]:
    if k in d:
        print(d[k]); raise SystemExit(0)
print("UNKNOWN")
PY

INTENT=$(cat "$WORKDIR/intent_id.txt" | tr -d '\n')
echo "INTENT=$INTENT" | tee "$WORKDIR/intent_id_kv.txt"

# FASE 4 — CONSUMIR EVENTOS
consume_topic () {
  local topic="$1"
  echo "=== CONSUME $topic ===" | tee -a "$WORKDIR/kafka_consume_all.txt"
  kubectl exec -n $NS "$KAFKA_POD" -- bash -lc \
    "/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic $topic --from-beginning --timeout-ms 30000 --max-messages 200" \
    2>/dev/null | tee "$WORKDIR/consume_${topic}.txt" >/dev/null || true
  echo "" | tee -a "$WORKDIR/kafka_consume_all.txt"
}

consume_topic "trisla-decision-events"
consume_topic "trisla-i04-decisions"
consume_topic "trisla-i05-actions"
consume_topic "trisla-i05-sla-agents"
consume_topic "trisla-ml-predictions"
consume_topic "trisla-ml-xai"

for f in "$WORKDIR"/consume_*.txt; do
  if [ -f "$f" ]; then
    echo "---- $f ----" | tee -a "$WORKDIR/grep_intent_hits.txt"
    grep -n "$INTENT" "$f" | head -n 20 | tee -a "$WORKDIR/grep_intent_hits.txt" || true
  fi
done

# FASE 5 — DIAGNÓSTICO RÁPIDO
kubectl logs -n $NS "$KAFKA_POD" --since=30m | tail -n 400 | tee "$WORKDIR/kafka_logs_tail.txt"

kubectl logs -n $NS "$DE_POD" --since=10m | tee "$WORKDIR/decision_engine_last10m.txt" >/dev/null || true
grep -E "decision_id|intent_id|Kafka|publish|Producer|send_" "$WORKDIR/decision_engine_last10m.txt" \
  | tail -n 200 | tee "$WORKDIR/decision_engine_last10m_signals.txt" || true

PB_POD=$(kubectl get pods -n $NS -l app=trisla-portal-backend -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n $NS "$PB_POD" --since=10m | tee "$WORKDIR/portal_backend_last10m.txt" >/dev/null || true
grep -E "decision|evaluate|intent_id|sla_id|submit|kafka" "$WORKDIR/portal_backend_last10m.txt" \
  | tail -n 200 | tee "$WORKDIR/portal_backend_last10m_signals.txt" || true

# FASE 6 — CORREÇÃO (se KAFKA_ENABLED=false)
if grep -q "KAFKA_ENABLED=false" "$WORKDIR/decision_engine_env_kafka.txt"; then
  echo "Kafka está desabilitado. Habilitando..."
  helm get values trisla -n $NS -a | tee "$WORKDIR/helm_values_before.yaml"
  
  helm upgrade --install trisla helm/trisla -n $NS --reuse-values \
    --set decisionEngine.env.KAFKA_ENABLED=true \
    --set decisionEngine.env.KAFKA_BROKERS=kafka:9092 \
    | tee "$WORKDIR/helm_upgrade_kafka_enable.log"
  
  kubectl rollout status -n $NS deploy/trisla-decision-engine --timeout=300s | tee "$WORKDIR/rollout_de_after_kafka_enable.txt"
  
  echo "Aguardando 30s para Kafka inicializar..."
  sleep 30
  
  # Repetir FASE 3 e 4 após correção
  echo "Repetindo submit após habilitar Kafka..."
  curl -fsS -X POST "$BASEURL/api/v1/sla/submit" \
    -H "Content-Type: application/json" \
    -d @"$WORKDIR/sla_submit.json" \
    | tee "$WORKDIR/sla_submit_response_after_kafka.json" >/dev/null
  
  python3 - <<PY | tee "$WORKDIR/intent_id_after_kafka.txt"
import json
d=json.load(open("$WORKDIR/sla_submit_response_after_kafka.json"))
for k in ["intent_id","sla_id","id","nest_id"]:
    if k in d:
        print(d[k]); raise SystemExit(0)
print("UNKNOWN")
PY
  
  INTENT_AFTER=$(cat "$WORKDIR/intent_id_after_kafka.txt" | tr -d '\n')
  
  sleep 10
  consume_topic "trisla-decision-events"
  consume_topic "trisla-i04-decisions"
  
  for f in "$WORKDIR"/consume_trisla-decision-events.txt "$WORKDIR"/consume_trisla-i04-decisions.txt; do
    if [ -f "$f" ]; then
      echo "---- $f (after kafka enable) ----" | tee -a "$WORKDIR/grep_intent_hits_after_kafka.txt"
      grep -n "$INTENT_AFTER" "$f" | head -n 20 | tee -a "$WORKDIR/grep_intent_hits_after_kafka.txt" || true
    fi
  done
fi

# FASE 7 — INTEGRIDADE FINAL
find "$WORKDIR" -type f -size 0 -print | tee "$WORKDIR/empty_files.txt" || true

sha256sum $(find "$WORKDIR" -type f | sort) > "$WORKDIR/CHECKSUMS.sha256"

echo "PASS: Evidence pack Kafka em $WORKDIR"
echo "Arquivos principais:"
ls -lah "$WORKDIR" | tee "$WORKDIR/ls_workdir.txt"
