# ============================================
# Script para Build e Push de Imagens Docker
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Build e Push de Imagens Docker                  ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar credenciais GHCR
$ghcrUser = $env:GHCR_USER
$ghcrToken = $env:GHCR_TOKEN

if (-not $ghcrUser -or -not $ghcrToken) {
    Write-Host "❌ Erro: Credenciais GHCR não configuradas"
    Write-Host "   Execute primeiro: .\scripts\configure-ghcr.ps1"
    exit 1
}

# Versão da imagem
$version = "1.0.0"
$registry = "ghcr.io/$ghcrUser"

# Módulos para build
$modules = @(
    @{name="sem-csmf"; path="apps/sem-csmf"},
    @{name="decision-engine"; path="apps/decision-engine"},
    @{name="ml-nsmf"; path="apps/ml_nsmf"},  # Diretório real é ml_nsmf (underscore)
    @{name="bc-nssmf"; path="apps/bc-nssmf"},
    @{name="sla-agent-layer"; path="apps/sla-agent-layer"},
    @{name="nasp-adapter"; path="apps/nasp-adapter"},
    @{name="ui-dashboard"; path="apps/ui-dashboard"}
)

Write-Host "Módulos a serem buildados:"
foreach ($module in $modules) {
    Write-Host "  - $($module.name)"
}
Write-Host ""

$confirm = Read-Host "Deseja continuar? (sim/não)"
if ($confirm -ne "sim") {
    Write-Host "Operação cancelada."
    exit 0
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Iniciando Build e Push de Imagens"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($module in $modules) {
    $imageName = "$registry/trisla-$($module.name):$version"
    $imagePath = $module.path
    
    Write-Host "📦 Buildando $($module.name)..."
    Write-Host "   Imagem: $imageName"
    Write-Host "   Path: $imagePath"
    
    # Verificar se diretório existe
    if (-not (Test-Path $imagePath)) {
        Write-Host "   ⚠️  Diretório não encontrado, pulando..."
        $failCount++
        continue
    }
    
    # Build
    Write-Host "   🔨 Executando build..."
    docker build -t $imageName $imagePath 2>&1 | ForEach-Object {
        if ($_ -match "ERROR|error|failed") {
            Write-Host "   ❌ $_" -ForegroundColor Red
        } else {
            Write-Host "   $_"
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ Build falhou para $($module.name)"
        $failCount++
        continue
    }
    
    Write-Host "   ✅ Build concluído"
    
    # Push
    Write-Host "   📤 Fazendo push..."
    docker push $imageName 2>&1 | ForEach-Object {
        if ($_ -match "ERROR|error|failed") {
            Write-Host "   ❌ $_" -ForegroundColor Red
        } else {
            Write-Host "   $_"
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Push concluído para $($module.name)"
        $successCount++
    } else {
        Write-Host "   ❌ Push falhou para $($module.name)"
        $failCount++
    }
    
    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Resumo"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "  ✅ Sucesso: $successCount"
Write-Host "  ❌ Falhas: $failCount"
Write-Host "  📦 Total: $($modules.Count)"
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "✅ Todas as imagens foram buildadas e enviadas com sucesso!"
    Write-Host ""
    Write-Host "Imagens disponíveis em:"
    Write-Host "  https://github.com/$ghcrUser?tab=packages"
} else {
    Write-Host "⚠️  Algumas imagens falharam. Verifique os erros acima."
}



