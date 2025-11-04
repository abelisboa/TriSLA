# 🖥️ Comandos Manuais para Execução no Node1
## Criação de Slices, Testes de Estresse e Coleta de Métricas

**Ambiente:** Node1 (via SSH: `porvir5g@ppgca.unisinos.br` → `node006`)  
**Namespace:** `trisla-nsp`  
**Data:** $(date +"%Y-%m-%d")

---

## 📋 Pré-requisitos

Antes de começar, verifique:

```bash
# 1. Conectar ao node1
ssh porvir5g@ppgca.unisinos.br
ssh node006

# 2. Verificar namespace
kubectl get ns trisla-nsp

# 3. Verificar pods do TriSLA
kubectl get pods -n trisla-nsp

# 4. Verificar serviços
kubectl get svc -n trisla-nsp

# 5. Verificar se Prometheus está acessível
kubectl get svc -n monitoring | grep prometheus
```

---

## 🔧 1. Configurar Variáveis de Ambiente

```bash
# Definir variáveis (ajustar conforme necessário)
export NAMESPACE=trisla-nsp
export API_SERVICE=trisla-portal-api  # Ajustar nome do serviço
export API_PORT=8000
export API_URL=http://${API_SERVICE}.${NAMESPACE}.svc.cluster.local:${API_PORT}
export PROMETHEUS_URL=http://prometheus.monitoring.svc.cluster.local:9090

# Criar diretório para evidências
mkdir -p ~/trisla-tests/$(date +%Y%m%d_%H%M%S)
export TEST_DIR=~/trisla-tests/$(date +%Y%m%d_%H%M%S)
cd $TEST_DIR

echo "Diretório de testes: $TEST_DIR"
echo "API URL: $API_URL"
echo "Prometheus URL: $PROMETHEUS_URL"
```

---

## 📝 2. Verificar Conectividade com a API

```bash
# Testar health check da API
kubectl run -it --rm test-curl --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s $API_URL/api/v1/health | jq .

# Ou via port-forward (em outro terminal)
# kubectl port-forward -n $NAMESPACE svc/$API_SERVICE 8000:8000
# curl http://localhost:8000/api/v1/health | jq .
```

---

## 🎯 3. Criar Slices - Cenário URLLC (Telemedicina)

```bash
# Criar slice URLLC via NLP
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
kubectl run -it --rm create-slice-urllc-$TIMESTAMP --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -X POST $API_URL/api/v1/slices \
    -H "Content-Type: application/json" \
    -d '{"descricao":"cirurgia remota 5G com latência ultra baixa e alta confiabilidade para telemedicina"}' \
    -w "\nHTTP_CODE:%{http_code}\n" \
    > ${TEST_DIR}/urllc_create_${TIMESTAMP}.json

# Ver resultado
cat ${TEST_DIR}/urllc_create_${TIMESTAMP}.json | jq .

# Extrair job_id (se houver)
JOB_URLLC=$(cat ${TEST_DIR}/urllc_create_${TIMESTAMP}.json | jq -r '.job_id // empty')
echo "Job ID URLLC: $JOB_URLLC"

# Verificar status do job (se job_id foi retornado)
if [ -n "$JOB_URLLC" ] && [ "$JOB_URLLC" != "null" ] && [ "$JOB_URLLC" != "" ]; then
  echo "Verificando status do job..."
  kubectl run -it --rm check-job-urllc-$TIMESTAMP --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
    curl -s $API_URL/api/v1/jobs/$JOB_URLLC | jq .
fi
```

---

## 📺 4. Criar Slices - Cenário eMBB (Streaming 4K)

```bash
# Criar slice eMBB via NLP
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
kubectl run -it --rm create-slice-embb-$TIMESTAMP --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -X POST $API_URL/api/v1/slices \
    -H "Content-Type: application/json" \
    -d '{"descricao":"streaming 4K e realidade aumentada com alta vazão de banda"}' \
    -w "\nHTTP_CODE:%{http_code}\n" \
    > ${TEST_DIR}/embb_create_${TIMESTAMP}.json

# Ver resultado
cat ${TEST_DIR}/embb_create_${TIMESTAMP}.json | jq .

# Extrair job_id
JOB_EMBB=$(cat ${TEST_DIR}/embb_create_${TIMESTAMP}.json | jq -r '.job_id // empty')
echo "Job ID eMBB: $JOB_EMBB"

# Verificar status do job
if [ -n "$JOB_EMBB" ] && [ "$JOB_EMBB" != "null" ] && [ "$JOB_EMBB" != "" ]; then
  kubectl run -it --rm check-job-embb-$TIMESTAMP --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
    curl -s $API_URL/api/v1/jobs/$JOB_EMBB | jq .
fi
```

