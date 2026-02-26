# ============================================
# Script: Corrigir Cache Corrompido do Docker
# ============================================
# Resolve problemas de blob not found no containerd
# ============================================

$ErrorActionPreference = "Continue"

$BASE_DIR = $PSScriptRoot | Split-Path -Parent
Set-Location $BASE_DIR

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Corrigir Cache Corrompido do Docker          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker não está instalado" -ForegroundColor Red
    exit 1
}

Write-Host "🛑 Parando todos os containers..." -ForegroundColor Yellow
docker stop $(docker ps -aq) 2>&1 | Out-Null
docker compose down --volumes --remove-orphans 2>&1 | Out-Null

Write-Host "🧹 Removendo imagens do Kafka e Zookeeper..." -ForegroundColor Yellow
docker rmi confluentinc/cp-kafka:7.5.0 -f 2>&1 | Out-Null
docker rmi confluentinc/cp-zookeeper:7.5.0 -f 2>&1 | Out-Null

Write-Host "🧹 Limpando sistema Docker completamente..." -ForegroundColor Yellow
docker system prune -a -f --volumes

Write-Host ""
Write-Host "🔄 Reiniciando Docker Desktop..." -ForegroundColor Yellow
Write-Host "   Por favor, reinicie o Docker Desktop manualmente e pressione Enter quando terminar" -ForegroundColor Cyan
Read-Host

Write-Host ""
Write-Host "📥 Fazendo pull das imagens novamente (sem cache)..." -ForegroundColor Cyan
Write-Host "   Tentando forçar download completo..." -ForegroundColor Yellow

# Tentar pull sem cache
docker pull --no-cache confluentinc/cp-zookeeper:7.5.0
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Erro ao fazer pull do Zookeeper (cache corrompido persistente)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Soluções alternativas:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. RESET COMPLETO DO DOCKER DESKTOP:" -ForegroundColor White
    Write-Host "   - Abra Docker Desktop" -ForegroundColor Yellow
    Write-Host "   - Settings → Troubleshoot → Reset to factory defaults" -ForegroundColor Yellow
    Write-Host "   - Isso remove TODAS as imagens e containers" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. USAR IMAGENS ALTERNATIVAS:" -ForegroundColor White
    Write-Host "   Edite docker-compose.yml e use:" -ForegroundColor Yellow
    Write-Host "   - bitnami/zookeeper:latest" -ForegroundColor Yellow
    Write-Host "   - bitnami/kafka:latest" -ForegroundColor Yellow
    Write-Host "   Ou versões anteriores:" -ForegroundColor Yellow
    Write-Host "   - confluentinc/cp-zookeeper:7.4.0" -ForegroundColor Yellow
    Write-Host "   - confluentinc/cp-kafka:7.4.0" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. REINICIAR COMPUTADOR:" -ForegroundColor White
    Write-Host "   Às vezes o containerd precisa ser reiniciado completamente" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

docker pull --no-cache confluentinc/cp-kafka:7.5.0
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer pull do Kafka" -ForegroundColor Red
    Write-Host "   Siga as soluções acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Imagens baixadas com sucesso" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Tentando iniciar serviços..." -ForegroundColor Cyan
docker compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Serviços iniciados com sucesso!" -ForegroundColor Green
    Write-Host ""
    docker compose ps
} else {
    Write-Host ""
    Write-Host "❌ Ainda há problemas. Tente:" -ForegroundColor Red
    Write-Host "   1. Reiniciar o computador" -ForegroundColor Yellow
    Write-Host "   2. Atualizar o Docker Desktop" -ForegroundColor Yellow
    Write-Host "   3. Verificar se há espaço em disco suficiente" -ForegroundColor Yellow
}

