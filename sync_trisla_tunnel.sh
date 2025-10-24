#!/bin/bash
# Tunnel SSH persistente TriSLA@NASP
# Redireciona localhost:8000 -> node1:3001 via gateway PPGCA

REMOTE_USER="porvir5g"
GATEWAY="ppgca.unisinos.br"
TARGET_NODE="192.168.10.16"
LOCAL_PORT=8000
REMOTE_PORT=3001

echo "🚀 Iniciando túnel SSH: localhost:${LOCAL_PORT} → ${TARGET_NODE}:${REMOTE_PORT} (via ${GATEWAY})"
autossh -M 0 -f -N -L ${LOCAL_PORT}:${TARGET_NODE}:${REMOTE_PORT} ${REMOTE_USER}@${GATEWAY}
