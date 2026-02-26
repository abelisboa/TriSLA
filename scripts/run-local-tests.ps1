# ============================================
# Script: Executar Testes Locais do TriSLA (PowerShell)
# ============================================
# Executa testes automatizados que podem ser feitos localmente
# ============================================

$ErrorActionPreference = "Continue"

$BASE_DIR = $PSScriptRoot | Split-Path -Parent
Set-Location $BASE_DIR

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Executar Testes Locais                       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar se pytest está instalado
if (-not (Get-Command pytest -ErrorAction SilentlyContinue)) {
    Write-Host "❌ pytest não está instalado" -ForegroundColor Red
    Write-Host "   Instale com: pip install pytest pytest-asyncio httpx" -ForegroundColor Yellow
    exit 1
}

# Executar testes unitários
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🧪 Executando Testes Unitários" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "tests\unit") {
    pytest tests/unit/ -v --tb=short
}
else {
    Write-Host "⚠️  Diretório de testes unitários não encontrado" -ForegroundColor Yellow
}

Write-Host ""

# Executar testes de integração
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔗 Executando Testes de Integração" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "tests\integration") {
    pytest tests/integration/ -v --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Alguns testes de integração falharam (pode ser esperado se serviços não estiverem rodando)" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️  Diretório de testes de integração não encontrado" -ForegroundColor Yellow
}

Write-Host ""

# Executar testes E2E (se disponíveis)
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🎯 Executando Testes End-to-End" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "tests\e2e") {
    pytest tests/e2e/ -v --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Alguns testes E2E falharam (pode ser esperado se serviços não estiverem rodando)" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️  Diretório de testes E2E não encontrado" -ForegroundColor Yellow
}

Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Testes Concluídos" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

