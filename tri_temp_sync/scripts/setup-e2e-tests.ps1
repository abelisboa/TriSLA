# ============================================
# Script: Setup e Execução de Testes E2E
# ============================================
# Configura ambiente e executa testes end-to-end
# ============================================

$ErrorActionPreference = "Continue"

$BASE_DIR = $PSScriptRoot | Split-Path -Parent
Set-Location $BASE_DIR

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Setup e Execução de Testes E2E               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker não está instalado ou não está no PATH" -ForegroundColor Red
    Write-Host "   Instale o Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Verificar se Docker está rodando
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker não está rodando" -ForegroundColor Red
    Write-Host "   Inicie o Docker Desktop e tente novamente" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker está disponível" -ForegroundColor Green
Write-Host ""

# Limpar cache do Docker se houver problemas
$cleanCache = Read-Host "Deseja limpar o cache do Docker antes de iniciar? (s/N)"
if ($cleanCache -eq "s" -or $cleanCache -eq "S") {
    Write-Host "🧹 Limpando cache do Docker..." -ForegroundColor Yellow
    docker system prune -a -f --volumes
    Write-Host "✅ Cache limpo" -ForegroundColor Green
    Write-Host ""
}

# Parar serviços existentes
Write-Host "🛑 Parando serviços existentes..." -ForegroundColor Yellow
docker compose down 2>&1 | Out-Null
Write-Host ""

# Iniciar serviços
Write-Host "🚀 Iniciando serviços Docker Compose..." -ForegroundColor Cyan
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao iniciar serviços Docker" -ForegroundColor Red
    Write-Host "   Problema detectado: blob not found (cache corrompido)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Soluções recomendadas:" -ForegroundColor Cyan
    Write-Host "   1. Execute o script de correção:" -ForegroundColor White
    Write-Host "      powershell -ExecutionPolicy Bypass -File scripts/fix-docker-cache.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   2. Ou manualmente:" -ForegroundColor White
    Write-Host "      - Reinicie o Docker Desktop" -ForegroundColor Yellow
    Write-Host "      - Execute: docker system prune -a -f --volumes" -ForegroundColor Yellow
    Write-Host "      - Execute: docker pull confluentinc/cp-kafka:7.5.0" -ForegroundColor Yellow
    Write-Host "      - Execute: docker pull confluentinc/cp-zookeeper:7.5.0" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ Serviços iniciados" -ForegroundColor Green
Write-Host ""

# Aguardar serviços ficarem saudáveis
Write-Host "⏳ Aguardando serviços ficarem saudáveis (30 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verificar status dos serviços
Write-Host ""
Write-Host "📊 Status dos serviços:" -ForegroundColor Cyan
docker compose ps
Write-Host ""

# Verificar se serviços principais estão acessíveis
Write-Host "🔍 Verificando conectividade dos serviços..." -ForegroundColor Cyan

$services = @(
    @{Name="sem-csmf"; Port=8080},
    @{Name="sla-agent-layer"; Port=8084},
    @{Name="nasp-adapter"; Port=8085}
)

$allHealthy = $true
foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        Write-Host "  ✅ $($service.Name) está respondendo" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️  $($service.Name) não está respondendo ainda (pode estar iniciando)" -ForegroundColor Yellow
        $allHealthy = $false
    }
}

Write-Host ""

# Executar testes
if ($allHealthy) {
    Write-Host "🧪 Executando testes E2E..." -ForegroundColor Cyan
    Write-Host ""
    python -m pytest tests/e2e/ -v --tb=short
} else {
    Write-Host "⚠️  Alguns serviços não estão respondendo ainda" -ForegroundColor Yellow
    Write-Host "   Aguardando mais 30 segundos..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    Write-Host ""
    Write-Host "🧪 Executando testes E2E..." -ForegroundColor Cyan
    Write-Host ""
    python -m pytest tests/e2e/ -v --tb=short
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Processo concluído" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Para parar os serviços, execute:" -ForegroundColor Yellow
Write-Host "   docker compose down" -ForegroundColor White
Write-Host ""

