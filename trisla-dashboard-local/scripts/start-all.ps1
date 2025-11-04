# Script para iniciar tudo: túnel SSH, backend e frontend
Write-Host " Iniciando TriSLA Dashboard Local..." -ForegroundColor Cyan
Write-Host ""

# 1. Túnel SSH
Write-Host "1 Iniciando túnel SSH..." -ForegroundColor Yellow
$jumpHost = "porvir5g@ppgca.unisinos.br"
$targetHost = "porvir5g@node006"
Start-Process -FilePath "ssh" -ArgumentList "-L", "9090:nasp-prometheus.monitoring.svc.cluster.local:9090", "-J", $jumpHost, $targetHost, "-N" -WindowStyle Hidden
Start-Sleep -Seconds 2
Write-Host "    Túnel SSH iniciado" -ForegroundColor Green
Write-Host ""

# 2. Backend
Write-Host "2 Iniciando backend..." -ForegroundColor Yellow
$backendPath = (Get-Location).Path + "\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; if (Test-Path venv\Scripts\Activate.ps1) { .\venv\Scripts\Activate.ps1 }; python -m uvicorn main:app --reload --port 5000"
Start-Sleep -Seconds 3
Write-Host "    Backend iniciado em http://localhost:5000" -ForegroundColor Green
Write-Host ""

# 3. Frontend
Write-Host "3 Iniciando frontend..." -ForegroundColor Yellow
$frontendPath = (Get-Location).Path + "\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev"
Start-Sleep -Seconds 5
Write-Host "    Frontend iniciado em http://localhost:5173" -ForegroundColor Green
Write-Host ""

Write-Host " Tudo iniciado!" -ForegroundColor Green
Write-Host ""
Write-Host " Acesse: http://localhost:5173" -ForegroundColor Cyan
