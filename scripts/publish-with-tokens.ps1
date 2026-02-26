# ============================================
# Script para Publicação com Tokens Interativos
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  TriSLA - Publicação v1.0.0 (Com Tokens Interativos)       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar se tokens já estão configurados
if (-not $env:GITHUB_TOKEN_REPO -or -not $env:GHCR_TOKEN_DOCKER) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host "Configuração de Tokens" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Os tokens não estão configurados nesta sessão." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Por favor, execute os seguintes comandos no terminal:" -ForegroundColor White
    Write-Host ""
    Write-Host '  $env:GITHUB_TOKEN_REPO="COLE_AQUI_O_TOKEN_Publicar_Repositorio"' -ForegroundColor Cyan
    Write-Host '  $env:GHCR_TOKEN_DOCKER="COLE_AQUI_O_TOKEN_push_de_Docker"' -ForegroundColor Cyan
    Write-Host '  $env:GHCR_USER="abelisboa"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Depois execute novamente:" -ForegroundColor White
    Write-Host "  .\scripts\master-publish-clean-repo.ps1" -ForegroundColor Green
    Write-Host ""
    Write-Host "OU execute este script novamente após configurar os tokens." -ForegroundColor White
    Write-Host ""
    exit 1
}

# Se chegou aqui, os tokens estão configurados
Write-Host "✅ Tokens configurados!" -ForegroundColor Green
Write-Host "   GITHUB_TOKEN_REPO: $($env:GITHUB_TOKEN_REPO.Length) caracteres" -ForegroundColor Cyan
Write-Host "   GHCR_TOKEN_DOCKER: $($env:GHCR_TOKEN_DOCKER.Length) caracteres" -ForegroundColor Cyan
Write-Host "   GHCR_USER: $($env:GHCR_USER)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Executando script master de publicação...`n" -ForegroundColor Yellow

# Executar script master
.\scripts\master-publish-clean-repo.ps1

