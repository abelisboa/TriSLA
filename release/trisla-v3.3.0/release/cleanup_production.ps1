# TriSLA - Script de Limpeza para Produção
# Remove arquivos e diretórios não essenciais para produção

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "🧹 TriSLA - Limpeza para Produção" -ForegroundColor Yellow
Write-Host "==============================================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n⚠️  MODO DRY-RUN - Nenhum arquivo será removido" -ForegroundColor Yellow
}

# Lista de itens para remover
$itemsToRemove = @(
    @{Path = "trisla_dissertacao_completo"; Type = "Directory"; Reason = "Backup completo da dissertação, não necessário para produção" },
    @{Path = "trisla_dissertacao_completo.tar.gz"; Type = "File"; Reason = "Arquivo de backup" },
    @{Path = "STATE"; Type = "Directory"; Reason = "Conteúdo deve ser consolidado em docs/" },
    @{Path = "kube-prometheus-stack"; Type = "Directory"; Reason = "Duplicado (já existe em ansible/kube-prometheus-stack/)" },
    @{Path = "EXECUTION_GUIDE.md"; Type = "File"; Reason = "Consolidar em docs/README_OPERATIONS_PROD.md" },
    @{Path = "INSTALLATION_NOTES.md"; Type = "File"; Reason = "Consolidar em docs/INSTALLATION_GUIDE.md" },
    @{Path = "README_MONITORING_SETUP.md"; Type = "File"; Reason = "Consolidar em docs/MONITORING_SETUP.md" },
    @{Path = "ansible/logs"; Type = "Directory"; Reason = "Logs temporários" },
    @{Path = "scripts"; Type = "Directory"; Reason = "Scripts de teste (reavaliar antes de remover)" }
)

Write-Host "`n📋 Itens identificados para remoção:" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------------" -ForegroundColor Cyan

$totalSize = 0
$itemsToProcess = @()

foreach ($item in $itemsToRemove) {
    $fullPath = Join-Path (Get-Location) $item.Path
    
    if (Test-Path $fullPath) {
        if ($item.Type -eq "Directory") {
            $size = (Get-ChildItem $fullPath -Recurse -ErrorAction SilentlyContinue | 
                    Measure-Object -Property Length -Sum).Sum / 1MB
        } else {
            $size = (Get-Item $fullPath).Length / 1MB
        }
        
        $totalSize += $size
        
        Write-Host "  ❌ $($item.Path)" -ForegroundColor Red
        Write-Host "     Tipo: $($item.Type) | Tamanho: $([math]::Round($size, 2)) MB" -ForegroundColor Gray
        Write-Host "     Motivo: $($item.Reason)" -ForegroundColor Gray
        Write-Host ""
        
        $itemsToProcess += $item
    } else {
        Write-Host "  ⚠️  $($item.Path) - Não encontrado" -ForegroundColor Yellow
    }
}

Write-Host "--------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "📊 Total a ser liberado: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Green
Write-Host "--------------------------------------------------------------" -ForegroundColor Cyan

if ($itemsToProcess.Count -eq 0) {
    Write-Host "`n✅ Nenhum item para remover encontrado." -ForegroundColor Green
    exit 0
}

if (-not $Force -and -not $DryRun) {
    $confirmation = Read-Host "`n⚠️  Deseja continuar com a remoção? (S/N)"
    if ($confirmation -ne "S" -and $confirmation -ne "s") {
        Write-Host "`n❌ Operação cancelada pelo usuário." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "`n🧹 Iniciando limpeza..." -ForegroundColor Yellow

foreach ($item in $itemsToProcess) {
    $fullPath = Join-Path (Get-Location) $item.Path
    
    if ($DryRun) {
        Write-Host "  [DRY-RUN] Removeria: $($item.Path)" -ForegroundColor Cyan
    } else {
        try {
            if ($item.Type -eq "Directory") {
                Remove-Item -Path $fullPath -Recurse -Force -ErrorAction Stop
                Write-Host "  ✅ Removido: $($item.Path)" -ForegroundColor Green
            } else {
                Remove-Item -Path $fullPath -Force -ErrorAction Stop
                Write-Host "  ✅ Removido: $($item.Path)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ❌ Erro ao remover $($item.Path): $_" -ForegroundColor Red
        }
    }
}

if ($DryRun) {
    Write-Host "`n✅ Modo DRY-RUN concluído. Use sem -DryRun para executar." -ForegroundColor Green
} else {
    Write-Host "`n✅ Limpeza concluída!" -ForegroundColor Green
    Write-Host "📊 Espaço liberado: ~$([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
}

Write-Host "==============================================================" -ForegroundColor Cyan


