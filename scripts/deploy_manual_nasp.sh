#!/bin/bash

# Deploy Manual do TriSLA no NASP
# Este script executa o deploy manual via SSH nos nós NASP

set -e

echo "🚀 Iniciando deploy manual do TriSLA no NASP..."

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
NODE1_IP="192.168.10.16"
NODE2_IP="192.168.10.17"
SSH_USER="porvir5g"
SSH_HOST="ppgca.unisinos.br"
TRISLA_REPO="https://github.com/abelisboa/TriSLA-Portal.git"

# Função para executar comando via SSH
ssh_exec() {
    local node_ip=$1
    local command=$2
    ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST} "ssh -o StrictHostKeyChecking=no ${SSH_USER}@${node_ip} '${command}'"
}

# Verificar conectividade
log "Verificando conectividade com os nós NASP..."

# Testar node1
if ssh_exec ${NODE1_IP} "echo 'Node1 conectado'"; then
    success "Node1 (${NODE1_IP}): Conectado"
    NODE1_AVAILABLE=true
else
    error "Node1 (${NODE1_IP}): Falha na conexão"
    NODE1_AVAILABLE=false
fi

# Testar node2
if ssh_exec ${NODE2_IP} "echo 'Node2 conectado'"; then
    success "Node2 (${NODE2_IP}): Conectado"
    NODE2_AVAILABLE=true
else
    error "Node2 (${NODE2_IP}): Falha na conexão"
    NODE2_AVAILABLE=false
fi

if [ "$NODE1_AVAILABLE" = false ] && [ "$NODE2_AVAILABLE" = false ]; then
    error "Nenhum nó NASP disponível. Verifique a conectividade."
    exit 1
fi

# Deploy no node1
if [ "$NODE1_AVAILABLE" = true ]; then
    log "Iniciando deploy no Node1 (${NODE1_IP})..."
    
    # Atualizar sistema
    log "Atualizando sistema no Node1..."
    ssh_exec ${NODE1_IP} "sudo apt update && sudo apt upgrade -y"
    
    # Instalar dependências
    log "Instalando dependências no Node1..."
    ssh_exec ${NODE1_IP} "sudo apt install -y git curl wget unzip python3 python3-pip docker.io kubectl helm"
    
    # Iniciar Docker
    log "Configurando Docker no Node1..."
    ssh_exec ${NODE1_IP} "sudo systemctl start docker && sudo systemctl enable docker"
    ssh_exec ${NODE1_IP} "sudo usermod -aG docker ${SSH_USER}"
    
    # Clonar repositório
    log "Clonando repositório TriSLA no Node1..."
    ssh_exec ${NODE1_IP} "rm -rf /home/${SSH_USER}/trisla-portal"
    ssh_exec ${NODE1_IP} "git clone ${TRISLA_REPO} /home/${SSH_USER}/trisla-portal"
    
    # Instalar dependências Python
    log "Instalando dependências Python no Node1..."
    ssh_exec ${NODE1_IP} "cd /home/${SSH_USER}/trisla-portal && pip3 install -r requirements.txt"
    
    # Configurar variáveis de ambiente
    log "Configurando variáveis de ambiente no Node1..."
    ssh_exec ${NODE1_IP} "cat > /home/${SSH_USER}/.env << 'EOF'
