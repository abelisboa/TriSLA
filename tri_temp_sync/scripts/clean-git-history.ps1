# Script para remover arquivos temporários do histórico do Git
# ATENÇÃO: Isso reescreve o histórico do Git!

Write-Host "⚠️  ATENÇÃO: Este script irá reescrever o histórico do Git!" -ForegroundColor Yellow
Write-Host "   Certifique-se de fazer backup antes de continuar." -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Deseja continuar? (s/N)"
if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "Operação cancelada." -ForegroundColor Red
    exit 1
}

$tempFiles = @(
    "ACAO_LIMPEZA_IMAGENS.md",
    "COMANDOS_GIT_WSL.md",
    "COMANDOS_NASP_NODE1.md",
    "COMANDOS_RAPIDOS_NASP.md",
    "COMANDO_COMMIT_CORRETO.md",
    "COMANDO_COPIAR_NASP.md",
    "COMANDO_COPIAR_NASP_CORRETO.md",
    "COMANDO_FINAL_PUSH.md",
    "COMANDO_LIMPEZA_KUBE_SYSTEM.md",
    "COMANDO_LIMPEZA_RAPIDA.md",
    "COMANDO_RAPIDO_PUSH.md",
    "COMANDO_VERIFICAR_NASP.md",
    "CORRECAO_DOCKERFILE.md",
    "CORRECAO_TAGS_IMAGENS.md",
    "CORRECOES_WORKFLOWS.md",
    "CORRIGIR_COMMIT.md",
    "ENDPOINTS_DESCOBERTOS_NASP.md",
    "GUIA_GIT_SETUP.md",
    "LIMPEZA_CONCLUIDA.md",
    "PROGRESSO_EXECUCAO.md",
    "PROXIMOS_PASSOS_EXECUTADOS.md",
    "PROXIMOS_PASSOS_FINAIS.md",
    "PROXIMOS_PASSOS_IMEDIATOS.md",
    "PROXIMO_PASSO_AGORA.md",
    "README_DEPLOY_DEVOPS.md",
    "README_GITHUB.md",
    "RESUMO_ALTERACOES.md",
    "RESUMO_CONFIGURACAO_NASP.md",
    "RESUMO_CORRECOES_MODULOS.md",
    "RESUMO_DESCOBERTA_NASP.md",
    "RESUMO_FINAL_CONFIGURACAO.md",
    "RESUMO_LIMPEZA_E_PROXIMOS_PASSOS.md",
    "RESUMO_PROXIMO_PASSO.md",
    "SOLUCAO_ERRO_BUILD.md",
    "TriSLA_PROMPTS_FULL_PACKAGE_V3.zip",
    "VERIFICAR_NASP_RAPIDO.md"
)

$filesToRemove = $tempFiles -join " "

Write-Host "Removendo arquivos do histórico..." -ForegroundColor Cyan

# Usar git filter-branch para remover os arquivos do histórico
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch $filesToRemove" --prune-empty --tag-name-filter cat -- --all

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Arquivos removidos do histórico!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
    Write-Host "   1. Verificar: git log --oneline"
    Write-Host "   2. Forçar push: git push origin main --force --all"
    Write-Host ""
    Write-Host "⚠️  ATENÇÃO: Todos os colaboradores precisarão fazer:" -ForegroundColor Yellow
    Write-Host "   git fetch origin"
    Write-Host "   git reset --hard origin/main"
} else {
    Write-Host "❌ Erro ao remover arquivos do histórico" -ForegroundColor Red
}

