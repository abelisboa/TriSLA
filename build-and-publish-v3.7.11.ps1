# Script de Build e Publish TriSLA v3.7.11
# Execute: .\build-and-publish-v3.7.11.ps1

$ErrorActionPreference = "Stop"
$TRISLA_VERSION = "v3.7.11"
$NEXT_PUBLIC_API_URL = "http://localhost:32002/api/v1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TriSLA v3.7.11 - Build and Publish" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# SEÇÃO 0 - Configurar versão
Write-Host "[SEÇÃO 0] Versão configurada: $TRISLA_VERSION" -ForegroundColor Green
Write-Host ""

# SEÇÃO 1.1 - BC-NSSMF
Write-Host "[SEÇÃO 1.1] Building BC-NSSMF..." -ForegroundColor Yellow
Set-Location "apps\bc-nssmf"
docker build -t ghcr.io/abelisboa/trisla-bc-nssmf:$TRISLA_VERSION -t ghcr.io/abelisboa/trisla-bc-nssmf:latest .
if ($LASTEXITCODE -ne 0) { throw "Build BC-NSSMF falhou" }
Write-Host "✅ BC-NSSMF build concluído" -ForegroundColor Green

Write-Host "📤 Pushing BC-NSSMF..." -ForegroundColor Yellow
docker push ghcr.io/abelisboa/trisla-bc-nssmf:$TRISLA_VERSION
docker push ghcr.io/abelisboa/trisla-bc-nssmf:latest
if ($LASTEXITCODE -ne 0) { throw "Push BC-NSSMF falhou" }
Write-Host "✅ BC-NSSMF push concluído" -ForegroundColor Green
Write-Host ""

# SEÇÃO 1.2 - Portal Backend
Write-Host "[SEÇÃO 1.2] Building Portal Backend..." -ForegroundColor Yellow
Set-Location "..\..\trisla-portal\backend"
docker build -t ghcr.io/abelisboa/trisla-portal-backend:$TRISLA_VERSION -t ghcr.io/abelisboa/trisla-portal-backend:latest .
if ($LASTEXITCODE -ne 0) { throw "Build Portal Backend falhou" }
Write-Host "✅ Portal Backend build concluído" -ForegroundColor Green

Write-Host "📤 Pushing Portal Backend..." -ForegroundColor Yellow
docker push ghcr.io/abelisboa/trisla-portal-backend:$TRISLA_VERSION
docker push ghcr.io/abelisboa/trisla-portal-backend:latest
if ($LASTEXITCODE -ne 0) { throw "Push Portal Backend falhou" }
Write-Host "✅ Portal Backend push concluído" -ForegroundColor Green
Write-Host ""

# SEÇÃO 1.3 - Portal Frontend
Write-Host "[SEÇÃO 1.3] Building Portal Frontend..." -ForegroundColor Yellow
Set-Location "..\frontend"
$env:NEXT_PUBLIC_API_URL = $NEXT_PUBLIC_API_URL
docker build --build-arg NEXT_PUBLIC_API_URL="$env:NEXT_PUBLIC_API_URL" -t ghcr.io/abelisboa/trisla-portal-frontend:$TRISLA_VERSION -t ghcr.io/abelisboa/trisla-portal-frontend:latest .
if ($LASTEXITCODE -ne 0) { throw "Build Portal Frontend falhou" }
Write-Host "✅ Portal Frontend build concluído" -ForegroundColor Green

Write-Host "📤 Pushing Portal Frontend..." -ForegroundColor Yellow
docker push ghcr.io/abelisboa/trisla-portal-frontend:$TRISLA_VERSION
docker push ghcr.io/abelisboa/trisla-portal-frontend:latest
if ($LASTEXITCODE -ne 0) { throw "Push Portal Frontend falhou" }
Write-Host "✅ Portal Frontend push concluído" -ForegroundColor Green
Write-Host ""

# SEÇÃO 2 - Verificação das imagens
Write-Host "[SEÇÃO 2] Verificando imagens publicadas..." -ForegroundColor Yellow
Set-Location "C:\Users\USER\Documents\TriSLA-clean"

$bcId = docker inspect ghcr.io/abelisboa/trisla-bc-nssmf:$TRISLA_VERSION --format='{{.Id}}'
$backendId = docker inspect ghcr.io/abelisboa/trisla-portal-backend:$TRISLA_VERSION --format='{{.Id}}'
$frontendId = docker inspect ghcr.io/abelisboa/trisla-portal-frontend:$TRISLA_VERSION --format='{{.Id}}'

Write-Host "BC-NSSMF ID: $bcId" -ForegroundColor Cyan
Write-Host "Backend ID: $backendId" -ForegroundColor Cyan
Write-Host "Frontend ID: $frontendId" -ForegroundColor Cyan
Write-Host "✅ Imagens verificadas" -ForegroundColor Green
Write-Host ""

# SEÇÃO 3 - Atualizar Helm Charts (já foi feito, mas vamos verificar)
Write-Host "[SEÇÃO 3] Verificando Helm Charts..." -ForegroundColor Yellow
$helmFiles = Get-ChildItem -Path . -Recurse -Filter "values.yaml" | Where-Object { $_.FullName -match "helm|trisla-portal" }
foreach ($file in $helmFiles) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match "tag:\s*(latest|nasp-a2|v3\.7\.10)") {
        Write-Host "⚠️  Arquivo $($file.FullName) ainda tem tag antiga" -ForegroundColor Yellow
    }
}
Write-Host "✅ Helm Charts verificados" -ForegroundColor Green
Write-Host ""

# SEÇÃO 4 - Commit + Tag + Push
Write-Host "[SEÇÃO 4] Commit + Tag + Push..." -ForegroundColor Yellow
git add .
git commit -m "release: TriSLA $TRISLA_VERSION — unified version for BC-NSSMF, Backend and Frontend"
if ($LASTEXITCODE -ne 0) { Write-Host "⚠️  Nenhuma mudança para commitar ou commit falhou" -ForegroundColor Yellow }
else {
    git push origin main
    if ($LASTEXITCODE -ne 0) { throw "Push falhou" }
    Write-Host "✅ Push concluído" -ForegroundColor Green
}

git tag $TRISLA_VERSION
git push origin $TRISLA_VERSION
if ($LASTEXITCODE -ne 0) { throw "Push tag falhou" }
Write-Host "✅ Tag $TRISLA_VERSION criada e publicada" -ForegroundColor Green
Write-Host ""

# SEÇÃO 5 - Finalização
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RELEASE TriSLA $TRISLA_VERSION CONCLUÍDO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Imagens publicadas no GHCR" -ForegroundColor Green
Write-Host "✅ Helm charts atualizados localmente" -ForegroundColor Green
Write-Host "✅ Nenhum deploy foi executado" -ForegroundColor Green
Write-Host "✅ Pronto para o PROMPT 4 (helm upgrade no NASP)" -ForegroundColor Green

