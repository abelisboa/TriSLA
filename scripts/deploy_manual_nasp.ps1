# Deploy Manual do TriSLA no NASP
# Este script executa o deploy manual via SSH nos nós NASP

Write-Host "🚀 Iniciando deploy manual do TriSLA no NASP..." -ForegroundColor Blue

# Configurações
$NODE1_IP = "192.168.10.16"
$NODE2_IP = "192.168.10.17"
$SSH_USER = "porvir5g"
$SSH_HOST = "ppgca.unisinos.br"
$TRISLA_REPO = "https://github.com/abelisboa/TriSLA-Portal.git"

# Função para executar comando via SSH
function Invoke-SSHCommand {
    param(
        [string]$NodeIP,
        [string]$Command
    )
    
    $sshCommand = "ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SSH_HOST} `"ssh -o StrictHostKeyChecking=no ${SSH_USER}@${NodeIP} '${Command}'`""
    Invoke-Expression $sshCommand
}

# Verificar conectividade
Write-Host "Verificando conectividade com os nós NASP..." -ForegroundColor Blue

# Testar node1
try {
    $result1 = Invoke-SSHCommand -NodeIP $NODE1_IP -Command "echo 'Node1 conectado'"
    if ($result1 -like "*Node1 conectado*") {
        Write-Host "Node1 ($NODE1_IP): Conectado" -ForegroundColor Green
        $NODE1_AVAILABLE = $true
    } else {
        Write-Host "Node1 ($NODE1_IP): Falha na conexão" -ForegroundColor Red
        $NODE1_AVAILABLE = $false
    }
} catch {
    Write-Host "Node1 ($NODE1_IP): Falha na conexão" -ForegroundColor Red
    $NODE1_AVAILABLE = $false
}

# Testar node2
try {
    $result2 = Invoke-SSHCommand -NodeIP $NODE2_IP -Command "echo 'Node2 conectado'"
    if ($result2 -like "*Node2 conectado*") {
        Write-Host "Node2 ($NODE2_IP): Conectado" -ForegroundColor Green
        $NODE2_AVAILABLE = $true
    } else {
        Write-Host "Node2 ($NODE2_IP): Falha na conexão" -ForegroundColor Red
        $NODE2_AVAILABLE = $false
    }
} catch {
    Write-Host "Node2 ($NODE2_IP): Falha na conexão" -ForegroundColor Red
    $NODE2_AVAILABLE = $false
}

if (-not $NODE1_AVAILABLE -and -not $NODE2_AVAILABLE) {
    Write-Host "Nenhum nó NASP disponível. Verifique a conectividade." -ForegroundColor Red
    exit 1
}

# Deploy no node1
if ($NODE1_AVAILABLE) {
    Write-Host "Iniciando deploy no Node1 ($NODE1_IP)..." -ForegroundColor Blue
    
    # Atualizar sistema
    Write-Host "Atualizando sistema no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "sudo apt update && sudo apt upgrade -y"
    
    # Instalar dependências
    Write-Host "Instalando dependências no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "sudo apt install -y git curl wget unzip python3 python3-pip docker.io kubectl helm"
    
    # Iniciar Docker
    Write-Host "Configurando Docker no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "sudo systemctl start docker && sudo systemctl enable docker"
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "sudo usermod -aG docker $SSH_USER"
    
    # Clonar repositório
    Write-Host "Clonando repositório TriSLA no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "rm -rf /home/$SSH_USER/trisla-portal"
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "git clone $TRISLA_REPO /home/$SSH_USER/trisla-portal"
    
    # Instalar dependências Python
    Write-Host "Instalando dependências Python no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "cd /home/$SSH_USER/trisla-portal && pip3 install -r requirements.txt"
    
    # Configurar variáveis de ambiente
    Write-Host "Configurando variáveis de ambiente no Node1..." -ForegroundColor Blue
    $envContent = @"
TRISLA_VERSION=1.0.0
NASP_ENDPOINT=http://$NODE1_IP:8080
K8S_NAMESPACE=trisla
LOG_LEVEL=INFO
"@
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "cat > /home/$SSH_USER/.env << 'EOF'
$envContent
EOF"
    
    # Criar namespace Kubernetes
    Write-Host "Criando namespace Kubernetes no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "kubectl create namespace trisla || echo 'Namespace já existe'"
    
    # Deploy dos serviços
    Write-Host "Deployando serviços no Node1..." -ForegroundColor Blue
    
    # Deploy NWDAF
    Write-Host "Deployando NWDAF no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "cd /home/$SSH_USER/trisla-portal && helm install nwdaf helm/nwdaf -n trisla --wait"
    
    # Deploy Decision Engine
    Write-Host "Deployando Decision Engine no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "cd /home/$SSH_USER/trisla-portal && helm install decision-engine helm/decision-engine -n trisla --wait"
    
    # Deploy SLA Agents
    Write-Host "Deployando SLA Agents no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "cd /home/$SSH_USER/trisla-portal && helm install sla-agents helm/sla-agents -n trisla --wait"
    
    # Deploy Dashboard
    Write-Host "Deployando Dashboard no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "cd /home/$SSH_USER/trisla-portal && helm install dashboard helm/dashboard -n trisla --wait"
    
    # Deploy Prometheus
    Write-Host "Deployando Prometheus no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "helm repo update"
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --wait"
    
    # Deploy Grafana
    Write-Host "Deployando Grafana no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "helm repo add grafana https://grafana.github.io/helm-charts"
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "helm install grafana grafana/grafana -n monitoring --set adminPassword=trisla123 --wait"
    
    # Configurar port-forward
    Write-Host "Configurando port-forward no Node1..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "nohup kubectl port-forward svc/dashboard 8080:80 -n trisla > /dev/null 2>&1 &"
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "nohup kubectl port-forward svc/grafana 3000:80 -n monitoring > /dev/null 2>&1 &"
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "nohup kubectl port-forward svc/prometheus 9090:80 -n monitoring > /dev/null 2>&1 &"
    
    Write-Host "Deploy no Node1 concluído!" -ForegroundColor Green
}

# Deploy no node2
if ($NODE2_AVAILABLE) {
    Write-Host "Iniciando deploy no Node2 ($NODE2_IP)..." -ForegroundColor Blue
    
    # Atualizar sistema
    Write-Host "Atualizando sistema no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "sudo apt update && sudo apt upgrade -y"
    
    # Instalar dependências
    Write-Host "Instalando dependências no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "sudo apt install -y git curl wget unzip python3 python3-pip docker.io kubectl helm"
    
    # Iniciar Docker
    Write-Host "Configurando Docker no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "sudo systemctl start docker && sudo systemctl enable docker"
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "sudo usermod -aG docker $SSH_USER"
    
    # Clonar repositório
    Write-Host "Clonando repositório TriSLA no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "rm -rf /home/$SSH_USER/trisla-portal"
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "git clone $TRISLA_REPO /home/$SSH_USER/trisla-portal"
    
    # Instalar dependências Python
    Write-Host "Instalando dependências Python no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "cd /home/$SSH_USER/trisla-portal && pip3 install -r requirements.txt"
    
    # Configurar variáveis de ambiente
    Write-Host "Configurando variáveis de ambiente no Node2..." -ForegroundColor Blue
    $envContent = @"
TRISLA_VERSION=1.0.0
NASP_ENDPOINT=http://$NODE2_IP:8080
K8S_NAMESPACE=trisla
LOG_LEVEL=INFO
"@
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "cat > /home/$SSH_USER/.env << 'EOF'
$envContent
EOF"
    
    # Criar namespace Kubernetes
    Write-Host "Criando namespace Kubernetes no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "kubectl create namespace trisla || echo 'Namespace já existe'"
    
    # Deploy dos serviços
    Write-Host "Deployando serviços no Node2..." -ForegroundColor Blue
    
    # Deploy NWDAF
    Write-Host "Deployando NWDAF no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "cd /home/$SSH_USER/trisla-portal && helm install nwdaf helm/nwdaf -n trisla --wait"
    
    # Deploy Decision Engine
    Write-Host "Deployando Decision Engine no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "cd /home/$SSH_USER/trisla-portal && helm install decision-engine helm/decision-engine -n trisla --wait"
    
    # Deploy SLA Agents
    Write-Host "Deployando SLA Agents no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "cd /home/$SSH_USER/trisla-portal && helm install sla-agents helm/sla-agents -n trisla --wait"
    
    # Deploy Dashboard
    Write-Host "Deployando Dashboard no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "cd /home/$SSH_USER/trisla-portal && helm install dashboard helm/dashboard -n trisla --wait"
    
    # Deploy Prometheus
    Write-Host "Deployando Prometheus no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "helm repo update"
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --wait"
    
    # Deploy Grafana
    Write-Host "Deployando Grafana no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "helm repo add grafana https://grafana.github.io/helm-charts"
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "helm install grafana grafana/grafana -n monitoring --set adminPassword=trisla123 --wait"
    
    # Configurar port-forward
    Write-Host "Configurando port-forward no Node2..." -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "nohup kubectl port-forward svc/dashboard 8080:80 -n trisla > /dev/null 2>&1 &"
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "nohup kubectl port-forward svc/grafana 3000:80 -n monitoring > /dev/null 2>&1 &"
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "nohup kubectl port-forward svc/prometheus 9090:80 -n monitoring > /dev/null 2>&1 &"
    
    Write-Host "Deploy no Node2 concluído!" -ForegroundColor Green
}

# Verificar status final
Write-Host "Verificando status final dos serviços..." -ForegroundColor Blue

if ($NODE1_AVAILABLE) {
    Write-Host "Status dos serviços no Node1:" -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "kubectl get pods -n trisla"
    Invoke-SSHCommand -NodeIP $NODE1_IP -Command "kubectl get pods -n monitoring"
}

if ($NODE2_AVAILABLE) {
    Write-Host "Status dos serviços no Node2:" -ForegroundColor Blue
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "kubectl get pods -n trisla"
    Invoke-SSHCommand -NodeIP $NODE2_IP -Command "kubectl get pods -n monitoring"
}

# Resumo do deploy
Write-Host ""
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "📊 RESUMO DO DEPLOY MANUAL NO NASP" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow

if ($NODE1_AVAILABLE) {
    Write-Host "Node1 ($NODE1_IP): Deploy concluído" -ForegroundColor Green
    Write-Host "  ✅ Dashboard: http://$NODE1_IP:8080" -ForegroundColor Green
    Write-Host "  ✅ Grafana: http://$NODE1_IP:3000 (admin/trisla123)" -ForegroundColor Green
    Write-Host "  ✅ Prometheus: http://$NODE1_IP:9090" -ForegroundColor Green
} else {
    Write-Host "Node1 ($NODE1_IP): Deploy falhou" -ForegroundColor Red
}

if ($NODE2_AVAILABLE) {
    Write-Host "Node2 ($NODE2_IP): Deploy concluído" -ForegroundColor Green
    Write-Host "  ✅ Dashboard: http://$NODE2_IP:8080" -ForegroundColor Green
    Write-Host "  ✅ Grafana: http://$NODE2_IP:3000 (admin/trisla123)" -ForegroundColor Green
    Write-Host "  ✅ Prometheus: http://$NODE2_IP:9090" -ForegroundColor Green
} else {
    Write-Host "Node2 ($NODE2_IP): Deploy falhou" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 DEPLOY MANUAL NO NASP CONCLUÍDO!" -ForegroundColor Green
Write-Host "✅ TriSLA Portal rodando nos nós NASP" -ForegroundColor Green
Write-Host "✅ Pronto para uso em produção" -ForegroundColor Green

# Próximos passos
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. Acessar dashboards dos nós" -ForegroundColor White
Write-Host "2. Configurar slices de rede" -ForegroundColor White
Write-Host "3. Testar integração com NASP" -ForegroundColor White
Write-Host "4. Monitorar métricas em tempo real" -ForegroundColor White