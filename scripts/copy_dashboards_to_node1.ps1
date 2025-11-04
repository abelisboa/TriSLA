# Script PowerShell para copiar dashboards para node1

$Node1Host = "porvir5g@192.168.10.16"
$Node1Path = "~/gtp5g/trisla-portal/grafana-dashboards"
$LocalPath = "grafana-dashboards"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 Copiando Dashboards para node1" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se diretório local existe
if (-not (Test-Path $LocalPath)) {
    Write-Host "❌ Diretório local não encontrado: $LocalPath" -ForegroundColor Red
    exit 1
}

# Listar arquivos JSON
$JsonFiles = Get-ChildItem "$LocalPath\*.json"
Write-Host "📁 Arquivos encontrados localmente:" -ForegroundColor Yellow
foreach ($file in $JsonFiles) {
    Write-Host "   • $($file.Name) ($([math]::Round($file.Length/1KB, 2)) KB)" -ForegroundColor Gray
}
Write-Host ""

# Verificar conectividade SSH
Write-Host "🔍 Verificando conectividade SSH..." -ForegroundColor Yellow
try {
    $TestConnection = ssh -o ConnectTimeout=5 -o BatchMode=yes "$Node1Host" "echo 'OK'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Conexão SSH OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Conexão SSH pode precisar de senha" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Verificando conexão SSH..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📤 Copiando arquivos para node1..." -ForegroundColor Yellow
Write-Host "   Destino: ${Node1Host}:${Node1Path}" -ForegroundColor Gray
Write-Host ""

$SuccessCount = 0
$FailedCount = 0

foreach ($file in $JsonFiles) {
    $FileName = $file.Name
    Write-Host "   Copiando: $FileName..." -ForegroundColor Cyan
    
    try {
        # Criar diretório remoto se não existir
        ssh "$Node1Host" "mkdir -p $Node1Path" 2>&1 | Out-Null
        
        # Copiar arquivo
        scp "$($file.FullName)" "${Node1Host}:${Node1Path}/" 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $FileName copiado com sucesso" -ForegroundColor Green
            $SuccessCount++
        } else {
            Write-Host "   ❌ Falha ao copiar $FileName" -ForegroundColor Red
            $FailedCount++
        }
    } catch {
        Write-Host "   ❌ Erro ao copiar $FileName : $_" -ForegroundColor Red
        $FailedCount++
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 RESUMO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Copiados com sucesso: $SuccessCount" -ForegroundColor Green
if ($FailedCount -gt 0) {
    Write-Host "❌ Falhados: $FailedCount" -ForegroundColor Red
}
Write-Host ""

# Verificar arquivos no node1
Write-Host "🔍 Verificando arquivos no node1..." -ForegroundColor Yellow
ssh "$Node1Host" "ls -lh $Node1Path/*.json 2>&1" | ForEach-Object {
    Write-Host "   $_" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ Pronto! Agora execute no node1:" -ForegroundColor Green
Write-Host "   cd ~/gtp5g/trisla-portal" -ForegroundColor Cyan
Write-Host "   ./scripts/import_grafana_dashboards_fixed.sh" -ForegroundColor Cyan
Write-Host ""
