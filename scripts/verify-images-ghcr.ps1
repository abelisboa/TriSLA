# ============================================
# Script de Verificação Final de Imagens GHCR
# ============================================
# Valida login, manifestos e tags das imagens TriSLA
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Verificação Final de Imagens GHCR               ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Configuração
$GHCR_USER = $env:GHCR_USER
if (-not $GHCR_USER) {
    $GHCR_USER = "abelisboa"
}

$REGISTRY = "ghcr.io/$GHCR_USER"
$MODULES = @(
    @{name="SEM-CSMF"; image="trisla-sem-csmf"},
    @{name="ML-NSMF"; image="trisla-ml-nsmf"},
    @{name="Decision Engine"; image="trisla-decision-engine"},
    @{name="BC-NSSMF"; image="trisla-bc-nssmf"},
    @{name="SLA-Agent Layer"; image="trisla-sla-agent-layer"},
    @{name="NASP Adapter"; image="trisla-nasp-adapter"},
    @{name="UI Dashboard"; image="trisla-ui-dashboard"}
)

# Resultados
$results = @()
$validCount = 0
$invalidCount = 0

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "1. Verificando Login GHCR"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Verificar se está logado no Docker
$dockerInfoOutput = docker info 2>&1 | Out-String
if ($LASTEXITCODE -ne 0 -and $dockerInfoOutput -match "Cannot connect|error") {
    Write-Host "❌ Docker não está em execução ou não está acessível"
    exit 1
}

# Verificar se está logado no GHCR
$ghcrLoginCheck = docker manifest inspect "$REGISTRY/trisla-sem-csmf:latest" 2>&1
if ($LASTEXITCODE -ne 0 -and $ghcrLoginCheck -match "unauthorized|authentication required") {
    Write-Host "⚠️  Não autenticado no GHCR. Execute:"
    Write-Host "   echo `$env:GHCR_TOKEN | docker login ghcr.io -u $GHCR_USER --password-stdin"
    Write-Host ""
} else {
    Write-Host "✅ Docker está em execução"
    Write-Host "✅ Acesso ao GHCR verificado"
}
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "2. Verificando Manifests das Imagens"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

foreach ($module in $MODULES) {
    $imageRef = "$REGISTRY/$($module.image):latest"
    Write-Host "Verificando $($module.name)... " -NoNewline
    
    # Verificar manifest
    $manifestOutput = docker manifest inspect $imageRef 2>&1
    $manifestExitCode = $LASTEXITCODE
    
    if ($manifestExitCode -eq 0) {
        # Tentar extrair informações do manifest
        try {
            $manifestJson = $manifestOutput | ConvertFrom-Json
            $digest = $manifestJson.config.digest
            $architecture = $manifestJson.architecture
            
            Write-Host "✅" -ForegroundColor Green
            Write-Host "   Imagem: $imageRef"
            Write-Host "   Digest: $digest"
            Write-Host "   Arquitetura: $architecture"
            
            $results += @{
                Module = $module.name
                Image = $imageRef
                Status = "✅ OK"
                Digest = $digest
                Architecture = $architecture
                Tag = "latest"
                Valid = $true
            }
            $validCount++
        } catch {
            Write-Host "✅ (manifest válido, mas não foi possível extrair detalhes)" -ForegroundColor Green
            $results += @{
                Module = $module.name
                Image = $imageRef
                Status = "✅ OK"
                Digest = "N/A"
                Architecture = "N/A"
                Tag = "latest"
                Valid = $true
            }
            $validCount++
        }
    } else {
        Write-Host "❌" -ForegroundColor Red
        Write-Host "   Erro: $($manifestOutput -join ' ')"
        
        $results += @{
            Module = $module.name
            Image = $imageRef
            Status = "❌ FALTANDO"
            Digest = "N/A"
            Architecture = "N/A"
            Tag = "latest"
            Valid = $false
        }
        $invalidCount++
    }
    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "3. Resumo da Verificação"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "  ✅ Imagens válidas: $validCount"
Write-Host "  ❌ Imagens faltando: $invalidCount"
Write-Host "  📦 Total: $($MODULES.Count)"
Write-Host ""

if ($invalidCount -eq 0) {
    Write-Host "✅ Todas as imagens estão válidas e acessíveis no GHCR!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:"
    Write-Host "   - Imagens prontas para deploy no NASP"
    Write-Host "   - Execute: python3 scripts/audit_ghcr_images.py para relatório detalhado"
} else {
    Write-Host "⚠️  Algumas imagens estão faltando ou inacessíveis." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Ação necessária:"
    Write-Host "   - Execute: .\scripts\publish_all_images_ghcr.ps1 para publicar imagens faltantes"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Retornar código de saída
if ($invalidCount -eq 0) {
    exit 0
} else {
    exit 1
}
