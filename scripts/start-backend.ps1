# Script separado para iniciar apenas o backend
# Usa cmd.exe para evitar problemas de política de execução

$backendPath = Resolve-Path "$PSScriptRoot\..\backend"

Write-Host "🔧 Iniciando backend..." -ForegroundColor Cyan
Write-Host "   Caminho: $backendPath" -ForegroundColor Gray
Write-Host ""

# Tenta usar o Python do venv diretamente (sem precisar ativar)
$pythonPath = Join-Path $backendPath "venv\Scripts\python.exe"
if (Test-Path $pythonPath) {
    Write-Host "   Usando Python do venv: $pythonPath" -ForegroundColor Gray
    cmd.exe /c "cd /d `"$backendPath`" && `"$pythonPath`" -m uvicorn main:app --reload --port 5000"
} else {
    Write-Host "   Usando Python do sistema" -ForegroundColor Gray
    cmd.exe /c "cd /d `"$backendPath`" && python -m uvicorn main:app --reload --port 5000"
}
