#!/bin/bash
# ============================================
# Script para Descobrir Endpoints do NASP
# ============================================
# Executar no NASP (node1) para descobrir endpoints reais
# ============================================

set -e

echo "🔍 Descobrindo endpoints do NASP..."
echo ""

# Valores conhecidos
NODE_IP="192.168.10.16"
INTERFACE="my5g"
GATEWAY="192.168.10.1"

echo "Valores conhecidos:"
echo "  Node IP: $NODE_IP"
echo "  Interface: $INTERFACE"
echo "  Gateway: $GATEWAY"
echo ""

# 1. Descobrir IPs dos nodes
echo "1️⃣ Descobrindo IPs dos nodes do cluster..."
if command -v kubectl &> /dev/null; then
    echo "Nodes do cluster:"
    kubectl get nodes -o wide
    echo ""
    
    NODE1_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' 2>/dev/null || echo "$NODE_IP")
    NODE2_IP=$(kubectl get nodes -o jsonpath='{.items[1].status.addresses[?(@.type=="InternalIP")].address}' 2>/dev/null || echo "")
    
    echo "  Node1 IP: $NODE1_IP"
    echo "  Node2 IP: $NODE2_IP"
else
    echo "⚠️  kubectl não encontrado. Usando valores padrão."
    NODE1_IP="$NODE_IP"
    NODE2_IP=""
fi
echo ""

# 2. Descobrir serviços NASP (RAN, Transport, Core)
echo "2️⃣ Descobrindo serviços NASP..."
echo "   Verificando namespaces do NASP..."

