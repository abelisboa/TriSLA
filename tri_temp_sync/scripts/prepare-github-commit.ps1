# ============================================
# Script para Preparar Commit para GitHub
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Preparar Commit para GitHub                   ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar se está em repositório git
if (-not (Test-Path ".git")) {
    Write-Host "❌ Erro: Não é um repositório git"
    exit 1
}

# Verificar status
Write-Host "Verificando status do git..."
$status = git status --short

if ($status.Count -eq 0) {
    Write-Host "✅ Nenhuma mudança para commitar"
    exit 0
}

Write-Host ""
Write-Host "Arquivos modificados/novos encontrados:"
Write-Host $status
Write-Host ""

# Verificar se há secrets expostos
Write-Host "Verificando se há secrets expostos..."
$secrets = @(
    "password",
    "secret",
    "token",
    "key",
    ".env",
    "credentials"
)

$hasSecrets = $false
foreach ($file in $status) {
    $fileName = $file.Substring(3)  # Remover status (M, A, etc.)
    foreach ($secret in $secrets) {
        if ($fileName -like "*$secret*" -and $fileName -notlike "*.example*" -and $fileName -notlike "*template*") {
            Write-Host "⚠️  ATENÇÃO: Possível secret em: $fileName"
            $hasSecrets = $true
        }
    }
}

if ($hasSecrets) {
    Write-Host ""
    Write-Host "❌ ERRO: Possíveis secrets encontrados!"
    Write-Host "   Revise os arquivos antes de commitar"
    Write-Host "   Verifique .gitignore para garantir que secrets não sejam commitados"
    exit 1
}

# Verificar .gitignore
Write-Host ""
Write-Host "Verificando .gitignore..."
if (-not (Test-Path ".gitignore")) {
    Write-Host "⚠️  .gitignore não encontrado"
} else {
    Write-Host "✅ .gitignore encontrado"
}

# Mostrar resumo
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Resumo das Mudanças:"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

$modified = ($status | Where-Object { $_ -match "^ M" }).Count
$added = ($status | Where-Object { $_ -match "^A " -or $_ -match "^??" }).Count
$deleted = ($status | Where-Object { $_ -match "^D " }).Count

Write-Host "  Modificados: $modified"
Write-Host "  Adicionados: $added"
Write-Host "  Deletados: $deleted"
Write-Host ""

# Sugerir mensagem de commit
$commitMessage = @"
feat: Implementação completa de produção

- Autenticação JWT habilitada
- HTTPS/TLS configurado (Nginx)
- Retry logic para gRPC e Kafka
- Alertas configurados (12 regras)
- Alertmanager configurado
- Backup/Restore implementado
- Testes de carga implementados
- Troubleshooting completo documentado
- Documentação atualizada
"@

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Mensagem de Commit Sugerida:"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host $commitMessage
Write-Host ""

$confirm = Read-Host "Deseja fazer commit agora? (sim/não)"
if ($confirm -ne "sim") {
    Write-Host "Commit cancelado. Execute manualmente quando estiver pronto."
    exit 0
}

# Fazer commit
Write-Host ""
Write-Host "Adicionando arquivos..."
git add .

Write-Host "Fazendo commit..."
git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Commit realizado com sucesso!"
    Write-Host ""
    Write-Host "Para fazer push:"
    Write-Host "  git push origin main"
    Write-Host ""
    
    $push = Read-Host "Deseja fazer push agora? (sim/não)"
    if ($push -eq "sim") {
        Write-Host "Fazendo push..."
        git push origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Push realizado com sucesso!"
        } else {
            Write-Host ""
            Write-Host "❌ Erro ao fazer push. Verifique credenciais e permissões."
        }
    }
} else {
    Write-Host ""
    Write-Host "❌ Erro ao fazer commit"
    exit 1
}

