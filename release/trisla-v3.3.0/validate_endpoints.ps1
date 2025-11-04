# TriSLA Production Validation Script (PowerShell)
param(
    [string]$NodeIP = "localhost"
)

Write-Host "Validating TriSLA production endpoints..." -ForegroundColor Green

Write-Host "`nTesting SEM-NSMF (Port 8081)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://${NodeIP}:8081/semantic/interpret" -Method POST -ContentType "application/json" -Body '{"descricao": "Criar slice URLLC com prioridade alta e latência 5ms"}'
    Write-Host "✓ SEM-NSMF responding" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ SEM-NSMF endpoint not responding" -ForegroundColor Red
}

Write-Host "`nTesting ML-NSMF (Port 8080)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://${NodeIP}:8080/predict" -Method POST -ContentType "application/json" -Body '{"slice_type": "URLLC", "priority": "alta", "qos": {"latency": 5.0}}'
    Write-Host "✓ ML-NSMF responding" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ ML-NSMF endpoint not responding" -ForegroundColor Red
}

Write-Host "`nTesting BC-NSSMF (Port 8051)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://${NodeIP}:8051/contracts/register" -Method POST -ContentType "application/json" -Body '{"sla_id": "SLA-TEST-001", "slice_type": "URLLC", "decision": "ACCEPT", "compliance": "0.95"}'
    Write-Host "✓ BC-NSSMF responding" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ BC-NSSMF endpoint not responding" -ForegroundColor Red
}

Write-Host "`nTesting NWDAF-like (Port 8090)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://${NodeIP}:8090/metrics" -Method GET
    Write-Host "✓ NWDAF-like responding" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ NWDAF-like endpoint not responding" -ForegroundColor Red
}

Write-Host "`nValidation complete!" -ForegroundColor Green