---

## 🌐 5. Criar Slices - Cenário mMTC (IoT Massivo)

```bash
# Criar slice mMTC via NLP
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
kubectl run -it --rm create-slice-mmtc-$TIMESTAMP --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -X POST $API_URL/api/v1/slices \
    -H "Content-Type: application/json" \
    -d '{"descricao":"sensores IoT industriais massivos com milhares de dispositivos"}' \
    -w "\nHTTP_CODE:%{http_code}\n" \
    > ${TEST_DIR}/mmtc_create_${TIMESTAMP}.json

# Ver resultado
cat ${TEST_DIR}/mmtc_create_${TIMESTAMP}.json | jq .

# Extrair job_id
JOB_MMTC=$(cat ${TEST_DIR}/mmtc_create_${TIMESTAMP}.json | jq -r '.job_id // empty')
echo "Job ID mMTC: $JOB_MMTC"

# Verificar status do job
if [ -n "$JOB_MMTC" ] && [ "$JOB_MMTC" != "null" ] && [ "$JOB_MMTC" != "" ]; then
  kubectl run -it --rm check-job-mmtc-$TIMESTAMP --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
    curl -s $API_URL/api/v1/jobs/$JOB_MMTC | jq .
fi
```

---

## 🔥 6. Testes de Estresse - URLLC

```bash
# Configurar parâmetros do teste
CONCURRENT=10
TOTAL_REQUESTS=50
DELAY=0.2

echo "Iniciando teste de estresse URLLC..."
echo "Requisições simultâneas: $CONCURRENT"
echo "Total de requisições: $TOTAL_REQUESTS"

# Executar requisições em paralelo usando xargs
seq 1 $TOTAL_REQUESTS | xargs -n1 -P$CONCURRENT -I{} bash -c '
  TIMESTAMP=$(date +%s%N)
  RESPONSE=$(kubectl run --rm --restart=Never -i test-urllc-{}-${TIMESTAMP} --image=curlimages/curl:latest -n '$NAMESPACE' -- \
    curl -s -X POST '$API_URL'/api/v1/slices \
      -H "Content-Type: application/json" \
      -d "{\"descricao\":\"cirurgia remota 5G (stress test #{})\"}" \
      -w "\n%{http_code}\n%{time_total}")
  HTTP_CODE=$(echo "$RESPONSE" | tail -n2 | head -n1)
  TIME_TOTAL=$(echo "$RESPONSE" | tail -n1)
  echo "Request {}: HTTP $HTTP_CODE, Time: ${TIME_TOTAL}s" >> '${TEST_DIR}'/stress_urllc.log
  sleep '$DELAY'
'

# Resumo dos resultados
echo "=== Resumo URLLC ==="
SUCCESS=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_urllc.log | wc -l)
TOTAL=$(wc -l < ${TEST_DIR}/stress_urllc.log)
echo "Sucessos: $SUCCESS / $TOTAL"
echo "Taxa de sucesso: $(echo "scale=2; $SUCCESS * 100 / $TOTAL" | bc)%"
echo "Ver log completo: cat ${TEST_DIR}/stress_urllc.log"
```

---

## 🔥 7. Testes de Estresse - eMBB

