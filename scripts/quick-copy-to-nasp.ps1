# ============================================
# Script PowerShell para Copiar para NASP
# ============================================
# Para Windows PowerShell
# ============================================

$PPGCA_HOST = "ppgca.unisinos.br"
$PPGCA_USER = "porvir5g"
$NODE1_HOST = "node006"
$NODE1_USER = "porvir5g"
$NODE1_PATH = "~/gtp5g"

$FILE = $args[0]
if (-not $FILE) {
    $FILE = "scripts/discover-nasp-endpoints.sh"
}

Write-Host "📋 Copiando arquivo para o NASP..." -ForegroundColor Cyan
Write-Host "Arquivo: $FILE" -ForegroundColor Yellow
Write-Host ""

Write-Host "1️⃣ Copiando para ppgca..." -ForegroundColor Cyan
scp $FILE "${PPGCA_USER}@${PPGCA_HOST}:~/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Arquivo copiado para ppgca" -ForegroundColor Green
    Write-Host ""
    Write-Host "2️⃣ Próximos passos:" -ForegroundColor Cyan
    Write-Host "   ssh ${PPGCA_USER}@${PPGCA_HOST}" -ForegroundColor White
    Write-Host "   scp $(Split-Path -Leaf $FILE) ${NODE1_USER}@${NODE1_HOST}:${NODE1_PATH}/" -ForegroundColor White
    Write-Host "   ssh ${NODE1_HOST}" -ForegroundColor White
    Write-Host "   cd ${NODE1_PATH}" -ForegroundColor White
    Write-Host "   chmod +x $(Split-Path -Leaf $FILE)" -ForegroundColor White
    Write-Host "   ./$(Split-Path -Leaf $FILE)" -ForegroundColor White
} else {
    Write-Host "❌ Erro ao copiar para ppgca" -ForegroundColor Red
    exit 1
}