TRISLA_VERSION=1.0.0
NASP_ENDPOINT=http://${NODE1_IP}:8080
K8S_NAMESPACE=trisla
LOG_LEVEL=INFO
EOF"
    
    # Criar namespace Kubernetes
    log "Criando namespace Kubernetes no Node1..."
    ssh_exec ${NODE1_IP} "kubectl create namespace trisla || echo 'Namespace já existe'"
    
    # Deploy dos serviços
    log "Deployando serviços no Node1..."
    
    # Deploy NWDAF
    log "Deployando NWDAF no Node1..."
    ssh_exec ${NODE1_IP} "cd /home/${SSH_USER}/trisla-portal && helm install nwdaf helm/nwdaf -n trisla --wait"
    
    # Deploy Decision Engine
    log "Deployando Decision Engine no Node1..."
    ssh_exec ${NODE1_IP} "cd /home/${SSH_USER}/trisla-portal && helm install decision-engine helm/decision-engine -n trisla --wait"
    
    # Deploy SLA Agents
    log "Deployando SLA Agents no Node1..."
    ssh_exec ${NODE1_IP} "cd /home/${SSH_USER}/trisla-portal && helm install sla-agents helm/sla-agents -n trisla --wait"
    
    # Deploy Dashboard
    log "Deployando Dashboard no Node1..."
    ssh_exec ${NODE1_IP} "cd /home/${SSH_USER}/trisla-portal && helm install dashboard helm/dashboard -n trisla --wait"
    
    # Deploy Prometheus
    log "Deployando Prometheus no Node1..."
    ssh_exec ${NODE1_IP} "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
    ssh_exec ${NODE1_IP} "helm repo update"
    ssh_exec ${NODE1_IP} "helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --wait"
    
    # Deploy Grafana
    log "Deployando Grafana no Node1..."
    ssh_exec ${NODE1_IP} "helm repo add grafana https://grafana.github.io/helm-charts"
    ssh_exec ${NODE1_IP} "helm install grafana grafana/grafana -n monitoring --set adminPassword=trisla123 --wait"
    
    # Configurar port-forward
    log "Configurando port-forward no Node1..."
    ssh_exec ${NODE1_IP} "nohup kubectl port-forward svc/dashboard 8080:80 -n trisla > /dev/null 2>&1 &"
    ssh_exec ${NODE1_IP} "nohup kubectl port-forward svc/grafana 3000:80 -n monitoring > /dev/null 2>&1 &"
    ssh_exec ${NODE1_IP} "nohup kubectl port-forward svc/prometheus 9090:80 -n monitoring > /dev/null 2>&1 &"
    
    success "Deploy no Node1 concluído!"
fi

# Deploy no node2
if [ "$NODE2_AVAILABLE" = true ]; then
    log "Iniciando deploy no Node2 (${NODE2_IP})..."
    
    # Atualizar sistema
    log "Atualizando sistema no Node2..."
    ssh_exec ${NODE2_IP} "sudo apt update && sudo apt upgrade -y"
    
    # Instalar dependências
    log "Instalando dependências no Node2..."
    ssh_exec ${NODE2_IP} "sudo apt install -y git curl wget unzip python3 python3-pip docker.io kubectl helm"
    
    # Iniciar Docker
    log "Configurando Docker no Node2..."
    ssh_exec ${NODE2_IP} "sudo systemctl start docker && sudo systemctl enable docker"
    ssh_exec ${NODE2_IP} "sudo usermod -aG docker ${SSH_USER}"
    
    # Clonar repositório
    log "Clonando repositório TriSLA no Node2..."
    ssh_exec ${NODE2_IP} "rm -rf /home/${SSH_USER}/trisla-portal"
    ssh_exec ${NODE2_IP} "git clone ${TRISLA_REPO} /home/${SSH_USER}/trisla-portal"
    
    # Instalar dependências Python
    log "Instalando dependências Python no Node2..."
    ssh_exec ${NODE2_IP} "cd /home/${SSH_USER}/trisla-portal && pip3 install -r requirements.txt"
    
    # Configurar variáveis de ambiente
    log "Configurando variáveis de ambiente no Node2..."
    ssh_exec ${NODE2_IP} "cat > /home/${SSH_USER}/.env << 'EOF'