```bash
# Configurar parâmetros
CONCURRENT=10
TOTAL_REQUESTS=50
DELAY=0.2

echo "Iniciando teste de estresse eMBB..."

# Executar requisições
seq 1 $TOTAL_REQUESTS | xargs -n1 -P$CONCURRENT -I{} bash -c '
  TIMESTAMP=$(date +%s%N)
  RESPONSE=$(kubectl run --rm --restart=Never -i test-embb-{}-${TIMESTAMP} --image=curlimages/curl:latest -n '$NAMESPACE' -- \
    curl -s -X POST '$API_URL'/api/v1/slices \
      -H "Content-Type: application/json" \
      -d "{\"descricao\":\"streaming 4K alta vazão (stress test #{})\"}" \
      -w "\n%{http_code}\n%{time_total}")
  HTTP_CODE=$(echo "$RESPONSE" | tail -n2 | head -n1)
  TIME_TOTAL=$(echo "$RESPONSE" | tail -n1)
  echo "Request {}: HTTP $HTTP_CODE, Time: ${TIME_TOTAL}s" >> '${TEST_DIR}'/stress_embb.log
  sleep '$DELAY'
'

# Resumo
echo "=== Resumo eMBB ==="
SUCCESS=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_embb.log | wc -l)
TOTAL=$(wc -l < ${TEST_DIR}/stress_embb.log)
echo "Sucessos: $SUCCESS / $TOTAL"
echo "Taxa de sucesso: $(echo "scale=2; $SUCCESS * 100 / $TOTAL" | bc)%"
```

---

## 🔥 8. Testes de Estresse - mMTC

```bash
# Configurar parâmetros
CONCURRENT=10
TOTAL_REQUESTS=50
DELAY=0.2

echo "Iniciando teste de estresse mMTC..."

# Executar requisições
seq 1 $TOTAL_REQUESTS | xargs -n1 -P$CONCURRENT -I{} bash -c '
  TIMESTAMP=$(date +%s%N)
  RESPONSE=$(kubectl run --rm --restart=Never -i test-mmtc-{}-${TIMESTAMP} --image=curlimages/curl:latest -n '$NAMESPACE' -- \
    curl -s -X POST '$API_URL'/api/v1/slices \
      -H "Content-Type: application/json" \
      -d "{\"descricao\":\"sensores IoT massivos (stress test #{})\"}" \
      -w "\n%{http_code}\n%{time_total}")
  HTTP_CODE=$(echo "$RESPONSE" | tail -n2 | head -n1)
  TIME_TOTAL=$(echo "$RESPONSE" | tail -n1)
  echo "Request {}: HTTP $HTTP_CODE, Time: ${TIME_TOTAL}s" >> '${TEST_DIR}'/stress_mmtc.log
  sleep '$DELAY'
'

# Resumo
echo "=== Resumo mMTC ==="
SUCCESS=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_mmtc.log | wc -l)
TOTAL=$(wc -l < ${TEST_DIR}/stress_mmtc.log)
echo "Sucessos: $SUCCESS / $TOTAL"
echo "Taxa de sucesso: $(echo "scale=2; $SUCCESS * 100 / $TOTAL" | bc)%"
```

---

## 📊 9. Coletar Métricas do Prometheus - CPU Usage

```bash
# Criar pod temporário para acessar Prometheus
kubectl run -it --rm prometheus-client --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=rate(container_cpu_usage_seconds_total{namespace=\"${NAMESPACE}\"}[1m])" \
    > ${TEST_DIR}/prometheus_cpu_usage.json

# Ver resultado formatado
cat ${TEST_DIR}/prometheus_cpu_usage.json | jq '.data.result[] | {pod: .metric.pod, cpu_rate: .value[1]}'
```

---

## 📊 10. Coletar Métricas do Prometheus - Memory Usage

```bash
kubectl run -it --rm prometheus-client-mem --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=container_memory_usage_bytes{namespace=\"${NAMESPACE}\"}" \
    > ${TEST_DIR}/prometheus_memory_usage.json

# Converter bytes para MB e exibir
cat ${TEST_DIR}/prometheus_memory_usage.json | jq -r '.data.result[] | "Pod: \(.metric.pod), Memory: \(.value[1] | tonumber / 1024 / 1024 | floor) MB"'
```

---

## 📊 11. Coletar Métricas do Prometheus - Latência p99

```bash
kubectl run -it --rm prometheus-client-lat --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{namespace=\"${NAMESPACE}\"}[5m])) by (le, pod))" \
    > ${TEST_DIR}/prometheus_latency_p99.json

# Converter segundos para milissegundos
cat ${TEST_DIR}/prometheus_latency_p99.json | jq -r '.data.result[] | 
  if .value[1] != null then 
    "Pod: \(.metric.pod), Latência p99: \(.value[1] | tonumber * 1000 | floor) ms"
  else 
    "Pod: \(.metric.pod), Latência p99: N/A"
  end'
```

