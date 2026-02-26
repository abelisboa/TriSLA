# ============================================
# Script para Push de Todas as Imagens para GHCR
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Push de Todas as Imagens para GHCR             ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

$version = "v1.0.0"
$images = @(
    "ghcr.io/abelisboa/trisla-sem-csmf:$version",
    "ghcr.io/abelisboa/trisla-ml-nsmf:$version",
    "ghcr.io/abelisboa/trisla-decision-engine:$version",
    "ghcr.io/abelisboa/trisla-bc-nssmf:$version",
    "ghcr.io/abelisboa/trisla-sla-agent-layer:$version",
    "ghcr.io/abelisboa/trisla-nasp-adapter:$version",
    "ghcr.io/abelisboa/trisla-ui-dashboard:$version"
)

$successCount = 0
$failCount = 0

foreach ($image in $images) {
    Write-Host "📤 Fazendo push de: $image" -ForegroundColor Cyan
    docker push $image
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Push realizado com sucesso!" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "   ❌ Erro ao fazer push" -ForegroundColor Red
        $failCount++
    }
    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Resumo do Push"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "  ✅ Sucesso: $successCount" -ForegroundColor Green
Write-Host "  ❌ Falhas: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "🎉 Todas as imagens foram enviadas para GHCR!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Algumas imagens falharam. Verifique a autenticação:" -ForegroundColor Yellow
    Write-Host "   docker login ghcr.io -u abelisboa"
    Write-Host ""
}

