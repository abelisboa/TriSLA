#!/bin/bash
set -uo pipefail
NS=trisla
TS=$(date +%Y%m%d_%H%M%S)
WORKDIR=/home/porvir5g/gtp5g/trisla/evidencias_fixrun_${TS}
mkdir -p "$WORKDIR"

# FASE 1 — PROMETHEUS
# Check if port 9090 is already accessible
if ! curl -s http://localhost:9090/api/v1/targets > /dev/null 2>&1; then
  echo "Creating port-forward for Prometheus..."
  kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 \
    > "$WORKDIR/01_pf_prometheus.log" 2>&1 &
  sleep 5
else
  echo "Port 9090 already accessible, reusing existing port-forward"
  echo "Port 9090 already in use" > "$WORKDIR/01_pf_prometheus.log"
fi

curl -s http://localhost:9090/api/v1/targets > "$WORKDIR/01_targets.json"

python3 - <<PY > "$WORKDIR/01_targets_down.txt"
import json
d=json.load(open("$WORKDIR/01_targets.json"))
downs=[]
for a in d.get("data",{}).get("activeTargets",[]):
    if a.get("health")!="up":
        downs.append((a.get("labels",{}).get("job","?"), a.get("scrapeUrl","?"), a.get("lastError","")))
for job,url,err in downs:
    print(job, url, err)
PY

curl -s "http://localhost:9090/api/v1/query?query=avg(rate(node_cpu_seconds_total{mode=\"idle\"}[1m]))" > "$WORKDIR/01_q_cpu.json"
curl -s "http://localhost:9090/api/v1/query?query=node_memory_MemAvailable_bytes" > "$WORKDIR/01_q_mem.json"
curl -s "http://localhost:9090/api/v1/query?query=node_filesystem_avail_bytes" > "$WORKDIR/01_q_disk.json"
curl -s "http://localhost:9090/api/v1/query?query=rate(container_network_transmit_bytes_total[1m])" > "$WORKDIR/01_q_net.json"

set +e
python3 - <<PY | tee "$WORKDIR/01_prom_gate.txt"import jsonimport sysdef ok(p):    try:        with open(p, "r") as f:            content = f.read().strip()            if not content:                return False            d = json.loads(content)            return len(d.get("data", {}).get("result", [])) > 0    except:        return Falsefiles = ["01_q_cpu.json", "01_q_mem.json", "01_q_disk.json", "01_q_net.json"]oks = sum(ok("$WORKDIR/" + f) for f in files)print("prom_queries_ok", oks, "/4")PY

# FASE 2
DE_POD=$(kubectl get pods -n $NS -l app=trisla-decision-engine -o jsonpath={.items[0].metadata.name})
SEM_POD=$(kubectl get pods -n $NS -l app=trisla-sem-csmf -o jsonpath={.items[0].metadata.name})

kubectl exec -n $NS "$DE_POD" -- printenv | egrep "LOG|KAFKA|PROM|TOPIC" > "$WORKDIR/02_de_env.txt" || true
kubectl exec -n $NS "$SEM_POD" -- printenv | egrep "LOG|LEVEL|SEM|GST|NEST" > "$WORKDIR/02_sem_env.txt" || true

# FASE 3 — FIX XAI (precisa localizar arquivos primeiro)
grep -Rni "xai_data" . | tee "$WORKDIR/03_xai_grep.txt"

# FASE 4 — SUBMIT
PORTAL_SVC=trisla-portal-backend
NODEPORT=$(kubectl get svc -n $NS $PORTAL_SVC -o jsonpath={.spec.ports[0].nodePort})
NODEIP=$(hostname -I | awk '{print $1}')
BASEURL="http://${NODEIP}:${NODEPORT}"

cat > "$WORKDIR/04_submit.json" <<'JSON'
{
  "template_id": "template:eMBB",
  "form_values": {
    "service_type": "eMBB",
    "throughput": "1",
    "latency": "300"
  }
}
JSON

for i in {1..5}; do
  curl -s -X POST "$BASEURL/api/v1/sla/submit" -H "Content-Type: application/json" -d @"$WORKDIR/04_submit.json" \
    > "$WORKDIR/04_resp_$i.json"
  dec=$(jq -r '.decision' "$WORKDIR/04_resp_$i.json" 2>/dev/null || echo "ERROR")
  iid=$(jq -r '.intent_id' "$WORKDIR/04_resp_$i.json" 2>/dev/null || echo "")
  echo "$i decision=$dec intent_id=$iid" | tee -a "$WORKDIR/04_trials.txt"
  if [ "$dec" = "ACCEPT" ]; then
    echo "$iid" > "$WORKDIR/04_intent_accept.txt"
    break
  fi
  sleep 2
