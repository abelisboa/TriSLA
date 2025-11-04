# Script para iniciar backend e abrir no navegador
# Uso: .\scripts\start-backend-and-open.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Iniciando TriSLA Backend..." -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path "backend\main.py")) {
    Write-Host "❌ Erro: Execute este script da raiz do projeto (trisla-dashboard-local)" -ForegroundColor Red
    exit 1
}

# Mudar para diretório do backend
$backendDir = Join-Path $PSScriptRoot ".." "backend" | Resolve-Path
Push-Location $backendDir

try {
    # Verificar se venv existe
    $venvPython = Join-Path $backendDir "venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Host "❌ Erro: Virtual environment não encontrado em $backendDir\venv" -ForegroundColor Red
        Write-Host "   Execute: python -m venv venv" -ForegroundColor Yellow
        exit 1
    }

    # Verificar se backend já está rodando
    $port5000 = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
    if ($port5000) {
        Write-Host "⚠️  Porta 5000 já está em uso!" -ForegroundColor Yellow
        Write-Host "   O backend pode já estar rodando." -ForegroundColor Yellow
        Write-Host ""
        $response = Read-Host "Deseja abrir o navegador mesmo assim? (S/N)"
        if ($response -eq "S" -or $response -eq "s") {
            Start-Process "http://localhost:5000"
            Write-Host "✅ Navegador aberto em http://localhost:5000" -ForegroundColor Green
        }
        exit 0
    }

    Write-Host "1️⃣ Iniciando backend FastAPI..." -ForegroundColor Cyan
    
    # Iniciar backend em nova janela
    $backendProcess = Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/c", "cd /d `"$backendDir`" && `"$venvPython`" -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload" `
        -WindowStyle Normal `
        -PassThru

    Write-Host "   ✅ Backend iniciado (PID: $($backendProcess.Id))" -ForegroundColor Green
    Write-Host ""

    # Aguardar alguns segundos para o backend iniciar
    Write-Host "2️⃣ Aguardando backend iniciar..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3

    # Verificar se backend está respondendo
    $maxRetries = 10
    $retryCount = 0
    $backendReady = $false

    while ($retryCount -lt $maxRetries -and -not $backendReady) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $backendReady = $true
                Write-Host "   ✅ Backend está respondendo!" -ForegroundColor Green
            }
        } catch {
            $retryCount++
            Write-Host "   ⏳ Tentativa $retryCount/$maxRetries..." -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
    }

    if (-not $backendReady) {
        Write-Host "   ⚠️  Backend pode não estar pronto, mas tentando abrir navegador..." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "3️⃣ Abrindo navegador em http://localhost:5000..." -ForegroundColor Cyan
    
    # Abrir navegador
    Start-Process "http://localhost:5000"
    
    Write-Host ""
    Write-Host "✅ Backend rodando e navegador aberto!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 URLs disponíveis:" -ForegroundColor Cyan
    Write-Host "   API:      http://localhost:5000" -ForegroundColor White
    Write-Host "   Health:   http://localhost:5000/health" -ForegroundColor White
    Write-Host "   Swagger:  http://localhost:5000/docs" -ForegroundColor White
    Write-Host "   Redoc:    http://localhost:5000/redoc" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  Para parar o backend, feche a janela do terminal ou pressione Ctrl+C" -ForegroundColor Yellow

} catch {
    Write-Host ""
    Write-Host "❌ Erro ao iniciar backend: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}





