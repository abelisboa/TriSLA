#!/bin/bash
# ============================================
# 🚀 Auto-configuração do ambiente NASP para o TriSLA
# ============================================
# Este script identifica a interface principal, IP, gateway e gera templates
# prontos para o values.yaml, inventory Ansible e scripts do TriSLA.
# ============================================

set -e

echo "🔍 Coletando informações do NASP..."

# Informações reais do ambiente NASP
PRIMARY_IFACE="my5g"
PRIMARY_IP="192.168.10.16"
PRIMARY_GW="192.168.10.1"

# Validação básica
if [ -z "$PRIMARY_IFACE" ] || [ -z "$PRIMARY_IP" ] || [ -z "$PRIMARY_GW" ]; then
    echo "❌ ERRO: Informações de rede não configuradas!"
    exit 1
fi

echo "Interface física principal detectada: $PRIMARY_IFACE"
echo "IP utilizado pelo Kubernetes: $PRIMARY_IP"
echo "Gateway padrão: $PRIMARY_GW"

# Criar diretório de saída se não existir
mkdir -p configs/generated

# 🔧 Gerando trecho values.yaml
cat <<EOF > configs/generated/trisla_values_autogen.yaml
# ============================================
# Configurações de Rede Auto-geradas para TriSLA
# ============================================
# Gerado automaticamente por auto-config-nasp.sh
# Data: $(date)
# ============================================

network:
  interface: "$PRIMARY_IFACE"
  nodeIP: "$PRIMARY_IP"
  gateway: "$PRIMARY_GW"

service:
  type: ClusterIP

env:
  - name: TRISLA_NODE_INTERFACE
    value: "$PRIMARY_IFACE"
  - name: TRISLA_NODE_IP
    value: "$PRIMARY_IP"
  - name: TRISLA_GATEWAY
    value: "$PRIMARY_GW"
EOF

echo "✔ values.yaml gerado: configs/generated/trisla_values_autogen.yaml"

# 🔧 Gerando trecho de inventário Ansible
cat <<EOF > configs/generated/inventory_autogen.ini
# ============================================
# Inventory Ansible Auto-gerado para TriSLA
# ============================================
# Gerado automaticamente por auto-config-nasp.sh
# Data: $(date)
# ============================================
# ⚠️ IMPORTANTE: Substituir <INSERIR_IP_NODE1> e <INSERIR_IP_NODE2> pelos IPs reais

[nasp_nodes]
node1 ansible_host=<INSERIR_IP_NODE1> iface=$PRIMARY_IFACE
node2 ansible_host=<INSERIR_IP_NODE2> iface=$PRIMARY_IFACE

[control_plane]
node1
node2

[workers]
# Adicionar workers aqui se necessário
# node3 ansible_host=<INSERIR_IP_NODE3> iface=$PRIMARY_IFACE

[kubernetes:children]
nasp_nodes

[all:vars]
ansible_user=root
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
trisla_interface=$PRIMARY_IFACE
trisla_node_ip=$PRIMARY_IP
trisla_gateway=$PRIMARY_GW
EOF

echo "✔ Inventory gerado: configs/generated/inventory_autogen.ini"

# 🔧 Gerando script de integração TriSLA ↔ NASP
cat <<EOF > scripts/trisla_nasp_env.sh
#!/bin/bash
# ============================================
# Variáveis de Ambiente TriSLA ↔ NASP
# ============================================
# Gerado automaticamente por auto-config-nasp.sh
# Data: $(date)
# ============================================

export TRISLA_NODE_INTERFACE="$PRIMARY_IFACE"
export TRISLA_NODE_IP="$PRIMARY_IP"
export TRISLA_GATEWAY="$PRIMARY_GW"

# Exibir configuração
echo "TriSLA Environment Variables:"
echo "  TRISLA_NODE_INTERFACE=$TRISLA_NODE_INTERFACE"
echo "  TRISLA_NODE_IP=$TRISLA_NODE_IP"
echo "  TRISLA_GATEWAY=$TRISLA_GATEWAY"
EOF

chmod +x scripts/trisla_nasp_env.sh

echo "✔ Script trisla_nasp_env.sh gerado e pronto."

echo ""
echo "🎉 Auto-configuração concluída."
echo ""
echo "📋 Arquivos gerados:"
echo "  - configs/generated/trisla_values_autogen.yaml"
echo "  - configs/generated/inventory_autogen.ini"
echo "  - scripts/trisla_nasp_env.sh"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "  1. Editar inventory_autogen.ini e substituir <INSERIR_IP_NODE1> e <INSERIR_IP_NODE2>"
echo "  2. Revisar trisla_values_autogen.yaml"
echo "  3. Executar scripts de validação da infraestrutura"

