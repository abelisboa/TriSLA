#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/home/porvir5g/gtp5g/trisla"
OUT_DIR="${BASE_DIR}/evidencias_guardiao_deterministico"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="${OUT_DIR}/FASE_A_${TS}.log"

PROM_SVC="monitoring-kube-prometheus-prometheus"
PROM_NS="monitoring"
PROM_LOCAL="http://127.0.0.1:9090"

BB_RELEASE="blackbox-exporter"
BB_NS="monitoring"
BB_SVC="blackbox-exporter-prometheus-blackbox-exporter"
BB_SVC_FQDN="${BB_SVC}.${BB_NS}.svc.cluster.local:9115"

PROBE_NAME="trisla-transport-tcp-probe"
PROBE_NS="monitoring"
PROBE_JOB="probe/monitoring/${PROBE_NAME}"

CORE_NS="ns-1274485"

# Alvos TCP do core (ajuste se quiser adicionar/remover)
TARGETS=(
  "amf-namf.${CORE_NS}.svc.cluster.local:80"
  "smf-nsmf.${CORE_NS}.svc.cluster.local:80"
  "pcf-npcf.${CORE_NS}.svc.cluster.local:80"
  "nrf-nnrf.${CORE_NS}.svc.cluster.local:8000"
)

mkdir -p "${OUT_DIR}"

log() { echo -e "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
run() { log "+ $*"; eval "$*"; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "ERRO: comando ausente: $1"; exit 1; }
}

# URL encode simples (para queries PromQL em curl)
urlenc() {
  python3 - <<'PY' "$1"
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1], safe=""))
PY
}

pf_start() {
  # mata qualquer port-forward antigo para 9090 (best effort)
  pkill -f "kubectl -n ${PROM_NS} port-forward svc/${PROM_SVC} 9090:9090" >/dev/null 2>&1 || true
  nohup kubectl -n "${PROM_NS}" port-forward "svc/${PROM_SVC}" 9090:9090 >/tmp/pf_prom_9090.log 2>&1 &
  sleep 2
  if ! curl -s "${PROM_LOCAL}/-/ready" >/dev/null 2>&1; then
    log "ERRO: Prometheus não respondeu em ${PROM_LOCAL}. Veja /tmp/pf_prom_9090.log"
    exit 1
  fi
  log "OK: port-forward Prometheus ativo em ${PROM_LOCAL}"
}

prom_query() {
  local q="$1"
  local qe
  qe="$(urlenc "$q")"
  curl -s "${PROM_LOCAL}/api/v1/query?query=${qe}"
}

title() {
  echo
  log "=============================="
  log "$1"
  log "=============================="
}

# ---- Pré-checagens
need_cmd kubectl
need_cmd curl
need_cmd grep
need_cmd sed
need_cmd awk
need_cmd date
need_cmd python3

# Captura stdout+stderr no log
exec > >(tee -a "${OUT}") 2>&1

title "FASE A — Consolidar NASP como Guardião Determinístico (Passo 1–5)"
log "Base: ${BASE_DIR}"
log "Saída: ${OUT}"

# ---- PASSO 1: Métricas oficiais (validação operacional)
title "PASSO 1 — Validar Prometheus e fontes oficiais (Core/RAN/Transporte)"

pf_start

log "Testando API do Prometheus (up):"
run "prom_query 'up' | head -c 200; echo"

log "Validando que Probe/CRD existe (monitoring.coreos.com/v1 Probe):"
run "kubectl get crd probes.monitoring.coreos.com >/dev/null && echo 'OK: CRD Probe presente'"

# ---- PASSO 1.1: Garantir Blackbox Exporter instalado e módulo tcp_connect
title "PASSO 1.1 — Garantir Blackbox Exporter e módulo tcp_connect"

if ! kubectl get deploy -n "${BB_NS}" "${BB_RELEASE}-${BB_SVC#blackbox-exporter-}" >/dev/null 2>&1; then
  log "Blackbox exporter via Helm não encontrado com nome esperado; verificando por label..."
fi

if ! kubectl get svc -n "${BB_NS}" "${BB_SVC}" >/dev/null 2>&1; then
  log "Blackbox Service não encontrado. Instalando via Helm (prometheus-community/prometheus-blackbox-exporter)."
  run "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true"
  run "helm repo update >/dev/null 2>&1 || true"
  run "helm upgrade --install ${BB_RELEASE} prometheus-community/prometheus-blackbox-exporter -n ${BB_NS} --create-namespace"
fi

