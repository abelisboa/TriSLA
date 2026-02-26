# ============================================
# Script: Usar Versões Anteriores (Confluent)
# ============================================
# Substitui imagens Confluent 7.5.0 por versões anteriores 7.4.0
# Resolve problemas de cache corrompido
# ============================================

$ErrorActionPreference = "Continue"

$BASE_DIR = $PSScriptRoot | Split-Path -Parent
Set-Location $BASE_DIR

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Usar Versões Anteriores (Confluent 7.4.0)     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$composeFile = "docker-compose.yml"
$backupFile = "docker-compose.yml.backup"

# Fazer backup
if (Test-Path $composeFile) {
    Copy-Item $composeFile $backupFile -Force
    Write-Host "✅ Backup criado: $backupFile" -ForegroundColor Green
} else {
    Write-Host "❌ docker-compose.yml não encontrado" -ForegroundColor Red
    exit 1
}

# Ler conteúdo
$content = Get-Content $composeFile -Raw

# Substituir imagens
Write-Host "🔄 Substituindo para versões anteriores do Confluent (7.4.0)..." -ForegroundColor Yellow

# Zookeeper - usar versão anterior do Confluent
$content = $content -replace 'image: confluentinc/cp-zookeeper:7\.5\.0', 'image: confluentinc/cp-zookeeper:7.4.0'

# Kafka - usar versão anterior do Confluent
$content = $content -replace 'image: confluentinc/cp-kafka:7\.5\.0', 'image: confluentinc/cp-kafka:7.4.0'

# As variáveis de ambiente do Confluent permanecem as mesmas

# Salvar
Set-Content -Path $composeFile -Value $content -NoNewline

Write-Host "✅ Imagens substituídas com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Alterações:" -ForegroundColor Cyan
Write-Host "   - Zookeeper: confluentinc/cp-zookeeper:7.5.0 → confluentinc/cp-zookeeper:7.4.0" -ForegroundColor White
Write-Host "   - Kafka: confluentinc/cp-kafka:7.5.0 → confluentinc/cp-kafka:7.4.0" -ForegroundColor White
Write-Host "   (Usando versões anteriores que são mais estáveis)" -ForegroundColor Yellow
Write-Host ""
Write-Host "💾 Backup salvo em: $backupFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Agora você pode executar:" -ForegroundColor Cyan
Write-Host "   docker compose up -d" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Para reverter:" -ForegroundColor Yellow
Write-Host "   Copy-Item docker-compose.yml.backup docker-compose.yml -Force" -ForegroundColor White
Write-Host ""

