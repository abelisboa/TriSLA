# Script PowerShell para iniciar túnel SSH para Prometheus
# Uso: .\scripts\start-ssh-tunnel.ps1

Write-Host "🚇 Iniciando túnel SSH para Prometheus..." -ForegroundColor Cyan

# Verificar se já existe um túnel
$existingTunnels = Get-Process ssh -ErrorAction SilentlyContinue | Where-Object {
    try {
        $cmdLine = Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | 
                   Select-Object -ExpandProperty CommandLine
        $cmdLine -like "*9090*" -and $cmdLine -like "*prometheus*"
    } catch {
        $false
    }
}

if ($existingTunnels) {
    Write-Host "⚠️  Túnel SSH já está rodando (PID: $($existingTunnels[0].Id))" -ForegroundColor Yellow
    Write-Host "   Para parar: Stop-Process -Id $($existingTunnels[0].Id)" -ForegroundColor Gray
    exit 0
}

# Configurações
$jumpHost = "porvir5g@ppgca.unisinos.br"
$targetHost = "porvir5g@node006"
$localPort = 9090
$remoteHost = "nasp-prometheus.monitoring.svc.cluster.local"
$remotePort = 9090

Write-Host "   Jump Host: $jumpHost" -ForegroundColor Gray
Write-Host "   Target: $targetHost" -ForegroundColor Gray
Write-Host "   Local Port: $localPort -> ${remoteHost}:${remotePort}" -ForegroundColor Gray
Write-Host ""

# Iniciar túnel em background
Write-Host "Executando túnel SSH..." -ForegroundColor Gray
Start-Process -FilePath "ssh" -ArgumentList "-L", "${localPort}:${remoteHost}:${remotePort}", "-J", $jumpHost, $targetHost, "-N" -WindowStyle Hidden

Start-Sleep -Seconds 3

# Verificar se está rodando
$tunnel = Get-Process ssh -ErrorAction SilentlyContinue | Where-Object {
    try {
        $cmdLine = Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | 
                   Select-Object -ExpandProperty CommandLine
        $cmdLine -like "*9090*"
    } catch {
        $false
    }
}

if ($tunnel) {
    Write-Host "✅ Túnel SSH iniciado com sucesso!" -ForegroundColor Green
    Write-Host "   PID: $($tunnel[0].Id)" -ForegroundColor Gray
    Write-Host "   Acesse Prometheus em: http://localhost:9090" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para parar o túnel:" -ForegroundColor Yellow
    Write-Host "   Stop-Process -Id $($tunnel[0].Id)" -ForegroundColor Gray
} else {
    Write-Host "❌ Falha ao iniciar túnel SSH" -ForegroundColor Red
    Write-Host "   Verifique sua conexão SSH" -ForegroundColor Yellow
}