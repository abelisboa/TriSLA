#!/usr/bin/env bash
# ============================================
# Script de Descoberta de Endpoints NASP
# ============================================
# Coleta informações do cluster NASP sem expor IPs reais
# Gera relatório técnico em Markdown
# ============================================
# Uso: ./scripts/discover_nasp_endpoints.sh [--output-dir <dir>]
# ============================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$PROJECT_ROOT/tmp}"
REPORT_FILE="$OUTPUT_DIR/nasp_context_raw.txt"
REPORT_MD="$PROJECT_ROOT/docs/NASP_CONTEXT_REPORT.md"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🔍 Descoberta de Endpoints NASP - TriSLA${NC}"
echo -e "${BLUE}============================================================${NC}\n"

# Criar diretório de saída
mkdir -p "$OUTPUT_DIR"

# Verificar se kubectl está disponível
if ! command -v kubectl &> /dev/null; then
    echo -e "${YELLOW}⚠️ kubectl não encontrado. Este script deve ser executado no ambiente NASP.${NC}"
    exit 1
fi

# Verificar conectividade com cluster
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${YELLOW}⚠️ Não foi possível conectar ao cluster Kubernetes.${NC}"
    echo "   Verifique se kubectl está configurado corretamente."
    exit 1
fi

echo -e "${GREEN}✅ Conectado ao cluster Kubernetes${NC}\n"

# ============================================
# 1. Coletar informações do cluster
# ============================================

echo -e "${BLUE}1️⃣ Coletando informações do cluster...${NC}"

{
    echo "============================================"
    echo "RELATÓRIO DE CONTEXTO NASP - TriSLA"
    echo "Data: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    echo "============================================"
    echo ""
    
    # Informações gerais do cluster
    echo "=== INFORMAÇÕES DO CLUSTER ==="
    echo ""
    echo "Versão do Kubernetes:"
    kubectl version --short 2>/dev/null || echo "N/A"
    echo ""
    
    echo "Nodes do cluster:"
    kubectl get nodes -o custom-columns=NAME:.metadata.name,STATUS:.status.conditions[-1].type,VERSION:.status.nodeInfo.kubeletVersion --no-headers 2>/dev/null || echo "N/A"
    echo ""
    
    # CNI
    echo "CNI detectado:"
    if kubectl get pods -n kube-system -l k8s-app=calico-node &> /dev/null; then
        echo "Calico (detectado via pods kube-system)"
    elif kubectl get pods -n kube-system -l k8s-app=flannel &> /dev/null; then
        echo "Flannel (detectado via pods kube-system)"
    else
        echo "CNI não identificado automaticamente"
    fi
    echo ""
    
    # StorageClass
    echo "StorageClasses disponíveis:"
    kubectl get storageclass -o custom-columns=NAME:.metadata.name,PROVISIONER:.provisioner,DEFAULT:.metadata.annotations.storageclass\.kubernetes\.io/is-default-class --no-headers 2>/dev/null || echo "Nenhuma StorageClass encontrada"
    echo ""
    
    # Ingress
    echo "Ingress Classes disponíveis:"
    kubectl get ingressclass -o custom-columns=NAME:.metadata.name,CONTROLLER:.spec.controller --no-headers 2>/dev/null || echo "Nenhuma IngressClass encontrada"
    echo ""
    
} > "$REPORT_FILE"

# ============================================
# 2. Detectar serviços relevantes NASP
# ============================================

echo -e "${BLUE}2️⃣ Detectando serviços relevantes NASP...${NC}"

