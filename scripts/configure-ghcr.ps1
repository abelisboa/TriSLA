# ============================================
# Script para Configurar Credenciais GHCR
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Configurar Credenciais GHCR                     ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar se variáveis de ambiente já estão configuradas
$ghcrUser = $env:GHCR_USER
$ghcrToken = $env:GHCR_TOKEN

if (-not $ghcrUser -or -not $ghcrToken) {
    Write-Host "Configurando variáveis de ambiente GHCR..."
    
    # Solicitar credenciais
    if (-not $ghcrUser) {
        $ghcrUser = Read-Host "GitHub Username (GHCR_USER)"
    }
    
    if (-not $ghcrToken) {
        $ghcrTokenSecure = Read-Host "GitHub Token (GHCR_TOKEN)" -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ghcrTokenSecure)
        $ghcrToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    }
    
    # Configurar variáveis de ambiente para esta sessão
    $env:GHCR_USER = $ghcrUser
    $env:GHCR_TOKEN = $ghcrToken
    
    Write-Host ""
    Write-Host "✅ Variáveis de ambiente configuradas para esta sessão"
    Write-Host ""
    Write-Host "Para tornar permanente, adicione ao seu perfil PowerShell:"
    Write-Host "  [System.Environment]::SetEnvironmentVariable('GHCR_USER', '$ghcrUser', 'User')"
    Write-Host "  [System.Environment]::SetEnvironmentVariable('GHCR_TOKEN', '<TOKEN>', 'User')"
    Write-Host ""
}

# Fazer login no GHCR
Write-Host "Fazendo login no GitHub Container Registry..."
Write-Host ""

$loginResult = echo $ghcrToken | docker login ghcr.io -u $ghcrUser --password-stdin 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Login no GHCR realizado com sucesso!"
} else {
    Write-Host "❌ Erro ao fazer login no GHCR"
    Write-Host $loginResult
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Credenciais GHCR Configuradas"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "  Username: $ghcrUser"
Write-Host "  Registry: ghcr.io"
Write-Host "  Status: ✅ Logado"
Write-Host ""
Write-Host "Agora você pode fazer build e push de imagens:"
Write-Host "  docker build -t ghcr.io/$ghcrUser/trisla-<modulo>:1.0.0 ./apps/<modulo>"
Write-Host "  docker push ghcr.io/$ghcrUser/trisla-<modulo>:1.0.0"
Write-Host ""