run "kubectl get pods -n ${BB_NS} -l app.kubernetes.io/name=prometheus-blackbox-exporter"
run "kubectl get svc  -n ${BB_NS} -l app.kubernetes.io/name=prometheus-blackbox-exporter"

log "Aplicando ConfigMap 'blackbox.yaml' com tcp_connect (idempotente)."
cat > /tmp/blackbox-config.yaml <<YAML
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${BB_SVC}
  namespace: ${BB_NS}
  labels:
    app.kubernetes.io/instance: ${BB_RELEASE}
    app.kubernetes.io/name: prometheus-blackbox-exporter
data:
  blackbox.yaml: |
    modules:
      http_2xx:
        http:
          follow_redirects: true
          preferred_ip_protocol: ip4
          valid_http_versions:
          - HTTP/1.1
          - HTTP/2.0
        prober: http
        timeout: 5s
      tcp_connect:
        prober: tcp
        timeout: 5s
        tcp:
          preferred_ip_protocol: ip4
YAML

run "kubectl apply -f /tmp/blackbox-config.yaml"
run "kubectl rollout restart deployment -n ${BB_NS} ${BB_RELEASE}-prometheus-blackbox-exporter || true"
run "kubectl rollout status  deployment -n ${BB_NS} ${BB_RELEASE}-prometheus-blackbox-exporter --timeout=120s || true"

log "Teste direto do blackbox (tcp_connect) contra AMF:"
run "kubectl run curl-bb --rm -i --restart=Never -n ${BB_NS} --image=curlimages/curl -- \
  curl -s 'http://${BB_SVC}:9115/probe?target=${TARGETS[0]}&module=tcp_connect' | egrep 'probe_success|probe_duration_seconds' || true"

# ---- PASSO 1.2: Garantir Probe com label release=monitoring e targets
title "PASSO 1.2 — Garantir Probe (release=monitoring) e targets TCP"

cat > /tmp/trisla-transport-probes.yaml <<YAML
apiVersion: monitoring.coreos.com/v1
kind: Probe
metadata:
  name: ${PROBE_NAME}
  namespace: ${PROBE_NS}
  labels:
    release: monitoring
spec:
  interval: 10s
  module: tcp_connect
  prober:
    url: ${BB_SVC_FQDN}
  targets:
    staticConfig:
      static:
$(for t in "${TARGETS[@]}"; do echo "        - ${t}"; done)
YAML

run "kubectl apply -f /tmp/trisla-transport-probes.yaml"

log "Aguardando 20s para o Prometheus coletar..."
sleep 20

log "Validando probe_success (deve retornar 4 séries):"
run "prom_query 'probe_success' | head -c 400; echo"
log "Validando probe_duration_seconds (deve retornar 4 séries):"
run "prom_query 'probe_duration_seconds' | head -c 400; echo"

# ---- PASSO 1.3: Validar NASP multidomain atual (cpu/mem/ue e rtt ainda pode estar null)
title "PASSO 1.3 — Validar endpoint /metrics/multidomain do NASP-Adapter (estado atual)"

run "kubectl get pod -n trisla -l app=trisla-nasp-adapter -o jsonpath='{.items[0].spec.containers[0].image}{\"\\n\"}'"
run "kubectl run curl-md --rm -i --restart=Never -n trisla --image=curlimages/curl --command -- \
  curl -s -w '\nHTTP_CODE=%{http_code}\n' http://trisla-nasp-adapter:8085/api/v1/metrics/multidomain"

# ---- PASSO 2: Thresholds oficiais (contrato)
title "PASSO 2 — Registrar thresholds oficiais por slice (contrato determinístico)"

cat > "${OUT_DIR}/contract_thresholds_${TS}.md" <<'MD'
# TriSLA — Contrato Determinístico de Sustentabilidade (FASE A)

## Fontes oficiais
- **Core**: Prometheus (cpu_pct, mem_pct) — derivados de container_* e node_*.
- **RAN**: `ran.ue.active_count` (proxy de carga).
- **Transporte**: Blackbox TCP (`probe_duration_seconds`) → RTT/latência estimada (ms).

## Thresholds (propostos — determinísticos)
### URLLC
- RTT ≤ 20 ms
- CPU ≤ 70%
- MEM ≤ 75%

### eMBB
- RTT ≤ 80 ms
- CPU ≤ 85%
- MEM ≤ 85%

### mMTC
- RTT ≤ 150 ms
- CPU ≤ 90%
- MEM ≤ 90%

## Regra
Um SLA só é materializado se **Core && RAN && Transporte** forem sustentáveis no momento do instantiate.
MD

