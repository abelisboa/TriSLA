# ============================================
# TriSLA - Build e Push GHCR v3.7.7
# ============================================

$ErrorActionPreference = "Stop"
$VERSION = "v3.7.7"
$GITHUB_USERNAME = if ($env:GITHUB_USERNAME) { $env:GITHUB_USERNAME } else { "abelisboa" }
$GHCR_NAMESPACE = "ghcr.io/$GITHUB_USERNAME"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Build e Push GHCR $VERSION                     ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker não encontrado. Instale o Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar GHCR_TOKEN
if (-not $env:GHCR_TOKEN) {
    Write-Host "❌ Variável GHCR_TOKEN não definida." -ForegroundColor Red
    Write-Host "   Execute primeiro: `$env:GHCR_TOKEN = 'seu_token_aqui'" -ForegroundColor Yellow
    exit 1
}

# Mapeamento: nome do serviço -> diretório real
$serviceDirs = @{
    "bc-nssmf" = "bc-nssmf"
    "ml-nsmf" = "ml-nsmf"  # Diretório real é ml-nsmf (hífen)
    "sem-csmf" = "sem-csmf"
    "decision-engine" = "decision-engine"
    "sla-agent-layer" = "sla-agent-layer"
    "ui-dashboard" = "ui-dashboard"
    "nasp-adapter" = "nasp-adapter"
}

$services = @(
    "bc-nssmf",
    "ml-nsmf",
    "sem-csmf",
    "decision-engine",
    "sla-agent-layer",
    "ui-dashboard",
    "nasp-adapter"
)

Write-Host "🔐 Efetuando login no GHCR..." -ForegroundColor Cyan
$loginOutput = echo $env:GHCR_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer login no GHCR" -ForegroundColor Red
    Write-Host $loginOutput
    exit 1
}
Write-Host "✅ Login realizado com sucesso" -ForegroundColor Green
Write-Host ""

# Criar diretório de logs
$logDir = "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$buildLog = "$logDir/build_and_push_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

Write-Host "📦 Iniciando build e push de imagens..." -ForegroundColor Cyan
Write-Host "   Log: $buildLog" -ForegroundColor Gray
Write-Host ""

$successCount = 0
$failCount = 0
$failedServices = @()

foreach ($service in $services) {
    $serviceDirName = if ($serviceDirs.ContainsKey($service)) { $serviceDirs[$service] } else { $service }
    $serviceDir = "apps/$serviceDirName"
    
    if (-not (Test-Path $serviceDir)) {
        Write-Host "⚠️ Diretório $serviceDir não encontrado. Pulando..." -ForegroundColor Yellow
        continue
    }
    
    $imageName = "$GHCR_NAMESPACE/trisla-${service}:$VERSION"
    
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "📦 Construindo $imageName..." -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    
    # Build da imagem
    Write-Host "   Executando docker build..." -ForegroundColor Gray
    $buildOutput = docker build -t $imageName "./$serviceDir" 2>&1 | Tee-Object -FilePath $buildLog -Append
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Build concluído: $imageName" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Erro no build: $imageName" -ForegroundColor Red
        Write-Host "   Verifique o log: $buildLog" -ForegroundColor Yellow
        $failCount++
        $failedServices += $service
        continue
    }
    
    Write-Host "   🚀 Enviando $imageName para GHCR..." -ForegroundColor Gray
    
    # Push da imagem
    $pushOutput = docker push $imageName 2>&1 | Tee-Object -FilePath $buildLog -Append
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Push concluído: $imageName" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "   ❌ Erro no push: $imageName" -ForegroundColor Red
        Write-Host "   Verifique o log: $buildLog" -ForegroundColor Yellow
        $failCount++
        $failedServices += $service
    }
    
    Write-Host ""
}

Write-Host "==========================================" -ForegroundColor Cyan
if ($failCount -eq 0) {
    Write-Host "✅ Todas as imagens foram construídas e enviadas com sucesso!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Algumas imagens falharam: $failCount de $($services.Count)" -ForegroundColor Yellow
}
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 Resumo:" -ForegroundColor Cyan
Write-Host "   ✅ Sucesso: $successCount" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "   ❌ Falhas: $failCount" -ForegroundColor Red
    Write-Host "   Serviços com falha:" -ForegroundColor Yellow
    foreach ($failed in $failedServices) {
        Write-Host "     - $failed" -ForegroundColor Yellow
    }
}
Write-Host ""
Write-Host "📝 Log completo: $buildLog" -ForegroundColor Gray
Write-Host ""

# Listar imagens publicadas
Write-Host "📋 Imagens publicadas com tag ${VERSION}:" -ForegroundColor Cyan
foreach ($service in $services) {
    if (-not ($failedServices -contains $service)) {
        $imageName = "$GHCR_NAMESPACE/trisla-${service}:$VERSION"
        Write-Host "   ✅ $imageName" -ForegroundColor Green
    }
}
Write-Host ""

