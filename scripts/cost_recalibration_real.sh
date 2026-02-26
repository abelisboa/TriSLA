#!/usr/bin/env bash
set -e

NS=trisla
ADAPTER_URL="http://trisla-nasp-adapter:8085/api/v1/metrics/multidomain"

echo "=============================="
echo " BASELINE (5 amostras)"
echo "=============================="

CPU_SUM=0
MEM_SUM=0

get_metric() {
  kubectl run curl-md --quiet --rm -i --restart=Never \
    --image=curlimages/curl:8.5.0 -n $NS -- \
    curl -s $ADAPTER_URL 2>/dev/null \
  | sed -n '/^{/,$p' \
  | jq -r "$1"
}

for i in {1..5}; do
  CPU=$(get_metric '.core.upf.cpu_pct')
  MEM=$(get_metric '.core.upf.mem_pct')

  echo "Amostra $i → CPU=$CPU MEM=$MEM"

  CPU_SUM=$(echo "$CPU_SUM + $CPU" | bc -l)
  MEM_SUM=$(echo "$MEM_SUM + $MEM" | bc -l)

  sleep 3
done

CPU_BASE=$(echo "scale=4; $CPU_SUM / 5" | bc -l)
MEM_BASE=$(echo "scale=4; $MEM_SUM / 5" | bc -l)

echo ""
echo "Baseline médio:"
echo "CPU_BASE=$CPU_BASE"
echo "MEM_BASE=$MEM_BASE"

echo ""
echo "=============================="
echo " CRIANDO SLA eMBB TESTE"
echo "=============================="

NSI_ID="ev-cost-$(date +%s)"

kubectl run curl-inst --quiet --rm -i --restart=Never \
  --image=curlimages/curl:8.5.0 -n $NS -- \
  curl -s -X POST http://trisla-nasp-adapter:8085/api/v1/nsi/instantiate \
  -H "Content-Type: application/json" \
  -d "{\"nsiId\":\"$NSI_ID\",\"sliceType\":\"eMBB\"}" \
  | sed -n '/^{/,$p' > /dev/null

sleep 10

echo ""
echo "=============================="
echo " MÉTRICA APÓS SLA"
echo "=============================="

CPU_AFTER=$(get_metric '.core.upf.cpu_pct')
MEM_AFTER=$(get_metric '.core.upf.mem_pct')

echo "CPU_AFTER=$CPU_AFTER"
echo "MEM_AFTER=$MEM_AFTER"

CPU_DELTA=$(echo "scale=4; $CPU_AFTER - $CPU_BASE" | bc -l)
MEM_DELTA=$(echo "scale=4; $MEM_AFTER - $MEM_BASE" | bc -l)

echo ""
echo "=============================="
echo " DELTA REAL"
echo "=============================="
echo "CPU_DELTA=$CPU_DELTA"
echo "MEM_DELTA=$MEM_DELTA"

echo ""
echo "=============================="
echo " COST SUGERIDO"
echo "=============================="

COST_EMBB=$(printf "%.0f" $(echo "$CPU_DELTA * 1.5" | bc -l))
COST_URLLC=$(printf "%.0f" $(echo "$CPU_DELTA * 2.0" | bc -l))
COST_MMTC=$(printf "%.0f" $(echo "$CPU_DELTA * 0.7" | bc -l))

echo "COST_EMBB_CORE=$COST_EMBB"
echo "COST_URLLC_CORE=$COST_URLLC"
echo "COST_MMTC_CORE=$COST_MMTC"

echo ""
echo "Script finalizado."
