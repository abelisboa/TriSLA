# ============================================
# Script para Configurar SMTP no Alertmanager
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Configurar SMTP no Alertmanager               ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar se config.yml existe
if (-not (Test-Path "monitoring/alertmanager/config.yml")) {
    Write-Host "❌ Erro: config.yml não encontrado"
    exit 1
}

Write-Host "Este script irá configurar as credenciais SMTP no Alertmanager."
Write-Host ""
Write-Host "Provedores SMTP comuns:"
Write-Host "  - Gmail: smtp.gmail.com:587"
Write-Host "  - Outlook: smtp-mail.outlook.com:587"
Write-Host "  - SendGrid: smtp.sendgrid.net:587"
Write-Host "  - Amazon SES: email-smtp.us-east-1.amazonaws.com:587"
Write-Host ""

# Solicitar informações
$smtpHost = Read-Host "SMTP Host (ex: smtp.gmail.com:587)"
$smtpFrom = Read-Host "Email de envio (ex: trisla-alerts@example.com)"
$smtpUser = Read-Host "Usuário SMTP (ex: seu-email@gmail.com)"
$smtpPass = Read-Host "Senha SMTP (será mascarada)" -AsSecureString

# Converter senha
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($smtpPass)
$plainPass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

Write-Host ""
Write-Host "Configurando Alertmanager..."

# Ler config atual
$config = Get-Content "monitoring/alertmanager/config.yml" -Raw

# Substituir valores SMTP
$config = $config -replace "smtp_smarthost: '.*'", "smtp_smarthost: '$smtpHost'"
$config = $config -replace "smtp_from: '.*'", "smtp_from: '$smtpFrom'"
$config = $config -replace "smtp_auth_username: '.*'", "smtp_auth_username: '$smtpUser'"
$config = $config -replace "smtp_auth_password: '\$\{SMTP_PASSWORD\}'", "smtp_auth_password: '$plainPass'"

# Salvar config
$config | Set-Content "monitoring/alertmanager/config.yml" -NoNewline

Write-Host "✅ Configuração SMTP atualizada!"
Write-Host ""
Write-Host "Reiniciando Alertmanager..."
docker compose restart alertmanager

Write-Host ""
Write-Host "✅ Alertmanager reiniciado!"
Write-Host ""
Write-Host "Para testar, você pode:"
Write-Host "  1. Acessar http://localhost:9093"
Write-Host "  2. Verificar logs: docker compose logs alertmanager"
Write-Host "  3. Testar envio de email manualmente"

