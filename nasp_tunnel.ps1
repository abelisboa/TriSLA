# ======================================================================
# Script: nasp_tunnel_final.ps1
# Autor: Abel Lisboa
# Projeto: TriSLA@NASP
# Função: Criar túnel SSH seguro para o cluster NASP e coletar evidências
# Data: 17/10/2025
# ======================================================================

# ⚙️ CONFIGURAÇÕES
$User = "porvir5g"
$RemoteHost = "ppgca.unisinos.br"
$RemoteAPI = "192.168.10.16"
$LocalPort = "6444"   # Porta local alternativa para túnel
$KubeConfig = "$env:USERPROFILE\.kube\config-nasp"
$OutputDir = "docs\evidencias"

# ======================================================================
# 🧩 PASSO 1 - Testar presença do arquivo kubeconfig
if (-Not (Test-Path $KubeConfig)) {
    Write-Host "❌ Arquivo kubeconfig não encontrado em: $KubeConfig" -ForegroundColor Red
    exit
}
Write-Host "✅ kubeconfig localizado: $KubeConfig" -ForegroundColor Green

# ======================================================================
# 🧩 PASSO 2 - Criar diretório de saída, se não existir
if (-Not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    Write-Host "📁 Diretório criado: $OutputDir" -ForegroundColor Cyan
}

# ======================================================================
# 🧩 PASSO 3 - Verificar se porta local já está ocupada
$PortCheck = Get-NetTCPConnection -LocalPort $LocalPort -ErrorAction SilentlyContinue
if ($PortCheck) {
    Write-Host "⚠️ Porta $LocalPort já está em uso. Feche sessões anteriores ou altere a porta." -ForegroundColor Yellow
    exit
}

# ======================================================================
# 🧩 PASSO 4 - Criar túnel SSH
Write-Host ("🔌 Criando túnel SSH para o NASP ({0} → {1}:{2})..." -f $RemoteHost, $RemoteAPI, $LocalPort) -ForegroundColor Cyan
$sshCommand = ("ssh -L {0}:{1}:{2} {3}@{4}" -f $LocalPort, $RemoteAPI, $LocalPort, $User, $RemoteHost)
Start-Process powershell -ArgumentList "-NoExit", "-Command", $sshCommand -WindowStyle Normal
Start-Sleep -Seconds 6

# ======================================================================
# 🧩 PASSO 5 - Testar conexão com o cluster
Write-Host "🔍 Testando conexão com o cluster NASP..." -ForegroundColor Cyan
try {
    kubectl --kubeconfig $KubeConfig get nodes
    Write-Host "✅ Conexão com o cluster estabelecida!" -ForegroundColor Green
} catch {
    Write-Host "❌ Falha ao conectar ao cluster. Verifique se o túnel SSH está ativo." -ForegroundColor Red
    exit
}

# ======================================================================
# 🧩 PASSO 6 - Coletar evidências
Write-Host "📦 Coletando informações do namespace trisla-nsp..." -ForegroundColor Cyan
try {
    kubectl --kubeconfig $KubeConfig get pods -n trisla-nsp -o wide > "$OutputDir\final_pods_state.txt"
    kubectl --kubeconfig $KubeConfig top pods -n trisla-nsp > "$OutputDir\resource_usage.txt"
    Write-Host "✅ Evidências salvas em: $OutputDir" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao coletar evidências. Verifique a sessão SSH e tente novamente." -ForegroundColor Red
}

# ======================================================================
# 🧩 PASSO 7 - Encerramento
Write-Host ""
Write-Host "🎯 Processo concluído." -ForegroundColor Green
Write-Host "Arquivos gerados:" -ForegroundColor Cyan
Write-Host " - $OutputDir\final_pods_state.txt"
Write-Host " - $OutputDir\resource_usage.txt"
Write-Host ""
Write-Host "🔒 Mantenha a sessão SSH aberta enquanto coleta métricas do NASP." -ForegroundColor Yellow