---

## 📊 12. Coletar Métricas do Prometheus - Latência p90 e p50

```bash
# Latência p90
kubectl run -it --rm prometheus-client-lat90 --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=histogram_quantile(0.90, sum(rate(http_request_duration_seconds_bucket{namespace=\"${NAMESPACE}\"}[5m])) by (le, pod))" \
    > ${TEST_DIR}/prometheus_latency_p90.json

# Latência p50 (mediana)
kubectl run -it --rm prometheus-client-lat50 --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{namespace=\"${NAMESPACE}\"}[5m])) by (le, pod))" \
    > ${TEST_DIR}/prometheus_latency_p50.json

# Exibir resultados
echo "=== Latência p90 ==="
cat ${TEST_DIR}/prometheus_latency_p90.json | jq -r '.data.result[] | 
  if .value[1] != null then 
    "Pod: \(.metric.pod), Latência p90: \(.value[1] | tonumber * 1000 | floor) ms"
  else 
    "Pod: \(.metric.pod), Latência p90: N/A"
  end'

echo ""
echo "=== Latência p50 (Mediana) ==="
cat ${TEST_DIR}/prometheus_latency_p50.json | jq -r '.data.result[] | 
  if .value[1] != null then 
    "Pod: \(.metric.pod), Latência p50: \(.value[1] | tonumber * 1000 | floor) ms"
  else 
    "Pod: \(.metric.pod), Latência p50: N/A"
  end'
```

---

## 📊 13. Coletar Métricas do Prometheus - Taxa de Erros HTTP

```bash
kubectl run -it --rm prometheus-client-errors --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=rate(http_requests_total{namespace=\"${NAMESPACE}\",status=~\"5..\"}[5m])" \
    > ${TEST_DIR}/prometheus_http_errors.json

# Exibir taxa de erros por pod
cat ${TEST_DIR}/prometheus_http_errors.json | jq -r '.data.result[] | 
  if .value[1] != null then 
    "Pod: \(.metric.pod), Taxa de Erro 5xx: \(.value[1]) req/s"
  else 
    "Pod: \(.metric.pod), Taxa de Erro 5xx: 0 req/s"
  end'
```

---

## 📊 14. Coletar Métricas do Prometheus - Taxa Total de Requisições

```bash
kubectl run -it --rm prometheus-client-total --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=rate(http_requests_total{namespace=\"${NAMESPACE}\"}[5m])" \
    > ${TEST_DIR}/prometheus_http_total.json

# Exibir taxa total
cat ${TEST_DIR}/prometheus_http_total.json | jq -r '.data.result[] | 
  "Pod: \(.metric.pod), Método: \(.metric.method // "N/A"), Taxa: \(.value[1]) req/s"'
```

---

## 📊 15. Coletar Métricas do Prometheus - Restarts de Pods

```bash
kubectl run -it --rm prometheus-client-restarts --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=kube_pod_container_status_restarts_total{namespace=\"${NAMESPACE}\"}" \
    > ${TEST_DIR}/prometheus_pod_restarts.json

# Exibir restarts
cat ${TEST_DIR}/prometheus_pod_restarts.json | jq -r '.data.result[] | 
  "Pod: \(.metric.pod), Container: \(.metric.container}, Restarts: \(.value[1])"'
```

---

## 📊 16. Coletar Métricas do Prometheus - Status dos Pods (Ready)

```bash
kubectl run -it --rm prometheus-client-ready --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode "query=kube_pod_status_ready{namespace=\"${NAMESPACE}\",condition=\"true\"}" \
    > ${TEST_DIR}/prometheus_pod_ready.json

# Exibir status ready
cat ${TEST_DIR}/prometheus_pod_ready.json | jq -r '.data.result[] | 
  "Pod: \(.metric.pod), Ready: \(.value[1])"'
```

---

## 📊 17. Coletar Séries Temporais - CPU (últimos 30 minutos)

