#!/bin/bash

# Deploy Passo a Passo do TriSLA no NASP
# Execute este script no node1 após conectar via SSH

set -e

echo "🚀 Iniciando deploy passo a passo do TriSLA no NASP..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configurações
TRISLA_REPO="https://github.com/abelisboa/TriSLA-Portal.git"
TRISLA_DIR="/home/porvir5g/trisla-portal"
K8S_NAMESPACE="trisla"
MONITORING_NAMESPACE="monitoring"

# PASSO 1: Atualizar sistema
log "PASSO 1: Atualizando sistema..."
sudo apt update && sudo apt upgrade -y
success "Sistema atualizado"

# PASSO 2: Instalar dependências
log "PASSO 2: Instalando dependências..."
sudo apt install -y git curl wget unzip python3 python3-pip docker.io kubectl
success "Dependências instaladas"

# PASSO 3: Configurar Docker
log "PASSO 3: Configurando Docker..."
sudo systemctl start docker && sudo systemctl enable docker
sudo usermod -aG docker porvir5g
success "Docker configurado"

# PASSO 4: Clonar/Atualizar repositório
log "PASSO 4: Clonando/Atualizando repositório TriSLA..."
if [ -d "$TRISLA_DIR" ]; then
    cd "$TRISLA_DIR"
    git pull origin main
    log "Repositório atualizado"
else
    git clone "$TRISLA_REPO" "$TRISLA_DIR"
    cd "$TRISLA_DIR"
    log "Repositório clonado"
fi
success "Repositório TriSLA pronto"

# PASSO 5: Instalar dependências Python
log "PASSO 5: Instalando dependências Python..."
pip3 install -r requirements.txt
success "Dependências Python instaladas"

# PASSO 6: Configurar variáveis de ambiente
log "PASSO 6: Configurando variáveis de ambiente..."
cat > ~/.env << EOF
TRISLA_VERSION=1.0.0
NASP_ENDPOINT=http://192.168.10.16:8080
K8S_NAMESPACE=trisla
LOG_LEVEL=INFO
EOF
success "Variáveis de ambiente configuradas"

# PASSO 7: Criar namespaces Kubernetes
log "PASSO 7: Criando namespaces Kubernetes..."
kubectl create namespace "$K8S_NAMESPACE" || echo "Namespace trisla já existe"
kubectl create namespace "$MONITORING_NAMESPACE" || echo "Namespace monitoring já existe"
success "Namespaces criados"

# PASSO 8: Deploy NWDAF
log "PASSO 8: Deployando NWDAF..."
helm install nwdaf helm/nwdaf -n "$K8S_NAMESPACE" --wait
success "NWDAF deployado"

# PASSO 9: Deploy Decision Engine
log "PASSO 9: Deployando Decision Engine..."
helm install decision-engine helm/decision-engine -n "$K8S_NAMESPACE" --wait
success "Decision Engine deployado"

# PASSO 10: Deploy SLA Agents
log "PASSO 10: Deployando SLA Agents..."
helm install sla-agents helm/sla-agents -n "$K8S_NAMESPACE" --wait
success "SLA Agents deployados"

# PASSO 11: Deploy Dashboard
log "PASSO 11: Deployando Dashboard..."
helm install dashboard helm/dashboard -n "$K8S_NAMESPACE" --wait
success "Dashboard deployado"

# PASSO 12: Deploy Prometheus
log "PASSO 12: Deployando Prometheus..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n "$MONITORING_NAMESPACE" --wait
success "Prometheus deployado"

# PASSO 13: Deploy Grafana
log "PASSO 13: Deployando Grafana..."
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana -n "$MONITORING_NAMESPACE" --set adminPassword=trisla123 --wait
success "Grafana deployado"

# PASSO 14: Configurar port-forward
log "PASSO 14: Configurando port-forward..."
nohup kubectl port-forward svc/dashboard 8080:80 -n "$K8S_NAMESPACE" > /dev/null 2>&1 &
nohup kubectl port-forward svc/grafana 3000:80 -n "$MONITORING_NAMESPACE" > /dev/null 2>&1 &
nohup kubectl port-forward svc/prometheus 9090:80 -n "$MONITORING_NAMESPACE" > /dev/null 2>&1 &
success "Port-forward configurado"

# PASSO 15: Verificar status
log "PASSO 15: Verificando status dos serviços..."
echo ""
echo "=== STATUS DOS PODS ==="
kubectl get pods -n "$K8S_NAMESPACE"
echo ""
echo "=== STATUS DOS PODS DE MONITORAMENTO ==="
kubectl get pods -n "$MONITORING_NAMESPACE"
echo ""

# PASSO 16: Testar conectividade
log "PASSO 16: Testando conectividade..."
sleep 10

# Testar Dashboard
if curl -f http://localhost:8080/health &> /dev/null; then
    success "Dashboard: OK"
else
    warning "Dashboard: Falha na conexão"
fi

# Testar Grafana
if curl -f http://localhost:3000/api/health &> /dev/null; then
    success "Grafana: OK"
else
    warning "Grafana: Falha na conexão"
fi

# Testar Prometheus
if curl -f http://localhost:9090/-/healthy &> /dev/null; then
    success "Prometheus: OK"
else
    warning "Prometheus: Falha na conexão"
fi

# Resumo final
echo ""
echo "=========================================="
echo "📊 DEPLOY PASSO A PASSO CONCLUÍDO!"
echo "=========================================="
echo ""
echo "✅ Serviços deployados:"
echo "  - NWDAF (Network Data Analytics Function)"
echo "  - Decision Engine"
echo "  - SLA Agents"
echo "  - Dashboard"
echo "  - Prometheus (Monitoramento)"
echo "  - Grafana (Dashboards)"
echo ""
echo "🌐 Endpoints disponíveis:"
echo "  - Dashboard: http://192.168.10.16:8080"
echo "  - Grafana: http://192.168.10.16:3000 (admin/trisla123)"
echo "  - Prometheus: http://192.168.10.16:9090"
echo ""
echo "📋 Próximos passos:"
echo "1. Acessar dashboard em http://192.168.10.16:8080"
echo "2. Configurar slices de rede"
echo "3. Testar integração com NASP"
echo "4. Monitorar métricas em tempo real"
echo ""
echo "🎉 TriSLA Portal pronto para uso em produção!"