{
    echo "=== SERVIÇOS DETECTADOS ==="
    echo ""
    
    # Namespaces relevantes
    NAMESPACES=("monitoring" "nasp" "ran-test" "open5gs" "srsran" "nonrtric" "kube-system")
    
    for ns in "${NAMESPACES[@]}"; do
        if kubectl get namespace "$ns" &> /dev/null; then
            echo "📦 Namespace: $ns"
            
            # Serviços no namespace
            SERVICES=$(kubectl get svc -n "$ns" -o json 2>/dev/null || echo '{"items":[]}')
            
            # Prometheus
            if echo "$SERVICES" | jq -e '.items[] | select(.metadata.name | contains("prometheus"))' &> /dev/null; then
                PROM_SVC=$(echo "$SERVICES" | jq -r '.items[] | select(.metadata.name | contains("prometheus")) | .metadata.name' | head -1)
                PROM_PORT=$(echo "$SERVICES" | jq -r ".items[] | select(.metadata.name==\"$PROM_SVC\") | .spec.ports[0].port // \"N/A\"")
                PROM_TYPE=$(echo "$SERVICES" | jq -r ".items[] | select(.metadata.name==\"$PROM_SVC\") | .spec.type // \"N/A\"")
                echo "   ✅ Prometheus: $PROM_SVC ($PROM_TYPE, porta $PROM_PORT)"
            fi
            
            # Grafana
            if echo "$SERVICES" | jq -e '.items[] | select(.metadata.name | contains("grafana"))' &> /dev/null; then
                GRAF_SVC=$(echo "$SERVICES" | jq -r '.items[] | select(.metadata.name | contains("grafana")) | .metadata.name' | head -1)
                GRAF_PORT=$(echo "$SERVICES" | jq -r ".items[] | select(.metadata.name==\"$GRAF_SVC\") | .spec.ports[0].port // \"N/A\"")
                GRAF_TYPE=$(echo "$SERVICES" | jq -r ".items[] | select(.metadata.name==\"$GRAF_SVC\") | .spec.type // \"N/A\"")
                echo "   ✅ Grafana: $GRAF_SVC ($GRAF_TYPE, porta $GRAF_PORT)"
            fi
            
            # Loki
            if echo "$SERVICES" | jq -e '.items[] | select(.metadata.name | contains("loki"))' &> /dev/null; then
                LOKI_SVC=$(echo "$SERVICES" | jq -r '.items[] | select(.metadata.name | contains("loki")) | .metadata.name' | head -1)
                LOKI_PORT=$(echo "$SERVICES" | jq -r ".items[] | select(.metadata.name==\"$LOKI_SVC\") | .spec.ports[0].port // \"N/A\"")
                echo "   ✅ Loki: $LOKI_SVC (porta $LOKI_PORT)"
            fi
            
            # Kafka
            if echo "$SERVICES" | jq -e '.items[] | select(.metadata.name | contains("kafka"))' &> /dev/null; then
                KAFKA_SVC=$(echo "$SERVICES" | jq -r '.items[] | select(.metadata.name | contains("kafka")) | .metadata.name' | head -1)
                KAFKA_PORT=$(echo "$SERVICES" | jq -r ".items[] | select(.metadata.name==\"$KAFKA_SVC\") | .spec.ports[0].port // \"N/A\"")
                echo "   ✅ Kafka: $KAFKA_SVC (porta $KAFKA_PORT)"
            fi
            
            # NASP Adapter
            if echo "$SERVICES" | jq -e '.items[] | select(.metadata.name | contains("nasp") or contains("adapter"))' &> /dev/null; then
                NASP_SVC=$(echo "$SERVICES" | jq -r '.items[] | select(.metadata.name | contains("nasp") or contains("adapter")) | .metadata.name' | head -1)
                NASP_PORT=$(echo "$SERVICES" | jq -r ".items[] | select(.metadata.name==\"$NASP_SVC\") | .spec.ports[0].port // \"N/A\"")
                echo "   ✅ NASP Adapter: $NASP_SVC (porta $NASP_PORT)"
            fi
            
            # NWDAF
            if echo "$SERVICES" | jq -e '.items[] | select(.metadata.name | contains("nwdaf"))' &> /dev/null; then
                NWDAF_SVC=$(echo "$SERVICES" | jq -r '.items[] | select(.metadata.name | contains("nwdaf")) | .metadata.name' | head -1)
                NWDAF_PORT=$(echo "$SERVICES" | jq -r ".items[] | select(.metadata.name==\"$NWDAF_SVC\") | .spec.ports[0].port // \"N/A\"")
                echo "   ✅ NWDAF: $NWDAF_SVC (porta $NWDAF_PORT)"
            fi
            
            echo ""
        fi
    done
    
} >> "$REPORT_FILE"

# ============================================
# 3. Diagnóstico de saúde
# ============================================

echo -e "${BLUE}3️⃣ Realizando diagnóstico de saúde...${NC}"

{
    echo "=== DIAGNÓSTICO DE SAÚDE ==="
    echo ""
    
    # Pods em CrashLoopBackOff
    echo "Pods em CrashLoopBackOff:"
    CRASH_PODS=$(kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o json 2>/dev/null || echo '{"items":[]}')
    if echo "$CRASH_PODS" | jq -e '.items[] | select(.status.containerStatuses[]?.state.waiting.reason=="CrashLoopBackOff")' &> /dev/null; then
        echo "$CRASH_PODS" | jq -r '.items[] | select(.status.containerStatuses[]?.state.waiting.reason=="CrashLoopBackOff") | "   ⚠️ \(.metadata.namespace)/\(.metadata.name)"'
    else
        echo "   ✅ Nenhum pod em CrashLoopBackOff detectado"
    fi
    echo ""
    
    # Pods em ImagePullBackOff
    echo "Pods em ImagePullBackOff:"
    if echo "$CRASH_PODS" | jq -e '.items[] | select(.status.containerStatuses[]?.state.waiting.reason=="ImagePullBackOff")' &> /dev/null; then
        echo "$CRASH_PODS" | jq -r '.items[] | select(.status.containerStatuses[]?.state.waiting.reason=="ImagePullBackOff") | "   ⚠️ \(.metadata.namespace)/\(.metadata.name)"'
    else
        echo "   ✅ Nenhum pod em ImagePullBackOff detectado"
    fi
    echo ""
    
    # Pods não prontos
    echo "Pods não prontos (Ready != True):"
    NOT_READY=$(kubectl get pods -A -o json 2>/dev/null || echo '{"items":[]}')
    if echo "$NOT_READY" | jq -e '.items[] | select(.status.conditions[]? | select(.type=="Ready" and .status!="True"))' &> /dev/null; then
        echo "$NOT_READY" | jq -r '.items[] | select(.status.conditions[]? | select(.type=="Ready" and .status!="True")) | "   ⚠️ \(.metadata.namespace)/\(.metadata.name): \(.status.conditions[] | select(.type=="Ready") | .reason // "Unknown")"'
    else
        echo "   ✅ Todos os pods estão prontos"
    fi
    echo ""
    
} >> "$REPORT_FILE"