log "Contrato salvo em: ${OUT_DIR}/contract_thresholds_${TS}.md"

# ---- PASSO 3: PromQL recomendado para RTT (pior caso = max)
title "PASSO 3 — RTT real: query recomendada (pior caso) e evidência"

# 1) pegar p95 por instance via query_range e calcular offline seria o mais “correto”.
# Porém, para gate determinístico simples: usar max do instantâneo é aceitável e estável.
# Vamos registrar duas queries:
# - instant worst-case: max by() (probe_duration_seconds{job="..."} )*1000
# - 5m worst-case: max_over_time(probe_duration_seconds{job="..."}[5m])*1000 (precisa range)
# Como max_over_time não funcionou no instant query, registramos com query_range.

Q_INSTANT="max by (job) (probe_duration_seconds{job=\"${PROBE_JOB}\"}) * 1000"
log "Query instant (worst-case por job): ${Q_INSTANT}"
run "prom_query \"${Q_INSTANT}\" | head -c 500; echo"

START="$(date -d '5 minutes ago' +%s)"
END="$(date +%s)"
STEP=15

Q_RANGE="probe_duration_seconds{job=\"${PROBE_JOB}\"}"
log "Query range (5m) para cálculo determinístico em batch: ${Q_RANGE}"
run "curl -s \"${PROM_LOCAL}/api/v1/query_range?query=$(urlenc "${Q_RANGE}")&start=${START}&end=${END}&step=${STEP}\" | head -c 300; echo"

cat > "${OUT_DIR}/transport_promql_${TS}.md" <<MD
# Transporte RTT — PromQL (FASE A)

## Instantâneo (gate simples)
\`\`\`
${Q_INSTANT}
\`\`\`

## Série temporal (gate robusto em janela)
Use query_range + agregação offline (ou promQL avançado em regra):
\`\`\`
${Q_RANGE}
\`\`\`

Recomendação DevOps: para decisão de **admissão**, usar **pior caso** (max) e janela curta (2–5 min).
MD

log "PromQL salvo em: ${OUT_DIR}/transport_promql_${TS}.md"

# ---- PASSO 4: Decisão arquitetural (registrar recomendação)
title "PASSO 4 — Decisão arquitetural (DevOps): RTT = pior caso"

cat > "${OUT_DIR}/decision_rtt_policy_${TS}.md" <<'MD'
# Política de RTT para Sustentabilidade (FASE A)

## Recomendação
Usar **RTT pior caso** entre os endpoints monitorados (max), pois:
- reduz risco de aceitar SLA com transporte degradado em parte do core;
- torna o gate determinístico e conservador;
- evita “média que mascara outliers”.

## Política (resumo)
- RTT_transport = max( probe_duration_seconds * 1000 ) sobre o job do Probe TriSLA.
- Janela recomendada: 2–5 minutos.
MD

log "Política salva em: ${OUT_DIR}/decision_rtt_policy_${TS}.md"

# ---- PASSO 5: Checklist final e saída
title "PASSO 5 — Checklist final (PASS/FAIL)"

PASS=1

# probe_success tem de ter dados
if ! prom_query "probe_success" | grep -q "\"result\":\\s*\\["; then
  log "FAIL: probe_success não retornou séries."
  PASS=0
else
  # verifica pelo menos 4 instâncias
  COUNT="$(prom_query "probe_success" | grep -o '"instance"' | wc -l | tr -d ' ')"
  if [[ "${COUNT}" -lt 4 ]]; then
    log "FAIL: probe_success retornou menos de 4 instâncias (count=${COUNT})."
    PASS=0
  else
    log "PASS: probe_success retornou ${COUNT} instâncias."
  fi
fi

# multidomain tem de responder 200
MD_OUT="$(kubectl run curl-md2 --rm -i --restart=Never -n trisla --image=curlimages/curl --command -- \
  curl -s -w '\nHTTP_CODE=%{http_code}\n' http://trisla-nasp-adapter:8085/api/v1/metrics/multidomain || true)"
echo "${MD_OUT}" | tail -n 2 | grep -q "HTTP_CODE=200" && log "PASS: multidomain HTTP 200" || { log "FAIL: multidomain não retornou 200"; PASS=0; }

if [[ "${PASS}" -eq 1 ]]; then
  log "✅ FASE A CONCLUÍDA (telemetria+contratos+validações). Próximo: FASE B (alterar capacity_accounting.py para usar RTT)."
  exit 0
else
  log "❌ FASE A INCOMPLETA. Corrija os FAILs acima antes de avançar."
  exit 2
fi
