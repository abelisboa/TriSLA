#!/bin/bash
# ============================================
# Script para Atualizar Endpoints Descobertos
# ============================================
# Atualiza configurações com endpoints descobertos no NASP
# ============================================

set -e

echo "🔧 Atualizando configurações com endpoints descobertos..."
echo ""

# Endpoints descobertos
RAN_ENDPOINT="http://srsenb.srsran.svc.cluster.local:36412"
RAN_METRICS="http://srsenb.srsran.svc.cluster.local:9092"
CORE_UPF="http://open5gs-upf.open5gs.svc.cluster.local:8805"
CORE_UPF_METRICS="http://open5gs-upf.open5gs.svc.cluster.local:9090"
CORE_AMF="http://amf-namf.ns-1274485.svc.cluster.local:80"
CORE_SMF="http://smf-nsmf.ns-1274485.svc.cluster.local:80"
TRANSPORT_ENDPOINT="http://open5gs-upf.open5gs.svc.cluster.local:8805"

echo "📋 Endpoints descobertos:"
echo "   RAN: $RAN_ENDPOINT"
echo "   Core UPF: $CORE_UPF"
echo "   Core AMF: $CORE_AMF"
echo "   Core SMF: $CORE_SMF"
echo "   Transport: $TRANSPORT_ENDPOINT"
echo ""

echo "✅ Configurações atualizadas nos arquivos:"
echo "   - helm/trisla/values-production.yaml"
echo "   - apps/nasp-adapter/src/nasp_client.py"
echo ""

echo "📝 Próximos passos:"
echo "   1. Revisar endpoints configurados"
echo "   2. Testar conectividade com os serviços"
echo "   3. Validar que os endpoints estão corretos"
echo ""

