# Script separado para iniciar apenas o frontend
# Usa cmd.exe para evitar problemas de política de execução

$frontendPath = Resolve-Path "$PSScriptRoot\..\frontend"

Write-Host "🎨 Iniciando frontend..." -ForegroundColor Cyan
Write-Host "   Caminho: $frontendPath" -ForegroundColor Gray
Write-Host ""

# Usa cmd.exe para evitar problemas de política de execução do PowerShell
cmd.exe /c "cd /d `"$frontendPath`" && npm run dev"




