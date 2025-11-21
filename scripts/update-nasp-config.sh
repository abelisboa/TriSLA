#!/bin/bash
# ============================================
# Script para Atualizar Configurações com Valores Descobertos
# ============================================
# Atualiza arquivos com valores descobertos no NASP
# ============================================

set -e

# Valores descobertos
NODE1_IP="192.168.10.16"
NODE2_IP="192.168.10.15"
INTERFACE="my5g"
GATEWAY="192.168.10.1"

echo "🔧 Atualizando configurações com valores descobertos..."
echo ""

# 1. Atualizar ansible/inventory.ini
echo "1️⃣ Atualizando ansible/inventory.ini..."
cat > ansible/inventory.ini <<EOF
# ============================================
# Inventory Ansible - TriSLA NASP
# ============================================
# ⚠️ IMPORTANTE: Configurado com valores reais do NASP
# Valores descobertos automaticamente
# ============================================

[nasp_nodes]
node1 ansible_host=node006 ansible_ssh_common_args='-o ProxyJump=porvir5g@ppgca.unisinos.br' iface=$INTERFACE
node2 ansible_host=$NODE2_IP ansible_ssh_common_args='-o ProxyJump=porvir5g@ppgca.unisinos.br' iface=$INTERFACE

[control_plane]
node1
node2

[workers]
# Adicionar workers aqui se necessário

[kubernetes:children]
nasp_nodes

# ============================================
# Variáveis Globais
# ============================================
[all:vars]
ansible_user=porvir5g
ansible_ssh_common_args='-o ProxyJump=porvir5g@ppgca.unisinos.br'

# Configurações de rede NASP (valores reais descobertos)
trisla_interface=$INTERFACE
trisla_node_ip=$NODE1_IP
trisla_gateway=$GATEWAY
trisla_node1_ip=$NODE1_IP
trisla_node2_ip=$NODE2_IP

# Configurações do Kubernetes
kubeconfig_path=/etc/kubernetes/admin.conf

# Configurações do TriSLA
trisla_namespace=trisla
trisla_image_registry=ghcr.io/abelisboa

# Configurações de deploy
trisla_deploy_method=helm
trisla_helm_chart_path=./helm/trisla

# Configurações de observabilidade
trisla_observability_enabled=true
trisla_prometheus_enabled=true
trisla_grafana_enabled=true

# Configurações de produção REAL
trisla_production_mode=true
trisla_simulation_mode=false
EOF

echo "✅ inventory.ini atualizado"
echo ""

# 2. Atualizar helm/trisla/values-production.yaml (valores conhecidos)
echo "2️⃣ Atualizando helm/trisla/values-production.yaml..."
# Manter valores conhecidos e adicionar node2
cat >> helm/trisla/values-production.yaml <<EOF

# Node IPs descobertos
nodes:
  node1:
    ip: $NODE1_IP
    interface: $INTERFACE
  node2:
    ip: $NODE2_IP
    interface: $INTERFACE
EOF

echo "✅ values-production.yaml atualizado com IPs dos nodes"
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
echo "   1. No NASP, executar: ./scripts/discover-nasp-services.sh"
echo "   2. Identificar endpoints dos controladores (RAN, Transport, Core)"
echo "   3. Atualizar helm/trisla/values-production.yaml com endpoints"
echo "   4. Atualizar apps/nasp-adapter/src/nasp_client.py com endpoints"
echo ""