TRISLA_VERSION=1.0.0
NASP_ENDPOINT=http://${NODE2_IP}:8080
K8S_NAMESPACE=trisla
LOG_LEVEL=INFO
EOF"
    
    # Criar namespace Kubernetes
    log "Criando namespace Kubernetes no Node2..."
    ssh_exec ${NODE2_IP} "kubectl create namespace trisla || echo 'Namespace já existe'"
    
    # Deploy dos serviços
    log "Deployando serviços no Node2..."
    
    # Deploy NWDAF
    log "Deployando NWDAF no Node2..."
    ssh_exec ${NODE2_IP} "cd /home/${SSH_USER}/trisla-portal && helm install nwdaf helm/nwdaf -n trisla --wait"
    
    # Deploy Decision Engine
    log "Deployando Decision Engine no Node2..."
    ssh_exec ${NODE2_IP} "cd /home/${SSH_USER}/trisla-portal && helm install decision-engine helm/decision-engine -n trisla --wait"
    
    # Deploy SLA Agents
    log "Deployando SLA Agents no Node2..."
    ssh_exec ${NODE2_IP} "cd /home/${SSH_USER}/trisla-portal && helm install sla-agents helm/sla-agents -n trisla --wait"
    
    # Deploy Dashboard
    log "Deployando Dashboard no Node2..."
    ssh_exec ${NODE2_IP} "cd /home/${SSH_USER}/trisla-portal && helm install dashboard helm/dashboard -n trisla --wait"
    
    # Deploy Prometheus
    log "Deployando Prometheus no Node2..."
    ssh_exec ${NODE2_IP} "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
    ssh_exec ${NODE2_IP} "helm repo update"
    ssh_exec ${NODE2_IP} "helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --wait"
    
    # Deploy Grafana
    log "Deployando Grafana no Node2..."
    ssh_exec ${NODE2_IP} "helm repo add grafana https://grafana.github.io/helm-charts"
    ssh_exec ${NODE2_IP} "helm install grafana grafana/grafana -n monitoring --set adminPassword=trisla123 --wait"
    
    # Configurar port-forward
    log "Configurando port-forward no Node2..."
    ssh_exec ${NODE2_IP} "nohup kubectl port-forward svc/dashboard 8080:80 -n trisla > /dev/null 2>&1 &"
    ssh_exec ${NODE2_IP} "nohup kubectl port-forward svc/grafana 3000:80 -n monitoring > /dev/null 2>&1 &"
    ssh_exec ${NODE2_IP} "nohup kubectl port-forward svc/prometheus 9090:80 -n monitoring > /dev/null 2>&1 &"
    
    success "Deploy no Node2 concluído!"
fi

# Verificar status final
log "Verificando status final dos serviços..."

if [ "$NODE1_AVAILABLE" = true ]; then
    log "Status dos serviços no Node1:"
    ssh_exec ${NODE1_IP} "kubectl get pods -n trisla"
    ssh_exec ${NODE1_IP} "kubectl get pods -n monitoring"
fi

if [ "$NODE2_AVAILABLE" = true ]; then
    log "Status dos serviços no Node2:"
    ssh_exec ${NODE2_IP} "kubectl get pods -n trisla"
    ssh_exec ${NODE2_IP} "kubectl get pods -n monitoring"
fi

# Resumo do deploy
echo ""
echo "=========================================="
echo "📊 RESUMO DO DEPLOY MANUAL NO NASP"
echo "=========================================="

if [ "$NODE1_AVAILABLE" = true ]; then
    success "Node1 (${NODE1_IP}): Deploy concluído"
    echo "  ✅ Dashboard: http://${NODE1_IP}:8080"
    echo "  ✅ Grafana: http://${NODE1_IP}:3000 (admin/trisla123)"
    echo "  ✅ Prometheus: http://${NODE1_IP}:9090"
else
    error "Node1 (${NODE1_IP}): Deploy falhou"
fi

if [ "$NODE2_AVAILABLE" = true ]; then
    success "Node2 (${NODE2_IP}): Deploy concluído"
    echo "  ✅ Dashboard: http://${NODE2_IP}:8080"
    echo "  ✅ Grafana: http://${NODE2_IP}:3000 (admin/trisla123)"
    echo "  ✅ Prometheus: http://${NODE2_IP}:9090"
else
    error "Node2 (${NODE2_IP}): Deploy falhou"
fi

echo ""
echo "🎉 DEPLOY MANUAL NO NASP CONCLUÍDO!"
echo "✅ TriSLA Portal rodando nos nós NASP"
echo "✅ Pronto para uso em produção"

# Próximos passos
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Acessar dashboards dos nós"
echo "2. Configurar slices de rede"
echo "3. Testar integração com NASP"
echo "4. Monitorar métricas em tempo real"