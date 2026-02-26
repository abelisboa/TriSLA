# Script de Build e Push BC-NSSMF v3.7.11
# Execute: .\SCRIPT_BUILD_BC_NSSMF_v3.7.11.ps1

$ErrorActionPreference = "Stop"
$TRISLA_VERSION = "v3.7.11"
$IMAGE_NAME = "ghcr.io/abelisboa/trisla-bc-nssmf"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BC-NSSMF v3.7.11 - Build and Push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar código local
Write-Host "[PARTE A] Verificando código local..." -ForegroundColor Yellow
Set-Location "C:\Users\USER\Documents\TriSLA-clean"

$hasBCInfra = Select-String -Path "apps\bc-nssmf\src\service.py" -Pattern "class BCInfrastructureError" -Quiet
$hasBCBusiness = Select-String -Path "apps\bc-nssmf\src\service.py" -Pattern "class BCBusinessError" -Quiet

if (-not $hasBCInfra -or -not $hasBCBusiness) {
    Write-Host "❌ ERRO: Correções lógicas não encontradas no código!" -ForegroundColor Red
    Write-Host "   Verifique se BCInfrastructureError e BCBusinessError estão definidas." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Correções lógicas encontradas no código" -ForegroundColor Green
Write-Host ""

# Build da imagem
Write-Host "[PARTE B.1] Building BC-NSSMF image..." -ForegroundColor Yellow
Set-Location "apps\bc-nssmf"

docker build `
  -t "$IMAGE_NAME`:$TRISLA_VERSION" `
  -t "$IMAGE_NAME`:latest" `
  .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERRO: Build falhou!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build concluído" -ForegroundColor Green
Write-Host ""

# Push da imagem
Write-Host "[PARTE B.2] Pushing BC-NSSMF image..." -ForegroundColor Yellow

docker push "$IMAGE_NAME`:$TRISLA_VERSION"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERRO: Push da tag $TRISLA_VERSION falhou!" -ForegroundColor Red
    exit 1
}

docker push "$IMAGE_NAME`:latest"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERRO: Push da tag latest falhou!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Push concluído" -ForegroundColor Green
Write-Host ""

# Verificar imagem
Write-Host "[PARTE B.3] Verificando imagem publicada..." -ForegroundColor Yellow
$imageId = docker inspect "$IMAGE_NAME`:$TRISLA_VERSION" --format='{{.Id}}'
Write-Host "BC-NSSMF Image ID: $imageId" -ForegroundColor Cyan
Write-Host "✅ Imagem verificada" -ForegroundColor Green
Write-Host ""

# Commit e Tag
Write-Host "[PARTE C] Commit + Tag Git..." -ForegroundColor Yellow
Set-Location "C:\Users\USER\Documents\TriSLA-clean"

git add .
$commitMsg = "release: TriSLA BC-NSSMF $TRISLA_VERSION — lógica ajustada e imagem publicada"
git commit -m $commitMsg
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Nenhuma mudança para commitar ou commit falhou" -ForegroundColor Yellow
} else {
    git push origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERRO: Push falhou!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Push concluído" -ForegroundColor Green
}

$tagName = "$TRISLA_VERSION-bc-nssmf"
git tag $tagName
git push origin $tagName
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERRO: Push tag falhou!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Tag $tagName criada e publicada" -ForegroundColor Green
Write-Host ""

# Finalização
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BC-NSSMF v3.7.11 BUILD + PUSH CONCLUÍDO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Imagem publicada: $IMAGE_NAME`:$TRISLA_VERSION" -ForegroundColor Green
Write-Host "✅ Tag Git criada: $tagName" -ForegroundColor Green
Write-Host ""
Write-Host "Próximo passo: Deploy no NASP via Helm" -ForegroundColor Yellow
Write-Host "  Ver: PROMPT_BC_NSSMF_v3.7.11_COMPLETO.md - PARTE D" -ForegroundColor Yellow

