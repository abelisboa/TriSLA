# ============================================
# Script PowerShell de Publicação de Imagens GHCR - TriSLA
# ============================================
# Constrói e publica todas as imagens Docker dos módulos TriSLA
# no GitHub Container Registry (GHCR)
# ============================================
# Uso: $env:GHCR_TOKEN="<token>"; .\scripts\publish_all_images_ghcr.ps1
# ============================================

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR
$GHCR_USER = "abelisboa"
$GHCR_REGISTRY = "ghcr.io"

Write-Host "============================================================"
Write-Host "🚀 Publicação de Imagens TriSLA no GHCR"
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# 1. Verificar Pré-requisitos
# ============================================

Write-Host "1️⃣ Verificando pré-requisitos..." -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker não encontrado. Por favor, instale Docker." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker encontrado" -ForegroundColor Green

# Verificar GHCR_TOKEN
if (-not $env:GHCR_TOKEN) {
    Write-Host "❌ GHCR_TOKEN não definido." -ForegroundColor Red
    Write-Host "   Defina a variável: `$env:GHCR_TOKEN = '<seu_token>'"
    Write-Host "   Ou execute: `$env:GHCR_TOKEN='<token>'; .\scripts\publish_all_images_ghcr.ps1"
    exit 1
}
Write-Host "✅ GHCR_TOKEN definido" -ForegroundColor Green

