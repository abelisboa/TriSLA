# Script para iniciar dashboard: backend e frontend
# O túnel SSH é opcional e pode ser iniciado separadamente com: .\scripts\start-ssh-tunnel.ps1
# Uso: .\scripts\start-all.ps1

Write-Host "🚀 Iniciando TriSLA Dashboard Local..." -ForegroundColor Cyan
Write-Host ""
Write-Host "ℹ️  O dashboard funciona sem conexão SSH." -ForegroundColor Yellow
Write-Host "   Para conectar ao Prometheus do node1, execute: .\scripts\start-ssh-tunnel.ps1" -ForegroundColor Gray
Write-Host ""

# 1. Verificar se backend está rodando
Write-Host "1️⃣ Verificando backend..." -ForegroundColor Yellow
$backendPath = Resolve-Path "$PSScriptRoot\..\backend"

if (-not (Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    try {
        $cmdLine = Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | 
                   Select-Object -ExpandProperty CommandLine
        $cmdLine -like "*uvicorn*main:app*"
    } catch {
        $false
    }
})) {
    Write-Host "   Iniciando backend..." -ForegroundColor Gray
    # Usa cmd.exe para evitar problemas de política de execução do PowerShell
    $cmdPath = "cmd.exe"
    # Tenta usar o Python do venv diretamente
    $pythonPath = Join-Path $backendPath "venv\Scripts\python.exe"
    if (Test-Path $pythonPath) {
        $cmdArgs = "/k", "cd /d `"$backendPath`" && `"$pythonPath`" -m uvicorn main:app --reload --port 5000"
    } else {
        $cmdArgs = "/k", "cd /d `"$backendPath`" && python -m uvicorn main:app --reload --port 5000"
    }
    Start-Process -FilePath $cmdPath -ArgumentList $cmdArgs -WindowStyle Normal
    Start-Sleep -Seconds 3
    Write-Host "   ✅ Backend iniciado em http://localhost:5000" -ForegroundColor Green
} else {
    Write-Host "   ✅ Backend já está rodando" -ForegroundColor Green
}
Write-Host ""

# 2. Verificar se frontend está rodando
Write-Host "2️⃣ Verificando frontend..." -ForegroundColor Yellow
$frontendPath = Resolve-Path "$PSScriptRoot\..\frontend"

if (-not (Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    try {
        $cmdLine = Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue | 
                   Select-Object -ExpandProperty CommandLine
        $cmdLine -like "*vite*"
    } catch {
        $false
    }
})) {
    Write-Host "   Iniciando frontend..." -ForegroundColor Gray
    # Usa cmd.exe para evitar problemas de política de execução do PowerShell
    $cmdPath = "cmd.exe"
    $cmdArgs = "/k", "cd /d `"$frontendPath`" && npm run dev"
    Start-Process -FilePath $cmdPath -ArgumentList $cmdArgs -WindowStyle Normal
    Start-Sleep -Seconds 5
    Write-Host "   ✅ Frontend iniciado em http://localhost:5173" -ForegroundColor Green
} else {
    Write-Host "   ✅ Frontend já está rodando" -ForegroundColor Green
}
Write-Host ""

Write-Host "✅ Tudo iniciado!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Acesse o dashboard em:" -ForegroundColor Cyan
Write-Host "   http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "🔧 APIs disponíveis:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "   Swagger:  http://localhost:5000/docs" -ForegroundColor White
Write-Host "   Prometheus (via túnel, se configurado): http://localhost:9090" -ForegroundColor Gray
