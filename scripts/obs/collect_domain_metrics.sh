#!/usr/bin/env bash
set -euo pipefail

EVID=""
CORE_NS="ns-1274485"
UERANSIM_NS="ueransim"

usage() {
  echo "Usage: $0 --evid <evidence_dir> [--core-ns <ns>] [--ueransim-ns <ns>]"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --evid) EVID="$2"; shift 2;;
    --core-ns) CORE_NS="$2"; shift 2;;
    --ueransim-ns) UERANSIM_NS="$2"; shift 2;;
    *) usage; exit 1;;
  esac
done

if [ -z "${EVID}" ]; then
  usage; exit 1
fi

mkdir -p "${EVID}/obs"

echo "==== CORE (auditável) ===="

# 1) UPF CPU/Mem %: preferir metrics-server (kubectl top). Se não houver, tentar Prometheus via URL do naspAdapter (se exposto).
HAS_METRICS_API="$(kubectl get apiservices 2>/dev/null | grep -c metrics.k8s.io || true)"

# Descobrir UPF pod (heurística auditável: nome contém 'upf')
UPF_POD="$(kubectl get pods -n "${CORE_NS}" --no-headers 2>/dev/null | awk '{print $1}' | grep -i upf | head -n 1 || true)"
if [ -z "${UPF_POD}" ]; then
  echo "❌ FAIL: não encontrei pod UPF no namespace ${CORE_NS}"
  kubectl get pods -n "${CORE_NS}" -o wide > "${EVID}/obs/core_pods.txt" || true
  exit 2
fi

echo "UPF_POD=${UPF_POD}" | tee "${EVID}/obs/upf_pod.txt"

if [ "${HAS_METRICS_API}" -gt 0 ]; then
  echo "Fonte: metrics-server (kubectl top)"
  kubectl top pod -n "${CORE_NS}" "${UPF_POD}" | tee "${EVID}/obs/upf_top.txt"
else
  echo "⚠️ WARN: metrics-server não disponível. Salvando evidência e seguindo sem CPU/Mem %."
  echo "metrics-server ausente" > "${EVID}/obs/metrics_server_absent.txt"
fi

# 2) Número de pods core prontos (AMF/SMF/UPF/PCF/NRF)
# Fonte: K8s API
kubectl get pods -n "${CORE_NS}" -o wide | tee "${EVID}/obs/core_pods_wide.txt"
READY_COUNT="$(kubectl get pods -n "${CORE_NS}" --no-headers | awk '{print $2}' | awk -F/ '$1==$2{c++} END{print c+0}')"
echo "core_pods_ready=${READY_COUNT}" | tee "${EVID}/obs/core_pods_ready.txt"

# 3) Throughput do UPF (TX/RX) – se Prometheus tiver, ótimo; senão, proxy via node interface (guardrail mínimo)
# Aqui não inventamos métrica: guardamos evidências do que existe.
echo "Tentando identificar node do UPF para coleta de interface..."
UPF_NODE="$(kubectl get pod -n "${CORE_NS}" "${UPF_POD}" -o jsonpath='{.spec.nodeName}')"
echo "upf_node=${UPF_NODE}" | tee "${EVID}/obs/upf_node.txt"

# Capturar cAdvisor/Node metrics via K8s não é trivial sem endpoint; então registramos como TODO se Prometheus não estiver integrado.
echo "⚠️ INFO: throughput requer Prometheus/Node exporter ou coleta direta no nó (fora do kubectl). Sem fonte -> não calcular." | tee "${EVID}/obs/throughput_note.txt"

# 4) Falhas de sessão (logs SMF)
SMF_POD="$(kubectl get pods -n "${CORE_NS}" --no-headers | awk '{print $1}' | grep -i smf | head -n 1 || true)"
if [ -n "${SMF_POD}" ]; then
  echo "Fonte: logs SMF (contagem de Establishment Reject/Fail)"
  kubectl logs -n "${CORE_NS}" "${SMF_POD}" --since=30m > "${EVID}/obs/smf_logs_30m.txt" || true
  # Contagem simples, auditável (string match)
  FAILS="$(grep -Eci 'reject|fail|establishment' "${EVID}/obs/smf_logs_30m.txt" || true)"
  echo "core_session_fail_mentions_30m=${FAILS}" | tee "${EVID}/obs/core_session_fail_proxy.txt"
else
  echo "⚠️ WARN: SMF pod não encontrado; registrando ausência."
  echo "SMF ausente" > "${EVID}/obs/smf_absent.txt"
fi

echo "==== RAN (proxy mínimo auditável) ===="

kubectl get pods -n "${UERANSIM_NS}" -o wide | tee "${EVID}/obs/ran_pods_wide.txt"
RAN_READY="$(kubectl get pods -n "${UERANSIM_NS}" --no-headers 2>/dev/null | awk '{print $2}' | awk -F/ '$1==$2{c++} END{print c+0}')"
echo "ran_pods_ready=${RAN_READY}" | tee "${EVID}/obs/ran_pods_ready.txt"

# UE active count proxy via logs do ueransim (Registered + PDU Established)
UE_POD="$(kubectl get pods -n "${UERANSIM_NS}" --no-headers 2>/dev/null | awk '{print $1}' | grep -i ue | head -n 1 || true)"
if [ -n "${UE_POD}" ]; then
  kubectl logs -n "${UERANSIM_NS}" "${UE_POD}" --since=30m > "${EVID}/obs/ue_logs_30m.txt" || true
  REG="$(grep -ci 'Registered' "${EVID}/obs/ue_logs_30m.txt" || true)"
  PDU="$(grep -Eci 'PDU.*(Established|Session)' "${EVID}/obs/ue_logs_30m.txt" || true)"
  echo "ran_ue_registered_mentions_30m=${REG}" | tee "${EVID}/obs/ran_ue_registered_proxy.txt"
  echo "ran_pdu_established_mentions_30m=${PDU}" | tee "${EVID}/obs/ran_pdu_proxy.txt"
else
  echo "⚠️ WARN: UE pod não encontrado; registrando ausência."
  echo "UE ausente" > "${EVID}/obs/ue_absent.txt"
fi

echo "==== TRANSPORTE (guardrail simples) ===="

# RTT p95: se não houver blackbox exporter, usar ping controlado de um pod no ueransim para o serviço do UPF (ou endpoint conhecido)
# Sem inventar: registramos a execução e o output bruto.
TARGET="${TARGET_RTT:-trisla-besu.trisla.svc.cluster.local}" # ajuste para um endpoint crítico se tiver melhor SSOT
PING_POD="ping-${RANDOM}"
kubectl run -n "${UERANSIM_NS}" "${PING_POD}" --restart=Never --image=busybox:1.36 -- \
  sh -c "ping -c 50 ${TARGET} || true" > "${EVID}/obs/ping_output.txt" 2>&1 || true
kubectl delete pod -n "${UERANSIM_NS}" "${PING_POD}" --ignore-not-found >/dev/null 2>&1 || true

echo "⚠️ INFO: RTT p95 exige parsing do ping; guardamos output bruto auditável." | tee "${EVID}/obs/rtt_note.txt"
echo "✅ Coleta mínima concluída. Evidências em ${EVID}/obs"