# Verificar se está na pasta raiz
if (-not (Test-Path "$PROJECT_ROOT\docker-compose.yml")) {
    Write-Host "❌ Não está na pasta raiz do projeto." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Pasta raiz do projeto confirmada" -ForegroundColor Green
Write-Host ""

# ============================================
# 2. Login no GHCR
# ============================================

Write-Host "2️⃣ Fazendo login no GHCR..." -ForegroundColor Cyan
Write-Host ""

$loginProcess = Start-Process -FilePath "docker" -ArgumentList "login", "$GHCR_REGISTRY", "-u", "$GHCR_USER", "--password-stdin" -NoNewWindow -PassThru -RedirectStandardInput ([System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes($env:GHCR_TOKEN)))

$loginProcess.WaitForExit()

if ($loginProcess.ExitCode -eq 0) {
    Write-Host "✅ Login no GHCR realizado com sucesso" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "❌ Falha no login no GHCR. Verifique o token." -ForegroundColor Red
    exit 1
}

# Alternativa: usar echo e pipe
# echo $env:GHCR_TOKEN | docker login $GHCR_REGISTRY -u $GHCR_USER --password-stdin

# ============================================
# 3. Lista de Módulos
# ============================================

$MODULES = @(
    "sem-csmf",
    "ml-nsmf",
    "decision-engine",
    "bc-nssmf",
    "sla-agent-layer",
    "nasp-adapter",
    "ui-dashboard"
)

Write-Host "3️⃣ Módulos a serem publicados:" -ForegroundColor Cyan
foreach ($module in $MODULES) {
    Write-Host "   - $module"
}
Write-Host ""

# ============================================
# 4. Construir e Publicar Imagens
# ============================================

$SUCCESS_COUNT = 0
$FAILED_COUNT = 0
$FAILED_MODULES = @()

foreach ($MODULE in $MODULES) {
    Write-Host "============================================================"
    Write-Host "📦 Construindo e publicando: $MODULE" -ForegroundColor Cyan
    Write-Host "============================================================"
    Write-Host ""
    
    $MODULE_DIR = Join-Path $PROJECT_ROOT "apps\$MODULE"
    $DOCKERFILE = Join-Path $MODULE_DIR "Dockerfile"
    $IMAGE_NAME = "$GHCR_REGISTRY/$GHCR_USER/trisla-$MODULE:latest"
    
    # Verificar se Dockerfile existe
    if (-not (Test-Path $DOCKERFILE)) {
        Write-Host "❌ Dockerfile não encontrado: $DOCKERFILE" -ForegroundColor Red
        $FAILED_COUNT++
        $FAILED_MODULES += $MODULE
        continue
    }
    
    # Verificar se diretório do módulo existe
    if (-not (Test-Path $MODULE_DIR)) {
        Write-Host "❌ Diretório do módulo não encontrado: $MODULE_DIR" -ForegroundColor Red
        $FAILED_COUNT++
        $FAILED_MODULES += $MODULE
        continue
    }
    
    Write-Host "📋 Dockerfile: $DOCKERFILE"
    Write-Host "📋 Imagem: $IMAGE_NAME"
    Write-Host "📋 Contexto: $MODULE_DIR"
    Write-Host ""
    
    # Construir e publicar
    try {
        $buildArgs = @(
            "buildx", "build",
            "-t", $IMAGE_NAME,
            "-f", $DOCKERFILE,
            "--platform", "linux/amd64",
            "--push",
            $MODULE_DIR
        )
        
        $buildProcess = Start-Process -FilePath "docker" -ArgumentList $buildArgs -NoNewWindow -Wait -PassThru
        
        if ($buildProcess.ExitCode -eq 0) {
            Write-Host "✅ Imagem $MODULE publicada com sucesso" -ForegroundColor Green
            Write-Host ""
            $SUCCESS_COUNT++
            
            # Tentar obter digest (pode falhar se imagem ainda não estiver disponível)
            try {
                $digestOutput = docker inspect $IMAGE_NAME --format='{{index .RepoDigests 0}}' 2>&1
                if ($LASTEXITCODE -eq 0 -and $digestOutput -notmatch "Error") {
                    Write-Host "   Digest: $digestOutput" -ForegroundColor Green
                    Write-Host ""
                }
            } catch {
                # Ignorar erro ao obter digest
            }
        } else {
            Write-Host "❌ Falha ao publicar imagem $MODULE" -ForegroundColor Red
            Write-Host ""
            $FAILED_COUNT++
            $FAILED_MODULES += $MODULE
        }
    } catch {
        Write-Host "❌ Erro ao construir/publicar $MODULE : $_" -ForegroundColor Red
        Write-Host ""
        $FAILED_COUNT++
        $FAILED_MODULES += $MODULE
    }
}

# ============================================
# 5. Resumo da Publicação
# ============================================

Write-Host "============================================================"
Write-Host "📊 Resumo da Publicação" -ForegroundColor Cyan
Write-Host "============================================================"
Write-Host ""

Write-Host "✅ Imagens publicadas com sucesso: $SUCCESS_COUNT" -ForegroundColor Green

if ($FAILED_COUNT -gt 0) {
    Write-Host "❌ Imagens com falha: $FAILED_COUNT" -ForegroundColor Red
    Write-Host "   Módulos com falha:" -ForegroundColor Red
    foreach ($module in $FAILED_MODULES) {
        Write-Host "     - $module" -ForegroundColor Red
    }
    Write-Host ""
}

# ============================================
# 6. Validar Imagens Após Push
# ============================================

Write-Host "6️⃣ Validando imagens publicadas..." -ForegroundColor Cyan
Write-Host ""

$AUDIT_SCRIPT = Join-Path $SCRIPT_DIR "audit_ghcr_images.py"
if (Test-Path $AUDIT_SCRIPT) {
    try {
        python3 $AUDIT_SCRIPT
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Auditoria concluída" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Auditoria concluída com avisos" -ForegroundColor Yellow
        }
        Write-Host ""
    } catch {
        Write-Host "⚠️ Erro ao executar auditoria: $_" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "⚠️ Script de auditoria não encontrado: scripts/audit_ghcr_images.py" -ForegroundColor Yellow
    Write-Host ""
}

# ============================================
# 7. Mensagem Final
# ============================================

Write-Host "============================================================"
if ($FAILED_COUNT -eq 0) {
    Write-Host "✅ FINALIZADO — Todas as imagens foram publicadas no GHCR" -ForegroundColor Green
} else {
    Write-Host "⚠️ FINALIZADO — $SUCCESS_COUNT imagens publicadas, $FAILED_COUNT falhas" -ForegroundColor Yellow
}
Write-Host "============================================================"
Write-Host ""

Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Verificar docs/IMAGES_GHCR_MATRIX.md para confirmação"
Write-Host "   2. Testar pull das imagens: docker pull ghcr.io/$GHCR_USER/trisla-<module>:latest"
Write-Host "   3. Configurar secret GHCR no Kubernetes (se ainda não feito)"
Write-Host ""

if ($FAILED_COUNT -gt 0) {
    exit 1
} else {
    exit 0
}

