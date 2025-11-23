#!/usr/bin/env bash
# ============================================
# Script Interativo para Preencher values-production.yaml ou values-nasp.yaml
# ============================================
# Para NASP: preenche helm/trisla/values-nasp.yaml
# Para produção genérica: preenche helm/trisla/values-production.yaml
# de forma guiada e segura
# ============================================
# Uso: ./scripts/fill_values_production.sh
# ============================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# Determinar qual arquivo usar baseado no ambiente
# Para NASP, usar values-nasp.yaml; para produção genérica, usar values-production.yaml
if [ "${TRISLA_ENV:-}" = "nasp" ] || [ -n "${NASP_DEPLOY:-}" ]; then
    VALUES_FILE="$PROJECT_ROOT/helm/trisla/values-nasp.yaml"
    VALUES_TYPE="NASP"
else
    VALUES_FILE="$PROJECT_ROOT/helm/trisla/values-production.yaml"
    VALUES_TYPE="Produção Genérica"
fi
VALUES_BACKUP="$VALUES_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}📝 Preenchimento Guiado de $VALUES_FILE (${VALUES_TYPE})${NC}"
echo -e "${BLUE}============================================================${NC}\n"

# Verificar se yq está disponível
YQ_AVAILABLE=false
if command -v yq &> /dev/null; then
    YQ_AVAILABLE=true
elif command -v python3 &> /dev/null; then
    # Tentar usar yq via pip
    if python3 -c "import yq" 2>/dev/null; then
        YQ_AVAILABLE=true
    else
        echo -e "${YELLOW}⚠️ yq não encontrado. Usando método alternativo (sed).${NC}"
        echo -e "${YELLOW}   Para melhor experiência, instale yq: pip install yq${NC}"
    fi
fi

# Fazer backup do arquivo original
if [ -f "$VALUES_FILE" ]; then
    cp "$VALUES_FILE" "$VALUES_BACKUP"
    echo -e "${GREEN}✅ Backup criado: $VALUES_BACKUP${NC}\n"
else
    echo -e "${YELLOW}⚠️ Arquivo $VALUES_FILE não encontrado. Criando novo...${NC}\n"
    # Para NASP, tentar copiar de template; caso contrário, copiar de values.yaml
    if [ "$VALUES_TYPE" = "NASP" ] && [ -f "$PROJECT_ROOT/docs/nasp/values-nasp.yaml" ]; then
        cp "$PROJECT_ROOT/docs/nasp/values-nasp.yaml" "$VALUES_FILE"
        echo -e "${GREEN}✅ Arquivo criado a partir do template docs/nasp/values-nasp.yaml${NC}\n"
    elif [ -f "$PROJECT_ROOT/helm/trisla/values.yaml" ]; then
        cp "$PROJECT_ROOT/helm/trisla/values.yaml" "$VALUES_FILE"
        echo -e "${GREEN}✅ Arquivo criado a partir de values.yaml${NC}\n"
    fi
fi

# Função para ler valor com default
read_value() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        echo -e "${BLUE}$prompt${NC} [padrão: ${YELLOW}$default${NC}]: "
    else
        echo -e "${BLUE}$prompt${NC}: "
    fi
    
    read -r value
    if [ -z "$value" ] && [ -n "$default" ]; then
        value="$default"
    fi
    eval "$var_name='$value'"
}

# Função para atualizar YAML
update_yaml() {
    local path="$1"
    local value="$2"
    
    if [ "$YQ_AVAILABLE" = true ]; then
        if command -v yq &> /dev/null; then
            yq eval "$path = \"$value\"" -i "$VALUES_FILE" 2>/dev/null || {
                echo -e "${YELLOW}⚠️ Erro ao usar yq, usando método alternativo${NC}"
                update_yaml_sed "$path" "$value"
            }
        elif command -v python3 &> /dev/null; then
            python3 -c "
import yaml
import sys
with open('$VALUES_FILE', 'r') as f:
    data = yaml.safe_load(f)
# Atualizar caminho aninhado (implementação simplificada)
# Por enquanto, usar sed como fallback
" 2>/dev/null || update_yaml_sed "$path" "$value"
        else
            update_yaml_sed "$path" "$value"
        fi
    else
        update_yaml_sed "$path" "$value"
    fi
}

# Função fallback usando sed
update_yaml_sed() {
    local path="$1"
    local value="$2"
    # Converter path YAML para padrão sed (ex: global.namespace -> global: namespace)
    local sed_path=$(echo "$path" | sed 's/\./:/g')
    # Tentar atualizar (pode não funcionar para todos os casos)
    if grep -q "^[[:space:]]*${path}:" "$VALUES_FILE" 2>/dev/null; then
        sed -i.bak "s|^[[:space:]]*${path}:.*|${path}: \"${value}\"|" "$VALUES_FILE"
    else
        echo -e "${YELLOW}⚠️ Caminho ${path} não encontrado. Adicione manualmente ao arquivo.${NC}"
    fi
}

echo -e "${BLUE}1️⃣ Configurações Básicas${NC}\n"