```bash
# Calcular timestamps (últimos 30 minutos)
END_TIME=$(date +%s)
START_TIME=$((END_TIME - 1800))  # 30 minutos atrás
STEP=15s

kubectl run -it --rm prometheus-client-timeseries --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query_range" \
    --data-urlencode "query=rate(container_cpu_usage_seconds_total{namespace=\"${NAMESPACE}\"}[1m])" \
    --data-urlencode "start=${START_TIME}" \
    --data-urlencode "end=${END_TIME}" \
    --data-urlencode "step=${STEP}" \
    > ${TEST_DIR}/prometheus_cpu_timeseries.json

echo "Série temporal de CPU coletada (últimos 30 minutos)"
echo "Arquivo: ${TEST_DIR}/prometheus_cpu_timeseries.json"
```

---

## 📊 18. Coletar Séries Temporais - Memory (últimos 30 minutos)

```bash
END_TIME=$(date +%s)
START_TIME=$((END_TIME - 1800))
STEP=15s

kubectl run -it --rm prometheus-client-mem-ts --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query_range" \
    --data-urlencode "query=container_memory_usage_bytes{namespace=\"${NAMESPACE}\"}" \
    --data-urlencode "start=${START_TIME}" \
    --data-urlencode "end=${END_TIME}" \
    --data-urlencode "step=${STEP}" \
    > ${TEST_DIR}/prometheus_memory_timeseries.json

echo "Série temporal de memória coletada"
```

---

## 📊 19. Coletar Séries Temporais - Latência p99 (últimos 30 minutos)

```bash
END_TIME=$(date +%s)
START_TIME=$((END_TIME - 1800))
STEP=15s

kubectl run -it --rm prometheus-client-lat-ts --image=curlimages/curl:latest --restart=Never -n $NAMESPACE -- \
  curl -s -G "${PROMETHEUS_URL}/api/v1/query_range" \
    --data-urlencode "query=histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{namespace=\"${NAMESPACE}\"}[5m])) by (le, pod))" \
    --data-urlencode "start=${START_TIME}" \
    --data-urlencode "end=${END_TIME}" \
    --data-urlencode "step=${STEP}" \
    > ${TEST_DIR}/prometheus_latency_timeseries.json

echo "Série temporal de latência p99 coletada"
```

---

## 📋 20. Resumo dos Resultados

```bash
echo "==============================================="
echo "📊 RESUMO DOS TESTES - TriSLA@NASP"
echo "==============================================="
echo "Data: $(date)"
echo "Diretório: $TEST_DIR"
echo ""

# Resumo de criação de slices
echo "=== Criação de Slices ==="
echo "URLLC: $(ls -1 ${TEST_DIR}/urllc_create_*.json 2>/dev/null | wc -l) arquivo(s)"
echo "eMBB:  $(ls -1 ${TEST_DIR}/embb_create_*.json 2>/dev/null | wc -l) arquivo(s)"
echo "mMTC:  $(ls -1 ${TEST_DIR}/mmtc_create_*.json 2>/dev/null | wc -l) arquivo(s)"
echo ""

# Resumo de testes de estresse
echo "=== Testes de Estresse ==="
if [ -f ${TEST_DIR}/stress_urllc.log ]; then
  SUCCESS_URLLC=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_urllc.log | wc -l)
  TOTAL_URLLC=$(wc -l < ${TEST_DIR}/stress_urllc.log)
  echo "URLLC: $SUCCESS_URLLC / $TOTAL_URLLC sucessos"
fi
if [ -f ${TEST_DIR}/stress_embb.log ]; then
  SUCCESS_EMBB=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_embb.log | wc -l)
  TOTAL_EMBB=$(wc -l < ${TEST_DIR}/stress_embb.log)
  echo "eMBB:  $SUCCESS_EMBB / $TOTAL_EMBB sucessos"
fi
if [ -f ${TEST_DIR}/stress_mmtc.log ]; then
  SUCCESS_MMTC=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_mmtc.log | wc -l)
  TOTAL_MMTC=$(wc -l < ${TEST_DIR}/stress_mmtc.log)
  echo "mMTC:  $SUCCESS_MMTC / $TOTAL_MMTC sucessos"
fi
echo ""

# Resumo de métricas
echo "=== Métricas Coletadas ==="
echo "CPU Usage: $(ls -1 ${TEST_DIR}/prometheus_cpu_usage.json 2>/dev/null | wc -l) arquivo(s)"
echo "Memory:    $(ls -1 ${TEST_DIR}/prometheus_memory_usage.json 2>/dev/null | wc -l) arquivo(s)"
echo "Latência:  $(ls -1 ${TEST_DIR}/prometheus_latency_*.json 2>/dev/null | wc -l) arquivo(s)"
echo ""

# Listar todos os arquivos
echo "=== Arquivos Gerados ==="
ls -lh ${TEST_DIR}/
echo ""

echo "==============================================="
```

