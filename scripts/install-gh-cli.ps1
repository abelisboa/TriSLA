# ============================================
# Script para Instalar GitHub CLI no Windows
# ============================================

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  Instalando GitHub CLI (gh)                              ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar se já está instalado
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "✅ GitHub CLI já está instalado!" -ForegroundColor Green
    gh --version
    exit 0
}

Write-Host "Tentando instalar via winget..." -ForegroundColor Cyan

# Tentar instalar via winget
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Instalando GitHub CLI usando winget..." -ForegroundColor Yellow
    winget install --id GitHub.cli
    
    # Verificar se foi instalado
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        Write-Host "✅ GitHub CLI instalado com sucesso!" -ForegroundColor Green
        gh --version
    } else {
        Write-Host "❌ Falha na instalação via winget" -ForegroundColor Red
        Write-Host ""
        Write-Host "Por favor, instale manualmente:" -ForegroundColor Yellow
        Write-Host "1. Acesse: https://cli.github.com/" -ForegroundColor White
        Write-Host "2. Baixe o instalador para Windows" -ForegroundColor White
        Write-Host "3. Execute o instalador" -ForegroundColor White
    }
} else {
    Write-Host "❌ winget não está disponível" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instale manualmente:" -ForegroundColor Yellow
    Write-Host "1. Acesse: https://cli.github.com/" -ForegroundColor White
    Write-Host "2. Baixe o instalador para Windows" -ForegroundColor White
    Write-Host "3. Execute o instalador" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou instale o winget primeiro e tente novamente." -ForegroundColor White
}