done

# FASE 5 — KAFKA (only if ACCEPT was obtained)
if [ -f "$WORKDIR/04_intent_accept.txt" ]; then
  INTENT=$(cat "$WORKDIR/04_intent_accept.txt")
  kubectl run -n $NS kafkatools --rm -i --restart=Never --image=bitnami/kafka:3.6.0 -- \
    bash -lc "kafka-topics.sh --bootstrap-server kafka:9092 --list" > "$WORKDIR/05_topics.txt"

  grep -E "decision|trisla|i04|i05|sla" "$WORKDIR/05_topics.txt" | sort -u > "$WORKDIR/05_topics_candidates.txt" || true

  > "$WORKDIR/05_kafka_hits.txt"
  while read -r topic; do
    [ -n "$topic" ] || continue
    kubectl run -n $NS kafkaconsume --rm -i --restart=Never --image=bitnami/kafka:3.6.0 -- \
      bash -lc "kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic $topic --from-beginning --timeout-ms 90000 --max-messages 1000" \
      > "$WORKDIR/05_consume_${topic}.txt" || true
    grep -n "$INTENT" "$WORKDIR/05_consume_${topic}.txt" | head -n 20 >> "$WORKDIR/05_kafka_hits.txt" || true
  done < "$WORKDIR/05_topics_candidates.txt"

  test -s "$WORKDIR/05_kafka_hits.txt" && echo "OK" > "$WORKDIR/05_kafka_gate.txt" || echo "FAIL" > "$WORKDIR/05_kafka_gate.txt"
else
  echo "FAIL" > "$WORKDIR/05_kafka_gate.txt"
  > "$WORKDIR/05_kafka_hits.txt"
fi

# FASE 6 — BLOCKCHAIN
BC_POD=$(kubectl get pods -n $NS -l app=trisla-bc-nssmf -o jsonpath={.items[0].metadata.name})
BESU_POD=$(kubectl get pods -n $NS -l app=trisla-besu -o jsonpath={.items[0].metadata.name})

kubectl logs -n $NS "$BC_POD" --since=30m > "$WORKDIR/06_bc_logs.txt"
kubectl logs -n $NS "$BESU_POD" --since=30m > "$WORKDIR/06_besu_logs.txt"
grep -nEi "tx|hash|receipt|contract|rpc|block" "$WORKDIR/06_bc_logs.txt" | head -n 200 > "$WORKDIR/06_bc_hits.txt" || true

# FASE 7 — SEM + ML/XAI
SEM_POD=$(kubectl get pods -n $NS -l app=trisla-sem-csmf -o jsonpath={.items[0].metadata.name})
ML_POD=$(kubectl get pods -n $NS -l app=trisla-ml-nsmf -o jsonpath={.items[0].metadata.name})

kubectl logs -n $NS "$SEM_POD" --since=30m > "$WORKDIR/07_sem_logs.txt"
grep -nEi "gst|nest|ontology|reasoner|semantic" "$WORKDIR/07_sem_logs.txt" | head -n 200 > "$WORKDIR/07_sem_hits.txt" || true

kubectl logs -n $NS "$ML_POD" --since=30m > "$WORKDIR/07_ml_logs.txt"
grep -nEi "xai|shap|explain|risk_score|confidence|predict" "$WORKDIR/07_ml_logs.txt" | head -n 200 > "$WORKDIR/07_ml_hits.txt" || true
grep -qi "xai_data is not defined" "$WORKDIR/07_ml_logs.txt" && echo "FAIL" > "$WORKDIR/07_xai_gate.txt" || echo "OK" > "$WORKDIR/07_xai_gate.txt"

# FASE 8 — CHECKSUM + FINAL_GATES
sha256sum $(find "$WORKDIR" -type f | sort) > "$WORKDIR/CHECKSUMS.sha256"

cat > "$WORKDIR/FINAL_GATES.txt" <<EOF
G1 Prom 4/4: $(grep -q "prom_queries_ok 4 /4" "$WORKDIR/01_prom_gate.txt" && echo OK || echo FAIL)
G2 ACCEPT: $(test -s "$WORKDIR/04_intent_accept.txt" && echo OK || echo FAIL)
G3 Kafka: $(cat "$WORKDIR/05_kafka_gate.txt")
G4 BC: $(test -s "$WORKDIR/06_bc_hits.txt" && echo OK || echo FAIL)
G5 SEM: $(test -s "$WORKDIR/07_sem_hits.txt" && echo OK || echo FAIL)
G6 XAI: $(cat "$WORKDIR/07_xai_gate.txt")
EOF

cat "$WORKDIR/FINAL_GATES.txt"
