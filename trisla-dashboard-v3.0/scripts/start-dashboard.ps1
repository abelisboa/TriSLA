# Script para iniciar o TriSLA Dashboard v3.0 no Windows

# Definir o diretório raiz
$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ROOT_DIR

# Função para liberar uma porta
function Free-Port {
    param($Port)
    $connections = netstat -ano | findstr ":$Port"
    if ($connections) {
        $connections -match ":$Port\s+.*\s+(\d+)" | Out-Null
        if ($matches) {
            $pid = $matches[1]
            Write-Host "Liberando porta $Port (PID: $pid)..."
            taskkill /PID $pid /F
            Start-Sleep -Seconds 1
        }
    }
}

# Liberar portas
Free-Port 5000
Free-Port 5173

Write-Host "🚀 Iniciando TriSLA Dashboard v3.0 (backend + frontend)" -ForegroundColor Cyan

# Verificar e instalar dependências do backend
Write-Host "📦 Instalando dependências do backend..." -ForegroundColor Yellow
if (-not (Test-Path "backend\venv")) {
    Write-Host "Criando ambiente virtual Python..."
    python -m venv backend\venv
}
& backend\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

# Verificar se config.yaml existe, se não, copiar do exemplo
if (-not (Test-Path "backend\config.yaml")) {
    Write-Host "📄 Criando arquivo de configuração padrão..." -ForegroundColor Yellow
    Copy-Item "backend\config.yaml.example" "backend\config.yaml"
}

# Iniciar o backend
Write-Host "🔄 Iniciando backend..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:ROOT_DIR\backend
    & .\venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 5000
}
$backendPid = $backendJob.Id
$backendPid | Out-File -FilePath ".backend.pid"
Start-Sleep -Seconds 2

# Iniciar o frontend
Write-Host "🔄 Iniciando frontend..." -ForegroundColor Green
Set-Location frontend
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependências do frontend..." -ForegroundColor Yellow
    npm install
}
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:ROOT_DIR\frontend
    npm run dev -- --host --port 5173
}
$frontendPid = $frontendJob.Id
$frontendPid | Out-File -FilePath "$ROOT_DIR\.frontend.pid"
Start-Sleep -Seconds 2

Set-Location $ROOT_DIR

# Obter URLs de configuração
$configContent = Get-Content "backend\config.yaml" -Raw
$prometheusUrl = if ($configContent -match "prometheus:\s*\n\s*url:\s*""([^""]+)""") { $matches[1] } else { "http://localhost:9090" }
$semNsmfUrl = if ($configContent -match "sem_nsmf:\s*\n\s*url:\s*""([^""]+)""") { $matches[1] } else { "http://localhost:8000" }

Write-Host "✅ TriSLA Dashboard v3.0 iniciado com sucesso!" -ForegroundColor Green
Write-Host "🔗 UI: http://localhost:5173   |   API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📊 Prometheus: $prometheusUrl (configurado em backend/config.yaml)" -ForegroundColor Cyan
Write-Host "🤖 SEM-NSMF: $semNsmfUrl (configurado em backend/config.yaml)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para encerrar os serviços" -ForegroundColor Yellow

try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Verificar se os jobs ainda estão em execução
        $backendRunning = Get-Job -Id $backendPid -ErrorAction SilentlyContinue
        $frontendRunning = Get-Job -Id $frontendPid -ErrorAction SilentlyContinue
        
        if (-not $backendRunning -or -not $frontendRunning) {
            Write-Host "Um dos serviços foi encerrado. Encerrando..." -ForegroundColor Red
            break
        }
    }
}
finally {
    # Encerrar os jobs
    if (Test-Path ".backend.pid") {
        $backendPid = Get-Content ".backend.pid"
        Stop-Job -Id $backendPid -ErrorAction SilentlyContinue
        Remove-Job -Id $backendPid -Force -ErrorAction SilentlyContinue
        Remove-Item ".backend.pid" -ErrorAction SilentlyContinue
    }
    
    if (Test-Path ".frontend.pid") {
        $frontendPid = Get-Content ".frontend.pid"
        Stop-Job -Id $frontendPid -ErrorAction SilentlyContinue
        Remove-Job -Id $frontendPid -Force -ErrorAction SilentlyContinue
        Remove-Item ".frontend.pid" -ErrorAction SilentlyContinue
    }
    
    Write-Host "Serviços encerrados." -ForegroundColor Yellow
}