# Verificar namespaces do NASP
if command -v kubectl &> /dev/null; then
    NASP_NAMESPACES=$(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}' | grep -iE 'ran|transport|core|nasp' || echo "")
    
    if [ -n "$NASP_NAMESPACES" ]; then
        echo "   Namespaces encontrados: $NASP_NAMESPACES"
        
        # Procurar serviços RAN
        echo ""
        echo "   Procurando controladores RAN..."
        RAN_SERVICES=$(kubectl get svc -A -o jsonpath='{.items[?(@.metadata.name=~".*ran.*")].metadata.name}' 2>/dev/null || echo "")
        if [ -n "$RAN_SERVICES" ]; then
            echo "   Serviços RAN encontrados: $RAN_SERVICES"
            for svc in $RAN_SERVICES; do
                NS=$(kubectl get svc -A -o jsonpath="{.items[?(@.metadata.name==\"$svc\")].metadata.namespace}")
                IP=$(kubectl get svc -n "$NS" "$svc" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
                PORT=$(kubectl get svc -n "$NS" "$svc" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "8080")
                echo "     - $svc ($NS): http://$IP:$PORT"
            done
        fi
        
        # Procurar serviços Transport
        echo ""
        echo "   Procurando controladores Transport..."
        TRANSPORT_SERVICES=$(kubectl get svc -A -o jsonpath='{.items[?(@.metadata.name=~".*transport.*")].metadata.name}' 2>/dev/null || echo "")
        if [ -n "$TRANSPORT_SERVICES" ]; then
            echo "   Serviços Transport encontrados: $TRANSPORT_SERVICES"
            for svc in $TRANSPORT_SERVICES; do
                NS=$(kubectl get svc -A -o jsonpath="{.items[?(@.metadata.name==\"$svc\")].metadata.namespace}")
                IP=$(kubectl get svc -n "$NS" "$svc" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
                PORT=$(kubectl get svc -n "$NS" "$svc" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "8080")
                echo "     - $svc ($NS): http://$IP:$PORT"
            done
        fi
        
        # Procurar serviços Core
        echo ""
        echo "   Procurando controladores Core..."
        CORE_SERVICES=$(kubectl get svc -A -o jsonpath='{.items[?(@.metadata.name=~".*core.*")].metadata.name}' 2>/dev/null || echo "")
        if [ -n "$CORE_SERVICES" ]; then
            echo "   Serviços Core encontrados: $CORE_SERVICES"
            for svc in $CORE_SERVICES; do
                NS=$(kubectl get svc -A -o jsonpath="{.items[?(@.metadata.name==\"$svc\")].metadata.namespace}")
                IP=$(kubectl get svc -n "$NS" "$svc" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
                PORT=$(kubectl get svc -n "$NS" "$svc" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "8080")
                echo "     - $svc ($NS): http://$IP:$PORT"
            done
        fi
    else
        echo "   ⚠️  Nenhum namespace do NASP encontrado"
    fi
else
    echo "   ⚠️  kubectl não encontrado"
fi
echo ""

# 3. Verificar variáveis de ambiente ou configs
echo "3️⃣ Verificando configurações existentes..."
if [ -f "/etc/nasp/config" ] || [ -f "$HOME/.nasp/config" ]; then
    echo "   Arquivo de configuração encontrado"
    cat /etc/nasp/config 2>/dev/null || cat "$HOME/.nasp/config" 2>/dev/null || echo "   (vazio)"
fi
echo ""

# 4. Verificar processos/listening ports
echo "4️⃣ Verificando processos e portas..."
if command -v netstat &> /dev/null; then
    echo "   Portas em listening (8080, 8081, 8082, etc.):"
    netstat -tlnp 2>/dev/null | grep -E ':(8080|8081|8082|8083|8084|8085)' || echo "   Nenhuma porta encontrada"
elif command -v ss &> /dev/null; then
    echo "   Portas em listening:"
    ss -tlnp 2>/dev/null | grep -E ':(8080|8081|8082|8083|8084|8085)' || echo "   Nenhuma porta encontrada"
fi
echo ""

# 5. Gerar arquivo de configuração
echo "5️⃣ Gerando arquivo de configuração..."
cat > /tmp/nasp-endpoints-discovered.yaml <<EOF
# ============================================
# Endpoints NASP Descobertos
# ============================================
# Gerado automaticamente por discover-nasp-endpoints.sh
# Data: $(date)
# ============================================

network:
  interface: "$INTERFACE"
  nodeIP: "$NODE_IP"
  gateway: "$GATEWAY"

nodes:
  node1:
    ip: "$NODE1_IP"
    interface: "$INTERFACE"
  node2:
    ip: "$NODE2_IP"
    interface: "$INTERFACE"

# ⚠️ IMPORTANTE: Preencher manualmente os endpoints abaixo
# com base na descoberta acima ou informações do administrador NASP

naspControllers:
  ran:
    # Preencher com endpoint real do controlador RAN
    endpoint: "http://ran-controller.nasp:8080"  # ⚠️ AJUSTAR
    namespace: "nasp-ran"  # ⚠️ AJUSTAR
    service: "ran-controller"  # ⚠️ AJUSTAR
  
  transport:
    # Preencher com endpoint real do controlador Transport
    endpoint: "http://transport-controller.nasp:8080"  # ⚠️ AJUSTAR
    namespace: "nasp-transport"  # ⚠️ AJUSTAR
    service: "transport-controller"  # ⚠️ AJUSTAR
  
  core:
    # Preencher com endpoint real do controlador Core
    endpoint: "http://core-controller.nasp:8080"  # ⚠️ AJUSTAR
    namespace: "nasp-core"  # ⚠️ AJUSTAR
    service: "core-controller"  # ⚠️ AJUSTAR

# Comandos úteis para descobrir endpoints:
# kubectl get svc -A | grep -i ran
# kubectl get svc -A | grep -i transport
# kubectl get svc -A | grep -i core
EOF

echo "✅ Arquivo gerado: /tmp/nasp-endpoints-discovered.yaml"
echo ""
echo "📋 Próximos passos:"
echo "   1. Revisar /tmp/nasp-endpoints-discovered.yaml"
echo "   2. Preencher endpoints reais dos controladores"
echo "   3. Usar os valores para configurar helm/trisla/values-nasp.yaml"
echo ""

