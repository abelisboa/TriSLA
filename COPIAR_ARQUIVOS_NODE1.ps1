# Script PowerShell para copiar arquivos do dashboard customizado para node1

$Node1Host = "porvir5g@192.168.10.16"
$BasePath = "~/gtp5g/trisla-portal"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📤 Copiando Arquivos Dashboard Customizado" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Arquivos para copiar
$filesToCopy = @(
    @{
        Local = "trisla-portal\apps\api\prometheus.py"
        Remote = "$BasePath/apps/api/prometheus.py"
        Description = "Backend API Prometheus"
    },
    @{
        Local = "trisla-portal\apps\ui\src\pages\DashboardComplete.jsx"
        Remote = "$BasePath/apps/ui/src/pages/DashboardComplete.jsx"
        Description = "Dashboard Completo"
    },
    @{
        Local = "trisla-portal\apps\ui\src\pages\SlicesManagement.jsx"
        Remote = "$BasePath/apps/ui/src/pages/SlicesManagement.jsx"
        Description = "Gestão de Slices"
    }
)

$SuccessCount = 0
$FailedCount = 0

foreach ($file in $filesToCopy) {
    if (Test-Path $file.Local) {
        Write-Host "📤 Copiando: $($file.Description)" -ForegroundColor Yellow
        Write-Host "   De: $($file.Local)" -ForegroundColor Gray
        Write-Host "   Para: $($file.Remote)" -ForegroundColor Gray
        
        # Criar diretório remoto se necessário
        $RemoteDir = Split-Path $file.Remote -Parent
        ssh "$Node1Host" "mkdir -p $RemoteDir" 2>&1 | Out-Null
        
        # Copiar arquivo
        scp "$($file.Local)" "${Node1Host}:$($file.Remote)" 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Copiado com sucesso" -ForegroundColor Green
            $SuccessCount++
        } else {
            Write-Host "   ❌ Falha ao copiar" -ForegroundColor Red
            $FailedCount++
        }
        Write-Host ""
    } else {
        Write-Host "⚠️  Arquivo não encontrado: $($file.Local)" -ForegroundColor Yellow
        $FailedCount++
        Write-Host ""
    }
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 RESUMO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Copiados: $SuccessCount" -ForegroundColor Green
Write-Host "❌ Falhados: $FailedCount" -ForegroundColor $(if ($FailedCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($SuccessCount -gt 0) {
    Write-Host "✅ Próximos passos no node1:" -ForegroundColor Green
    Write-Host "   1. Verificar arquivos: ls -lh ~/gtp5g/trisla-portal/apps/api/prometheus.py" -ForegroundColor Cyan
    Write-Host "   2. Verificar se router está integrado no main.py" -ForegroundColor Cyan
    Write-Host "   3. Reiniciar services do TriSLA Portal" -ForegroundColor Cyan
    Write-Host "   4. Testar: curl http://localhost:8000/prometheus/health" -ForegroundColor Cyan
    Write-Host ""
}




