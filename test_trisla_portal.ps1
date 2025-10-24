# ===========================================================
# 🔍 TriSLA Portal Verification Script (PowerShell)
# Verifica a comunicação entre UI, API e módulos Core reais
# ===========================================================

$API_URL = "http://localhost:8000"
$UI_URL = "http://localhost:5173"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🔎 TriSLA Portal – Environment Validation" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Checking connections at: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url
    )
    Write-Host "🔗 Testing $Name at $Url ... " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ OK" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed (Status: $($response.StatusCode))" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Failed" -ForegroundColor Red
    }
}

# 1️⃣ API health
Test-Endpoint "TriSLA API health" "$API_URL/api/v1/health"

# 2️⃣ Semantic module
Write-Host "🧠 Testing SEM-NSMF (semantic) → " -NoNewline
try {
    $body = @{descricao="cirurgia remota 5G"} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/semantic" -Method POST -Body $body -ContentType "application/json"
    Write-Host ($response | ConvertTo-Json -Compress) -ForegroundColor Green
} catch {
    Write-Host "❌ Semantic module not responding" -ForegroundColor Red
}

# 3️⃣ AI prediction
Write-Host "🤖 Testing ML-NSMF (AI prediction) → " -NoNewline
try {
    $body = @{slice_type="URLLC"; qos=@{latency=5}} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/predict" -Method POST -Body $body -ContentType "application/json"
    Write-Host ($response | ConvertTo-Json -Compress) -ForegroundColor Green
} catch {
    Write-Host "❌ AI module not responding" -ForegroundColor Red
}

# 4️⃣ Blockchain contract
Write-Host "🔗 Testing BC-NSSMF (blockchain contract) → " -NoNewline
try {
    $body = @{descricao="teste de contrato"} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/contracts" -Method POST -Body $body -ContentType "application/json"
    Write-Host ($response | ConvertTo-Json -Compress) -ForegroundColor Green
} catch {
    Write-Host "❌ Blockchain module not responding" -ForegroundColor Red
}

# 5️⃣ Monitoring metrics
Write-Host "📊 Testing NWDAF-like (monitoring) → " -NoNewline
try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/v1/metrics"
    Write-Host ($response | ConvertTo-Json -Compress) -ForegroundColor Green
} catch {
    Write-Host "❌ Monitoring module not responding" -ForegroundColor Red
}

# 6️⃣ UI check
Test-Endpoint "TriSLA UI" $UI_URL

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "✅ Validation completed!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
