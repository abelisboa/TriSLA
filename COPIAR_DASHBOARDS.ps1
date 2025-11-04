# Script simples para copiar dashboards via SCP
# Execute: .\COPIAR_DASHBOARDS.ps1

$hostname = "porvir5g@192.168.10.16"
$remotePath = "~/gtp5g/trisla-portal/grafana-dashboards"

Write-Host "📊 Copiando Dashboards para node1" -ForegroundColor Cyan
Write-Host ""

# Criar diretório remoto
Write-Host "Criando diretório remoto..." -ForegroundColor Yellow
ssh $hostname "mkdir -p $remotePath"

# Lista de arquivos
$files = @(
    "trisla-complete-main.json",
    "trisla-slices-management.json",
    "trisla-metrics-detailed.json",
    "trisla-admin-panel.json",
    "trisla-create-slices.json",
    "trisla-centralized-view.json"
)

# Copiar cada arquivo
foreach ($file in $files) {
    $localFile = "grafana-dashboards\$file"
    
    if (Test-Path $localFile) {
        Write-Host "Copiando: $file..." -ForegroundColor Cyan
        scp $localFile "${hostname}:${remotePath}/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $file copiado" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Falha ao copiar $file" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠️  Arquivo não encontrado: $localFile" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "✅ Pronto! Arquivos copiados para node1" -ForegroundColor Green
Write-Host ""
Write-Host "Agora execute no node1:" -ForegroundColor Yellow
Write-Host "  cd ~/gtp5g/trisla-portal" -ForegroundColor Cyan
Write-Host "  ls grafana-dashboards/*.json" -ForegroundColor Cyan
Write-Host "  ./scripts/import_grafana_dashboards_fixed.sh" -ForegroundColor Cyan