# ============================================
# 4. Gerar relatório Markdown
# ============================================

echo -e "${BLUE}4️⃣ Gerando relatório Markdown...${NC}"

# Chamar script Python para gerar relatório formatado (se existir)
if [ -f "$SCRIPT_DIR/generate_nasp_context_report.py" ]; then
    python3 "$SCRIPT_DIR/generate_nasp_context_report.py" "$REPORT_FILE" "$REPORT_MD"
else
    # Gerar relatório básico em Markdown
    {
        echo "# Relatório de Contexto NASP — TriSLA"
        echo ""
        echo "**Data:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
        echo "**Gerado por:** scripts/discover_nasp_endpoints.sh"
        echo ""
        echo "---"
        echo ""
        echo "## Visão Geral do Cluster NASP"
        echo ""
        echo "| Campo | Valor (genérico) |"
        echo "|-------|------------------|"
        
        NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l || echo "N/A")
        K8S_VERSION=$(kubectl version --short 2>/dev/null | grep "Server Version" | awk '{print $3}' || echo "<K8S_VERSION>")
        
        echo "| Número de nodes | $NODE_COUNT |"
        echo "| Versão do Kubernetes | $K8S_VERSION |"
        
        if kubectl get pods -n kube-system -l k8s-app=calico-node &> /dev/null; then
            echo "| CNI | Calico |"
        else
            echo "| CNI | <CNI_TYPE> |"
        fi
        
        echo "| Namespace TriSLA alvo | <TRISLA_NAMESPACE> (ex.: trisla) |"
        echo ""
        echo "---"
        echo ""
        echo "## Serviços Detectados"
        echo ""
        echo "| Componente | Namespace | Tipo de Serviço | Observação |"
        echo "|------------|-----------|-----------------|------------|"
        
        # Adicionar serviços detectados (sem IPs)
        if kubectl get svc -n monitoring -l app=prometheus &> /dev/null; then
            echo "| Prometheus | monitoring | ClusterIP/NodePort | Usado para métricas NASP |"
        fi
        if kubectl get svc -n monitoring -l app=grafana &> /dev/null; then
            echo "| Grafana | monitoring | ClusterIP | UI de visualização de métricas |"
        fi
        if kubectl get svc -A -l app=kafka &> /dev/null; then
            KAFKA_NS=$(kubectl get svc -A -l app=kafka -o jsonpath='{.items[0].metadata.namespace}' 2>/dev/null || echo "<KAFKA_NS>")
            echo "| Kafka | $KAFKA_NS | ClusterIP | Broker para eventos TriSLA/NASP |"
        fi
        
        echo ""
        echo "---"
        echo ""
        echo "## Diagnóstico de Saúde"
        echo ""
        echo "### Problemas Encontrados"
        echo ""
        
        CRASH_COUNT=$(kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded -o json 2>/dev/null | jq '[.items[] | select(.status.containerStatuses[]?.state.waiting.reason=="CrashLoopBackOff")] | length' || echo "0")
        if [ "$CRASH_COUNT" -gt 0 ]; then
            echo "- ⚠️ $CRASH_COUNT pod(s) em CrashLoopBackOff detectado(s)"
        else
            echo "- ✅ Nenhum pod em CrashLoopBackOff"
        fi
        
        echo ""
        echo "---"
        echo ""
        echo "**Nota:** Este relatório foi gerado automaticamente. Para informações detalhadas, consulte o arquivo raw: \`tmp/nasp_context_raw.txt\`"
        
    } > "$REPORT_MD"
fi

echo -e "${GREEN}✅ Relatório gerado: $REPORT_MD${NC}\n"

# ============================================
# Resumo
# ============================================

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}📊 Resumo da Descoberta${NC}"
echo -e "${BLUE}============================================================${NC}\n"

echo -e "${GREEN}✅ Informações coletadas:${NC}"
echo "   - Dados brutos: $REPORT_FILE"
echo "   - Relatório Markdown: $REPORT_MD"
echo ""
echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo "   1. Revisar docs/NASP_CONTEXT_REPORT.md"
echo "   2. Identificar endpoints NASP relevantes"
echo "   3. Preencher helm/trisla/values-production.yaml"
echo "   4. Executar scripts/fill_values_production.sh"
echo ""


