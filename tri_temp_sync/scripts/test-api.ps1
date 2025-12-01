# Script de Teste da API TriSLA
# Testa persistência, gRPC e segurança

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Teste de API (Persistência, gRPC, Segurança)  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se serviços estão rodando
Write-Host "1. Verificando serviços..." -ForegroundColor Yellow
$semCsmfStatus = docker compose ps sem-csmf --format json | ConvertFrom-Json
$decisionEngineStatus = docker compose ps decision-engine --format json | ConvertFrom-Json

if ($semCsmfStatus.State -ne "running") {
    Write-Host "❌ SEM-CSMF não está rodando" -ForegroundColor Red
    exit 1
}
if ($decisionEngineStatus.State -ne "running") {
    Write-Host "❌ Decision Engine não está rodando" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Serviços estão rodando" -ForegroundColor Green
Write-Host ""

# 2. Testar health check
Write-Host "2. Testando health check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET -ErrorAction Stop
    Write-Host "✅ SEM-CSMF está saudável: $($healthResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao conectar ao SEM-CSMF: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. Criar intent (testa persistência)
Write-Host "3. Criando intent (testa persistência no banco)..." -ForegroundColor Yellow
$intentId = "test-$(Get-Date -Format 'yyyyMMddHHmmss')"
$intentBody = @{
    intent_id = $intentId
    service_type = "eMBB"
    sla_requirements = @{
        latency = "10ms"
        throughput = "100Mbps"
    }
} | ConvertTo-Json

try {
    $intentResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/intents" `
        -Method POST `
        -Body $intentBody `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "✅ Intent criado com sucesso!" -ForegroundColor Green
    Write-Host "   Intent ID: $($intentResponse.intent_id)" -ForegroundColor White
    Write-Host "   Status: $($intentResponse.status)" -ForegroundColor White
    Write-Host "   NEST ID: $($intentResponse.nest_id)" -ForegroundColor White
    Write-Host "   Mensagem: $($intentResponse.message)" -ForegroundColor White
} catch {
    Write-Host "❌ Erro ao criar intent: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Resposta: $responseBody" -ForegroundColor Red
    }
    exit 1
}
Write-Host ""

# 4. Verificar no banco de dados
Write-Host "4. Verificando persistência no banco..." -ForegroundColor Yellow
try {
    $dbQuery = "SELECT intent_id, service_type, created_at FROM intents WHERE intent_id = '$intentId';"
    $dbResult = docker compose exec -T postgres psql -U trisla -d trisla -c $dbQuery 2>&1
    
    if ($dbResult -match $intentId) {
        Write-Host "✅ Intent encontrado no banco de dados!" -ForegroundColor Green
        Write-Host $dbResult -ForegroundColor White
    } else {
        Write-Host "⚠️  Intent não encontrado no banco (tabela pode não ter sido criada ainda)" -ForegroundColor Yellow
        Write-Host "   Resultado: $dbResult" -ForegroundColor White
    }
} catch {
    Write-Host "⚠️  Erro ao consultar banco: $_" -ForegroundColor Yellow
}
Write-Host ""

# 5. Verificar NEST criado
Write-Host "5. Verificando NEST criado..." -ForegroundColor Yellow
try {
    $nestId = $intentResponse.nest_id
    $nestResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/nests/$nestId" `
        -Method GET `
        -ErrorAction Stop
    
    Write-Host "✅ NEST encontrado!" -ForegroundColor Green
    Write-Host "   NEST ID: $($nestResponse.nest_id)" -ForegroundColor White
    Write-Host "   Status: $($nestResponse.status)" -ForegroundColor White
    Write-Host "   Slices: $($nestResponse.network_slices.Count)" -ForegroundColor White
} catch {
    Write-Host "❌ Erro ao buscar NEST: $_" -ForegroundColor Red
}
Write-Host ""

# 6. Verificar logs do gRPC
Write-Host "6. Verificando comunicação gRPC..." -ForegroundColor Yellow
$grpcLogs = docker compose logs decision-engine --tail 20 2>&1 | Select-String -Pattern "grpc|gRPC|I-01|NESTMetadata" -CaseSensitive:$false
if ($grpcLogs) {
    Write-Host "✅ Logs de gRPC encontrados:" -ForegroundColor Green
    $grpcLogs | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
} else {
    Write-Host "⚠️  Nenhum log de gRPC encontrado (pode ser normal se não houver comunicação ainda)" -ForegroundColor Yellow
}
Write-Host ""

# 7. Testar rate limiting (se habilitado)
Write-Host "7. Testando rate limiting..." -ForegroundColor Yellow
$rateLimitHeaders = @{}
try {
    $testResponse = Invoke-WebRequest -Uri "http://localhost:8080/health" -Method GET -ErrorAction Stop
    if ($testResponse.Headers['X-RateLimit-Limit']) {
        Write-Host "✅ Rate limiting está ativo!" -ForegroundColor Green
        Write-Host "   Limite: $($testResponse.Headers['X-RateLimit-Limit'])" -ForegroundColor White
        Write-Host "   Restante: $($testResponse.Headers['X-RateLimit-Remaining'])" -ForegroundColor White
    } else {
        Write-Host "⚠️  Rate limiting não está ativo ou não retornou headers" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Erro ao testar rate limiting: $_" -ForegroundColor Yellow
}
Write-Host ""

# 8. Verificar security headers
Write-Host "8. Verificando security headers..." -ForegroundColor Yellow
try {
    $securityResponse = Invoke-WebRequest -Uri "http://localhost:8080/health" -Method GET -ErrorAction Stop
    $securityHeaders = @('X-Content-Type-Options', 'X-Frame-Options', 'X-XSS-Protection')
    $foundHeaders = 0
    
    foreach ($header in $securityHeaders) {
        if ($securityResponse.Headers[$header]) {
            Write-Host "   ✅ $header : $($securityResponse.Headers[$header])" -ForegroundColor Green
            $foundHeaders++
        }
    }
    
    if ($foundHeaders -eq $securityHeaders.Count) {
        Write-Host "✅ Todos os security headers estão presentes!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Alguns security headers estão faltando" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Erro ao verificar security headers: $_" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Teste Concluído                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

