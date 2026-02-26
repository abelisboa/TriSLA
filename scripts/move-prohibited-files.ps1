# ============================================
# Script: Move Prohibited Files from Root (PowerShell)
# ============================================
# Move automaticamente arquivos proibidos da raiz para pastas corretas
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║     Move Prohibited Files - TriSLA                         ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "README.md") -or -not (Test-Path "helm") -or -not (Test-Path "scripts")) {
    Write-Host "❌ Erro: Execute este script no diretório raiz do projeto TriSLA" -ForegroundColor Red
    Write-Host "   Localmente: cd C:\Users\USER\Documents\TriSLA-clean"
    exit 1
}

# Criar diretórios se não existirem
New-Item -ItemType Directory -Path "docs\reports" -Force | Out-Null
New-Item -ItemType Directory -Path "configs" -Force | Out-Null

$MOVED_COUNT = 0
$SKIPPED_COUNT = 0

# Lista de arquivos a mover
$FILES_TO_MOVE = @{
    "AUDIT_REPORT_COMPLETE.md" = "docs\reports\"
    "DEVOPS_AUDIT_REPORT.md" = "docs\reports\"
    "GITHUB_SAFETY_REPORT.md" = "docs\reports\"
    "RELEASE_CHECKLIST_v3.5.0.md" = "docs\reports\"
    "RELEASE_RENAME_REPORT.md" = "docs\reports\"
    "RELEASE_v3.5.0_SUMMARY.md" = "docs\reports\"
    "VALIDATION_REPORT_FINAL.md" = "docs\reports\"
    "ROOT_PROTECTION_REPORT.md" = "docs\reports\"
    "PUSH_COMPLETO_SUCESSO.md" = "docs\reports\"
    "PUSH_LOCAL_WINDOWS.md" = "docs\reports\"
    "PUSH_TO_GITHUB_v3.5.0.md" = "docs\reports\"
    "RELEASE_COMMANDS_v3.5.0.md" = "docs\reports\"
    "docker-compose.yml" = "configs\"
}

Write-Host "🔍 Movendo arquivos proibidos da raiz..." -ForegroundColor Yellow
Write-Host ""

foreach ($file in $FILES_TO_MOVE.Keys) {
    $dest = $FILES_TO_MOVE[$file]
    
    if (Test-Path $file) {
        $destPath = Join-Path $dest $file
        if (Test-Path $destPath) {
            Write-Host "⚠️  $file já existe em $dest (pulando)" -ForegroundColor Yellow
            $SKIPPED_COUNT++
        } else {
            Write-Host "📦 Movendo $file → $dest" -ForegroundColor Green
            Move-Item -Path $file -Destination $dest -Force
            $MOVED_COUNT++
        }
    } else {
        Write-Host "⏭️  $file não encontrado (pulando)" -ForegroundColor Yellow
        $SKIPPED_COUNT++
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "Relatório Final" -ForegroundColor Blue
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""
Write-Host "✅ Arquivos movidos: $MOVED_COUNT" -ForegroundColor Green
Write-Host "⏭️  Arquivos pulados: $SKIPPED_COUNT" -ForegroundColor Yellow
Write-Host ""

if ($MOVED_COUNT -gt 0) {
    Write-Host "✅ Operação concluída com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   1. Verificar estrutura: git status"
    Write-Host "   2. Commit das mudanças: git add . && git commit -m 'chore: move prohibited files from root'"
    Write-Host "   3. Push para GitHub: git push origin main"
} else {
    Write-Host "⚠️  Nenhum arquivo foi movido (todos já estão nos locais corretos ou não existem)" -ForegroundColor Yellow
}

Write-Host ""