---

## 📝 21. Exportar Resultados (Opcional)

```bash
# Criar arquivo consolidado com todos os resultados
SUMMARY_FILE=${TEST_DIR}/resumo_completo_$(date +%Y%m%d_%H%M%S).txt
cat > $SUMMARY_FILE << EOF
===============================================
RESUMO COMPLETO DE TESTES - TriSLA@NASP
===============================================
Data: $(date)
Ambiente: Node1 (NASP - UNISINOS)
Namespace: $NAMESPACE

CRIAÇÃO DE SLICES:
------------------
$(for scen in urllc embb mmtc; do
  files=$(ls -1 ${TEST_DIR}/${scen}_create_*.json 2>/dev/null)
  if [ -n "$files" ]; then
    echo "$scen:"
    for file in $files; do
      echo "  - $(basename $file)"
      cat $file | jq -r '.job_id // .id // "N/A"' | sed 's/^/    Job ID: /'
    done
  fi
done)

TESTES DE ESTRESSE:
-------------------
$(if [ -f ${TEST_DIR}/stress_urllc.log ]; then
  SUCCESS=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_urllc.log | wc -l)
  TOTAL=$(wc -l < ${TEST_DIR}/stress_urllc.log)
  echo "URLLC: $SUCCESS / $TOTAL sucessos ($(echo "scale=2; $SUCCESS * 100 / $TOTAL" | bc)%)"
fi)
$(if [ -f ${TEST_DIR}/stress_embb.log ]; then
  SUCCESS=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_embb.log | wc -l)
  TOTAL=$(wc -l < ${TEST_DIR}/stress_embb.log)
  echo "eMBB:  $SUCCESS / $TOTAL sucessos ($(echo "scale=2; $SUCCESS * 100 / $TOTAL" | bc)%)"
fi)
$(if [ -f ${TEST_DIR}/stress_mmtc.log ]; then
  SUCCESS=$(grep "HTTP 200\|HTTP 201\|HTTP 202" ${TEST_DIR}/stress_mmtc.log | wc -l)
  TOTAL=$(wc -l < ${TEST_DIR}/stress_mmtc.log)
  echo "mMTC:  $SUCCESS / $TOTAL sucessos ($(echo "scale=2; $SUCCESS * 100 / $TOTAL" | bc)%)"
fi)

MÉTRICAS PROMETHEUS:
--------------------
$(ls -1 ${TEST_DIR}/prometheus_*.json 2>/dev/null | sed 's|.*/|  - |' | head -10)

ARQUIVOS COMPLETOS:
-------------------
$(ls -lh ${TEST_DIR} | awk '{print $9, "(" $5 ")"}' | grep -v "^total")

===============================================
EOF

echo "Resumo completo salvo em: $SUMMARY_FILE"
cat $SUMMARY_FILE
```

---

## 📤 22. Copiar Resultados para PC Local (Opcional)

```bash
# No terminal do seu PC local (NÃO no node1):
# scp -o ProxyJump=porvir5g@ppgca.unisinos.br porvir5g@node006:~/trisla-tests/* /caminho/local/

# Ou compactar e copiar
# No node1:
cd ~/trisla-tests
tar -czf resultados_$(date +%Y%m%d_%H%M%S).tar.gz $(date +%Y%m%d_%H%M%S)
# Depois copiar o arquivo .tar.gz usando scp
```

---

## 🔍 23. Verificar Logs dos Pods

