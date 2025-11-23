#!/bin/bash
# ============================================
# Script para Atualizar Configurações com Valores Descobertos
# ============================================
# Atualiza arquivos com valores descobertos no NASP (local)
# ============================================

set -e

# Valores descobertos
NODE1_IP="192.168.10.16"
NODE2_IP="192.168.10.15"
INTERFACE="my5g"
GATEWAY="192.168.10.1"

echo "🔧 Atualizando configurações com valores descobertos..."
echo ""

# 1. Atualizar ansible/inventory.yaml
echo "1️⃣ Atualizando ansible/inventory.yaml..."
cat > ansible/inventory.yaml <<EOF
# ============================================
# Inventory Ansible YAML - TriSLA NASP
# ============================================
# Inventário para deploy local 127.0.0.1
# ============================================

[nasp]
127.0.0.1 ansible_connection=local ansible_python_interpreter=/usr/bin/python3
EOF

echo "✅ inventory.yaml atualizado"
echo ""

# 2. Atualizar helm/trisla/values-nasp.yaml (valores conhecidos)
echo "2️⃣ Atualizando helm/trisla/values-nasp.yaml..."
# Manter valores conhecidos e adicionar node2
cat >> helm/trisla/values-nasp.yaml <<EOF

# Node IPs descobertos
nodes:
  node1:
    ip: $NODE1_IP
    interface: $INTERFACE
  node2:
    ip: $NODE2_IP
    interface: $INTERFACE
EOF

echo "✅ values-nasp.yaml atualizado com IPs dos nodes"
echo ""

echo "=========================================="
echo "✅ Configurações atualizadas!"
echo ""
echo "📋 Valores configurados:"
echo "   Node1 IP: $NODE1_IP"
echo "   Node2 IP: $NODE2_IP"
echo "   Interface: $INTERFACE"
echo "   Gateway: $GATEWAY"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "   1. Executar: ./scripts/discover-nasp-services.sh"
echo "   2. Identificar endpoints dos controladores (RAN, Transport, Core)"
echo "   3. Atualizar helm/trisla/values-nasp.yaml com endpoints"
echo "   4. Atualizar apps/nasp-adapter/src/nasp_client.py com endpoints"
echo ""