# Namespace
read_value "Namespace do TriSLA" "trisla" TRISLA_NAMESPACE
update_yaml "global.namespace" "$TRISLA_NAMESPACE"

# Registry
read_value "Registry de imagens (ex: ghcr.io/abelisboa)" "ghcr.io/abelisboa" IMAGE_REGISTRY
update_yaml "global.imageRegistry" "$IMAGE_REGISTRY"

echo ""
echo -e "${BLUE}2️⃣ Configurações de Rede${NC}\n"

# Interface
read_value "Interface de rede NASP (ex: my5g)" "my5g" NETWORK_INTERFACE
update_yaml "network.interface" "$NETWORK_INTERFACE"

# Node IP (genérico)
read_value "IP do Node1 (use placeholder se não souber)" "<NODE1_IP>" NODE1_IP
update_yaml "nodes.node1.ip" "$NODE1_IP"

read_value "IP do Node2 (use placeholder se não souber)" "<NODE2_IP>" NODE2_IP
update_yaml "nodes.node2.ip" "$NODE2_IP"

# Gateway
read_value "Gateway IP (use placeholder se não souber)" "<GATEWAY_IP>" GATEWAY_IP
update_yaml "network.gateway" "$GATEWAY_IP"

echo ""
echo -e "${BLUE}3️⃣ Endpoints NASP${NC}\n"
echo -e "${YELLOW}💡 Dica: Execute scripts/discover_nasp_endpoints.sh primeiro para descobrir endpoints${NC}\n"

# RAN
read_value "Endpoint RAN (formato: http://<SERVICE>.<NS>.svc.cluster.local:<PORT>)" "http://<RAN_SERVICE>.<RAN_NAMESPACE>.svc.cluster.local:<RAN_PORT>" RAN_ENDPOINT
update_yaml "naspAdapter.naspEndpoints.ran" "$RAN_ENDPOINT"

read_value "Endpoint RAN Metrics" "http://<RAN_SERVICE>.<RAN_NAMESPACE>.svc.cluster.local:<RAN_METRICS_PORT>" RAN_METRICS
update_yaml "naspAdapter.naspEndpoints.ran_metrics" "$RAN_METRICS"

# Core
read_value "Endpoint Core UPF" "http://<UPF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<UPF_PORT>" CORE_UPF
update_yaml "naspAdapter.naspEndpoints.core_upf" "$CORE_UPF"

read_value "Endpoint Core UPF Metrics" "http://<UPF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<UPF_METRICS_PORT>" CORE_UPF_METRICS
update_yaml "naspAdapter.naspEndpoints.core_upf_metrics" "$CORE_UPF_METRICS"

read_value "Endpoint Core AMF" "http://<AMF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<AMF_PORT>" CORE_AMF
update_yaml "naspAdapter.naspEndpoints.core_amf" "$CORE_AMF"

read_value "Endpoint Core SMF" "http://<SMF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<SMF_PORT>" CORE_SMF
update_yaml "naspAdapter.naspEndpoints.core_smf" "$CORE_SMF"

# Transport
read_value "Endpoint Transport" "http://<TRANSPORT_SERVICE>.<TRANSPORT_NAMESPACE>.svc.cluster.local:<TRANSPORT_PORT>" TRANSPORT_ENDPOINT
update_yaml "naspAdapter.naspEndpoints.transport" "$TRANSPORT_ENDPOINT"

echo ""
echo -e "${BLUE}4️⃣ Configurações de Blockchain${NC}\n"

# Besu RPC
read_value "URL RPC do Besu/GoQuorum" "http://<BESU_SERVICE>.<BESU_NAMESPACE>.svc.cluster.local:8545" BESU_RPC
update_yaml "bcNssmf.besu.rpcUrl" "$BESU_RPC"

read_value "Chain ID do Besu" "1337" BESU_CHAIN_ID
update_yaml "bcNssmf.besu.chainId" "$BESU_CHAIN_ID"

echo ""
echo -e "${BLUE}5️⃣ Configurações de Observabilidade${NC}\n"

# OTLP
read_value "Endpoint OTLP Collector" "http://<OTLP_SERVICE>.<OTLP_NAMESPACE>.svc.cluster.local:4317" OTLP_ENDPOINT
update_yaml "observability.otlp.endpoint" "$OTLP_ENDPOINT"

# Prometheus
read_value "Endpoint Prometheus" "http://<PROMETHEUS_SERVICE>.<MONITORING_NS>.svc.cluster.local:9090" PROMETHEUS_ENDPOINT
update_yaml "observability.prometheus.endpoint" "$PROMETHEUS_ENDPOINT"

echo ""
echo -e "${GREEN}✅ Preenchimento concluído!${NC}\n"

echo -e "${BLUE}📋 Próximos passos:${NC}"
echo "   1. Revisar o arquivo: $VALUES_FILE"
echo "   2. Validar com: helm template trisla ./helm/trisla -f $VALUES_FILE --debug"
echo "   3. Se necessário, restaurar backup: cp $VALUES_BACKUP $VALUES_FILE"
echo ""