```bash
# Ver logs dos módulos TriSLA durante os testes
echo "=== Logs SEM-NSMF ==="
kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=sem-nsmf --tail=50

echo ""
echo "=== Logs ML-NSMF ==="
kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=ml-nsmf --tail=50

echo ""
echo "=== Logs BC-NSSMF ==="
kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=bc-nssmf --tail=50

# Salvar logs em arquivo
kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=sem-nsmf > ${TEST_DIR}/logs_sem_nsmf.txt
kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=ml-nsmf > ${TEST_DIR}/logs_ml_nsmf.txt
kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=bc-nssmf > ${TEST_DIR}/logs_bc_nssmf.txt
```

---

## 📊 24. Verificar Status dos Pods Após Testes

```bash
echo "=== Status dos Pods ==="
kubectl get pods -n $NAMESPACE -o wide

echo ""
echo "=== Recursos Utilizados ==="
kubectl top pods -n $NAMESPACE

echo ""
echo "=== Eventos Recentes ==="
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -20
```

---

## 🎯 25. Análise Rápida de Métricas

```bash
# Analisar CPU por pod
echo "=== CPU Usage por Pod ==="
cat ${TEST_DIR}/prometheus_cpu_usage.json | jq -r '.data.result[] | 
  "\(.metric.pod): \(.value[1])"'

# Analisar memória por pod
echo ""
echo "=== Memory Usage por Pod ==="
cat ${TEST_DIR}/prometheus_memory_usage.json | jq -r '.data.result[] | 
  "\(.metric.pod): \(.value[1] | tonumber / 1024 / 1024 | floor) MB"'

# Analisar latência p99
echo ""
echo "=== Latência p99 por Pod ==="
cat ${TEST_DIR}/prometheus_latency_p99.json | jq -r '.data.result[] | 
  if .value[1] != null then 
    "\(.metric.pod): \(.value[1] | tonumber * 1000 | floor) ms"
  else 
    "\(.metric.pod): N/A"
  end'
```

---

## 💡 Dicas e Observações

1. **Execução Sequencial**: Os comandos acima podem ser executados um por vez, copiando e colando no terminal do node1.

2. **Ajustar Parâmetros**: Ajuste `CONCURRENT`, `TOTAL_REQUESTS` e `DELAY` nos testes de estresse conforme necessário.

3. **Verificar Nomes de Serviços**: Antes de começar, verifique os nomes corretos dos serviços:
   ```bash
   kubectl get svc -n $NAMESPACE
   ```

4. **Ajustar URL do Prometheus**: Se o Prometheus estiver em outro namespace ou com outro nome:
   ```bash
   kubectl get svc -n monitoring | grep prometheus
   # Ajustar PROMETHEUS_URL conforme necessário
   ```

5. **Limpar Pods Temporários**: Os pods criados com `kubectl run` são automaticamente removidos com `--rm`, mas pode haver resíduos. Para limpar:
   ```bash
   kubectl delete pods -n $NAMESPACE --field-selector=status.phase=Succeeded
   ```

6. **Exportar para Análise**: Use os arquivos JSON gerados para análise posterior no seu PC local com ferramentas como `jq`, Python, ou Excel.

---

## 📚 Estrutura Final de Arquivos

Após executar todos os comandos, você terá em `$TEST_DIR`:

```
~/trisla-tests/YYYYMMDD_HHMMSS/
├── urllc_create_*.json          # Criação slice URLLC
├── embb_create_*.json           # Criação slice eMBB
├── mmtc_create_*.json           # Criação slice mMTC
├── stress_urllc.log             # Logs teste estresse URLLC
├── stress_embb.log               # Logs teste estresse eMBB
├── stress_mmtc.log               # Logs teste estresse mMTC
├── prometheus_cpu_usage.json    # Métricas CPU
├── prometheus_memory_usage.json # Métricas memória
├── prometheus_latency_p*.json   # Métricas latência
├── prometheus_http_*.json       # Métricas HTTP
├── prometheus_pod_*.json         # Status dos pods
├── prometheus_*_timeseries.json # Séries temporais
├── logs_*.txt                    # Logs dos pods
└── resumo_completo_*.txt        # Resumo consolidado
```

---

**Última atualização:** $(date)  
**Versão:** 1.0  
**Autor:** Abel José Rodrigues Lisboa





