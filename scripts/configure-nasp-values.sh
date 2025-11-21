#!/bin/bash
# ============================================
# Script para Configurar Valores Reais do NASP
# ============================================
# Usa valores conhecidos e permite preencher endpoints
# ============================================

set -e

# Valores conhecidos do NASP
INTERFACE="my5g"
NODE_IP="192.168.10.16"
GATEWAY="192.168.10.1"
NODE1_IP="${NODE1_IP:-$NODE_IP}"
NODE2_IP="${NODE2_IP:-}"

echo "🔧 Configurando valores reais do NASP..."
echo ""

# 1. Atualizar helm/trisla/values-production.yaml
echo "1️⃣ Atualizando helm/trisla/values-production.yaml..."

# Criar backup
cp helm/trisla/values-production.yaml helm/trisla/values-production.yaml.bak 2>/dev/null || true

# Atualizar valores conhecidos
cat > helm/trisla/values-production.yaml <<EOF
# ============================================
# Values para PRODUÇÃO REAL
# ============================================
# ⚠️ IMPORTANTE: Configurado com valores reais do NASP
# ============================================

# Network Configuration (valores reais)
network:
  interface: "$INTERFACE"
  nodeIP: "$NODE_IP"
  gateway: "$GATEWAY"

# Configurações de PRODUÇÃO REAL
production:
  enabled: true
  simulationMode: false  # ⚠️ NÃO usar simulação
  useRealServices: true  # ⚠️ Usar serviços REAIS
  executeRealActions: true  # ⚠️ Executar ações REAIS

# Endpoints REAIS do NASP
# ⚠️ IMPORTANTE: Preencher com endpoints reais dos controladores
naspAdapter:
  naspEndpoints:
    ran: "\${RAN_ENDPOINT:-http://ran-controller.nasp:8080}"  # ⚠️ AJUSTAR
    transport: "\${TRANSPORT_ENDPOINT:-http://transport-controller.nasp:8080}"  # ⚠️ AJUSTAR
    core: "\${CORE_ENDPOINT:-http://core-controller.nasp:8080}"  # ⚠️ AJUSTAR
  authentication:
    enabled: true
    type: "oauth2"  # Autenticação REAL

# Recursos aumentados para produção
semCsmf:
  replicas: 3
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi

mlNsmf:
  replicas: 3
  resources:
    requests:
      cpu: 2000m
      memory: 2Gi
    limits:
      cpu: 8000m
      memory: 8Gi

decisionEngine:
  replicas: 2
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi

bcNssmf:
  replicas: 2
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi

slaAgentLayer:
  replicas: 3
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi

naspAdapter:
  replicas: 2
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi

# Monitoramento ativo
monitoring:
  enabled: true
  alerting:
    enabled: true
EOF

echo "✅ values-production.yaml atualizado"
echo ""

# 2. Atualizar ansible/inventory.ini
echo "2️⃣ Atualizando ansible/inventory.ini..."

cat > ansible/inventory.ini <<EOF
# ============================================
# Inventory Ansible - TriSLA NASP
# ============================================
# ⚠️ IMPORTANTE: Configurado com valores reais do NASP
# ============================================

[nasp_nodes]
node1 ansible_host=$NODE1_IP iface=$INTERFACE
EOF

if [ -n "$NODE2_IP" ]; then
    echo "node2 ansible_host=$NODE2_IP iface=$INTERFACE" >> ansible/inventory.ini
fi

cat >> ansible/inventory.ini <<EOF

[control_plane]
node1
EOF

if [ -n "$NODE2_IP" ]; then
    echo "node2" >> ansible/inventory.ini
fi

cat >> ansible/inventory.ini <<EOF

[workers]
# Adicionar workers aqui se necessário

[kubernetes:children]
nasp_nodes

# ============================================
# Variáveis Globais
# ============================================
[all:vars]
ansible_user=root
ansible_ssh_common_args='-o StrictHostKeyChecking=no'

# Configurações de rede NASP (valores reais)
trisla_interface=$INTERFACE
trisla_node_ip=$NODE_IP
trisla_gateway=$GATEWAY

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

# 3. Atualizar apps/nasp-adapter/src/nasp_client.py
echo "3️⃣ Atualizando apps/nasp-adapter/src/nasp_client.py..."

# Criar backup
cp apps/nasp-adapter/src/nasp_client.py apps/nasp-adapter/src/nasp_client.py.bak 2>/dev/null || true

# Atualizar com valores reais (mantendo placeholders para endpoints)
sed -i.bak2 "s|ran-controller.nasp:8080|ran-controller.nasp:8080|g" apps/nasp-adapter/src/nasp_client.py 2>/dev/null || \
sed -i '' "s|ran-controller.nasp:8080|ran-controller.nasp:8080|g" apps/nasp-adapter/src/nasp_client.py 2>/dev/null || true

echo "✅ nasp_client.py mantido (endpoints precisam ser configurados manualmente)"
echo ""

# 4. Gerar resumo
echo "=========================================="
echo "✅ Configuração concluída!"
echo ""
echo "📋 Valores configurados:"
echo "   Interface: $INTERFACE"
echo "   Node IP: $NODE_IP"
echo "   Gateway: $GATEWAY"
echo "   Node1 IP: $NODE1_IP"
if [ -n "$NODE2_IP" ]; then
    echo "   Node2 IP: $NODE2_IP"
fi
echo ""
echo "⚠️  AÇÕES NECESSÁRIAS:"
echo "   1. Executar no NASP: ./scripts/discover-nasp-endpoints.sh"
echo "   2. Preencher endpoints reais em helm/trisla/values-production.yaml:"
echo "      - RAN controller endpoint"
echo "      - Transport controller endpoint"
echo "      - Core controller endpoint"
echo "   3. Atualizar apps/nasp-adapter/src/nasp_client.py com endpoints reais"
echo ""
echo "📝 Comandos úteis no NASP:"
echo "   kubectl get svc -A | grep -i ran"
echo "   kubectl get svc -A | grep -i transport"
echo "   kubectl get svc -A | grep -i core"
echo ""

