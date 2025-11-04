#!/bin/bash
set -e
JUMP_USER=${JUMP_USER:-porvir5g}
JUMP_HOST=${JUMP_HOST:-ppgca.unisinos.br}
NODE_USER=${NODE_USER:-porvir5g}
NODE_HOST=${NODE_HOST:-node006}
LOCAL_PORT=${LOCAL_PORT:-9090}
REMOTE_PORT=${REMOTE_PORT:-9090}
echo "🚇 Criando túnel: localhost:${LOCAL_PORT} → ${JUMP_HOST} → ${NODE_HOST}:localhost:${REMOTE_PORT}"
if lsof -i:${LOCAL_PORT} >/dev/null 2>&1; then echo "⚠️  Porta local ${LOCAL_PORT} já em uso. Encerrando antiga sessão..."; fuser -k ${LOCAL_PORT}/tcp || true; sleep 1; fi
ssh -N -L ${LOCAL_PORT}:localhost:${REMOTE_PORT} -J ${JUMP_USER}@${JUMP_HOST} ${NODE_USER}@${NODE_HOST} &
PID=$!; sleep 2; echo "✅ Túnel PID: ${PID}"
echo "🔍 Verificando Prometheus em http://localhost:${LOCAL_PORT}/-/ready ..."
set +e; curl -sf "http://localhost:${LOCAL_PORT}/-/ready" >/dev/null; RC=$?; set -e
if [ $RC -ne 0 ]; then echo "⚠️  Prometheus não respondeu. Rode no node:"; echo "    kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090"; else echo "🟢 Prometheus OK."; fi
echo "🔗 Para encerrar: kill ${PID}"; wait ${PID}
