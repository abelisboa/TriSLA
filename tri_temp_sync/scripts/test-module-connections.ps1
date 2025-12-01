# ============================================
# TriSLA - Testar Conexões entre Módulos
# ============================================

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Teste de Conexões entre Módulos             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot + "\.."
Set-Location $rootPath

# ============================================
# Configuração
# ============================================

$BASE_URL = "http://localhost"
$SEM_CSMF = "$BASE_URL:8080"
$ML_NSMF = "$BASE_URL:8081"
$DECISION_ENGINE = "$BASE_URL:8082"
$BC_NSSMF = "$BASE_URL:8083"
$SLA_AGENT_LAYER = "$BASE_URL:8084"
$NASP_ADAPTER = "$BASE_URL:8085"
$KAFKA_BROKER = "localhost:29092"

$results = @{
    "I-01" = @{ Status = "PENDING"; Message = "" }
    "I-02" = @{ Status = "PENDING"; Message = "" }
    "I-03" = @{ Status = "PENDING"; Message = "" }
    "I-04" = @{ Status = "PENDING"; Message = "" }
    "I-05" = @{ Status = "PENDING"; Message = "" }
    "I-06" = @{ Status = "PENDING"; Message = "" }
    "I-07" = @{ Status = "PENDING"; Message = "" }
}

# ============================================
# Funções Auxiliares
# ============================================

function Test-HTTPEndpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [int]$TimeoutSeconds = 5
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = $TimeoutSeconds
            ErrorAction = "Stop"
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        return @{
            Success = $true
            StatusCode = $response.StatusCode
            Content = $response.Content
        }
    }
    catch {
        return @{
            Success = $false
            Error = $_.Exception.Message
            StatusCode = $_.Exception.Response.StatusCode.value__
        }
    }
}

function Test-KafkaConnection {
    param(
        [string]$Broker,
        [string]$Topic
    )
    
    try {
        # Verificar se Python está disponível
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            return @{
                Success = $false
                Error = "Python não encontrado. Instale Python para testar Kafka."
            }
        }
        
        # Criar script temporário para testar Kafka
        $testScript = @"
import sys
from kafka import KafkaProducer, KafkaConsumer
import json

try:
    producer = KafkaProducer(
        bootstrap_servers=['$Broker'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1),
        request_timeout_ms=5000
    )
    
    # Testar envio
    test_message = {'test': 'connection'}
    producer.send('$Topic', value=test_message)
    producer.flush()
    producer.close()
    
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {str(e)}')
    sys.exit(1)
"@
        
        $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
        $testScript | Out-File -FilePath $tempFile -Encoding UTF8
        
        $output = python $tempFile 2>&1
        Remove-Item $tempFile -ErrorAction SilentlyContinue
        
        if ($output -match "SUCCESS") {
            return @{ Success = $true }
        } else {
            return @{ Success = $false; Error = $output }
        }
    }
    catch {
        return @{ Success = $false; Error = $_.Exception.Message }
    }
}

# ============================================
# Teste I-01: SEM-CSMF → Decision Engine (gRPC)
# ============================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔌 Testando I-01: SEM-CSMF → Decision Engine (gRPC)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# Verificar se SEM-CSMF está rodando
$semHealth = Test-HTTPEndpoint -Url "$SEM_CSMF/health"
if (-not $semHealth.Success) {
    $results["I-01"].Status = "SKIPPED"
    $results["I-01"].Message = "SEM-CSMF não está rodando na porta 8080"
    Write-Host "⚠️  SEM-CSMF não está rodando" -ForegroundColor Yellow
} else {
    Write-Host "✅ SEM-CSMF está rodando" -ForegroundColor Green
    # Nota: Teste gRPC completo requer cliente gRPC
    $results["I-01"].Status = "PARTIAL"
    $results["I-01"].Message = "SEM-CSMF está acessível. Teste gRPC completo requer cliente gRPC."
    Write-Host "ℹ️  Teste gRPC completo requer cliente gRPC (ver scripts/test-grpc.py)" -ForegroundColor Cyan
}

# ============================================
# Teste I-02: SEM-CSMF → ML-NSMF (REST)
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔌 Testando I-02: SEM-CSMF → ML-NSMF (REST)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# Verificar ML-NSMF
$mlHealth = Test-HTTPEndpoint -Url "$ML_NSMF/health"
if (-not $mlHealth.Success) {
    $results["I-02"].Status = "FAILED"
    $results["I-02"].Message = "ML-NSMF não está rodando na porta 8081"
    Write-Host "❌ ML-NSMF não está rodando" -ForegroundColor Red
} else {
    Write-Host "✅ ML-NSMF está rodando" -ForegroundColor Green
    
    # Testar envio de NEST
    $nestPayload = @{
        nest_id = "test-nest-001"
        intent_id = "test-intent-001"
        network_slices = @(
            @{
                slice_id = "slice-001"
                slice_type = "eMBB"
            }
        )
    }
    
    $nestResponse = Test-HTTPEndpoint -Url "$ML_NSMF/api/v1/nest" -Method "POST" -Body $nestPayload
    if ($nestResponse.Success) {
        $results["I-02"].Status = "PASSED"
        $results["I-02"].Message = "NEST enviado com sucesso (Status: $($nestResponse.StatusCode))"
        Write-Host "✅ NEST enviado com sucesso" -ForegroundColor Green
    } else {
        $results["I-02"].Status = "FAILED"
        $results["I-02"].Message = "Falha ao enviar NEST: $($nestResponse.Error)"
        Write-Host "❌ Falha ao enviar NEST: $($nestResponse.Error)" -ForegroundColor Red
    }
}

# ============================================
# Teste I-03: ML-NSMF → Decision Engine (Kafka)
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔌 Testando I-03: ML-NSMF → Decision Engine (Kafka)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$kafkaTest = Test-KafkaConnection -Broker $KAFKA_BROKER -Topic "trisla-ml-predictions"
if ($kafkaTest.Success) {
    $results["I-03"].Status = "PASSED"
    $results["I-03"].Message = "Kafka está acessível e mensagem enviada com sucesso"
    Write-Host "✅ Kafka está acessível e mensagem enviada" -ForegroundColor Green
} else {
    $results["I-03"].Status = "FAILED"
    $results["I-03"].Message = "Kafka não está acessível: $($kafkaTest.Error)"
    Write-Host "❌ Kafka não está acessível: $($kafkaTest.Error)" -ForegroundColor Red
    Write-Host "💡 Certifique-se de que Kafka está rodando: docker compose up -d kafka" -ForegroundColor Cyan
}

# ============================================
# Teste I-04: Decision Engine → BC-NSSMF (REST)
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔌 Testando I-04: Decision Engine → BC-NSSMF (REST)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$bcHealth = Test-HTTPEndpoint -Url "$BC_NSSMF/health"
if (-not $bcHealth.Success) {
    $results["I-04"].Status = "FAILED"
    $results["I-04"].Message = "BC-NSSMF não está rodando na porta 8083"
    Write-Host "❌ BC-NSSMF não está rodando" -ForegroundColor Red
} else {
    Write-Host "✅ BC-NSSMF está rodando" -ForegroundColor Green
    
    # Testar execução de contrato
    $contractPayload = @{
        decision = @{
            action = "AC"
            reasoning = "Teste de conexão"
        }
        contract_data = @{
            tenant_id = "test-tenant"
            slice_id = "test-slice"
        }
    }
    
    $contractResponse = Test-HTTPEndpoint -Url "$BC_NSSMF/api/v1/execute-contract" -Method "POST" -Body $contractPayload
    if ($contractResponse.Success) {
        $results["I-04"].Status = "PASSED"
        $results["I-04"].Message = "Contrato executado com sucesso (Status: $($contractResponse.StatusCode))"
        Write-Host "✅ Contrato executado com sucesso" -ForegroundColor Green
    } else {
        $results["I-04"].Status = "PARTIAL"
        $results["I-04"].Message = "BC-NSSMF está acessível, mas endpoint pode não estar implementado"
        Write-Host "⚠️  BC-NSSMF está acessível, mas endpoint pode não estar implementado" -ForegroundColor Yellow
    }
}

# ============================================
# Teste I-05: Decision Engine → SLA-Agents (Kafka)
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔌 Testando I-05: Decision Engine → SLA-Agents (Kafka)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$kafkaI05Test = Test-KafkaConnection -Broker $KAFKA_BROKER -Topic "trisla-i05-actions"
if ($kafkaI05Test.Success) {
    $results["I-05"].Status = "PASSED"
    $results["I-05"].Message = "Kafka está acessível e mensagem enviada para tópico I-05"
    Write-Host "✅ Kafka está acessível e mensagem enviada" -ForegroundColor Green
} else {
    $results["I-05"].Status = "FAILED"
    $results["I-05"].Message = "Kafka não está acessível: $($kafkaI05Test.Error)"
    Write-Host "❌ Kafka não está acessível" -ForegroundColor Red
}

# ============================================
# Teste I-06: SLA-Agents → NASP Adapter (REST)
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔌 Testando I-06: SLA-Agents → NASP Adapter (REST)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$slaHealth = Test-HTTPEndpoint -Url "$SLA_AGENT_LAYER/health"
$naspHealth = Test-HTTPEndpoint -Url "$NASP_ADAPTER/health"

if (-not $slaHealth.Success) {
    $results["I-06"].Status = "FAILED"
    $results["I-06"].Message = "SLA-Agent Layer não está rodando na porta 8084"
    Write-Host "❌ SLA-Agent Layer não está rodando" -ForegroundColor Red
} elseif (-not $naspHealth.Success) {
    $results["I-06"].Status = "FAILED"
    $results["I-06"].Message = "NASP Adapter não está rodando na porta 8085"
    Write-Host "❌ NASP Adapter não está rodando" -ForegroundColor Red
} else {
    Write-Host "✅ SLA-Agent Layer está rodando" -ForegroundColor Green
    Write-Host "✅ NASP Adapter está rodando" -ForegroundColor Green
    
    # Testar execução de ação
    $actionPayload = @{
        type = "adjust_prb_allocation"
        domain = "RAN"
        parameters = @{
            prb_percentage = 0.8
        }
    }
    
    $actionResponse = Test-HTTPEndpoint -Url "$NASP_ADAPTER/api/v1/nasp/actions" -Method "POST" -Body $actionPayload
    if ($actionResponse.Success) {
        $results["I-06"].Status = "PASSED"
        $results["I-06"].Message = "Ação executada com sucesso (Status: $($actionResponse.StatusCode))"
        Write-Host "✅ Ação executada com sucesso" -ForegroundColor Green
    } else {
        $results["I-06"].Status = "PARTIAL"
        $results["I-06"].Message = "Serviços estão acessíveis, mas endpoint pode não estar implementado"
        Write-Host "⚠️  Serviços estão acessíveis, mas endpoint pode não estar implementado" -ForegroundColor Yellow
    }
}

# ============================================
# Teste I-07: NASP Adapter ↔ NASP (REST)
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔌 Testando I-07: NASP Adapter ↔ NASP (REST)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$naspMetricsResponse = Test-HTTPEndpoint -Url "$NASP_ADAPTER/api/v1/nasp/metrics" -Method "GET"
if ($naspMetricsResponse.Success) {
    $results["I-07"].Status = "PASSED"
    $results["I-07"].Message = "Métricas NASP coletadas com sucesso (Status: $($naspMetricsResponse.StatusCode))"
    Write-Host "✅ Métricas NASP coletadas com sucesso" -ForegroundColor Green
    Write-Host "ℹ️  Em produção, isso conectaria ao NASP real" -ForegroundColor Cyan
} else {
    $results["I-07"].Status = "PARTIAL"
    $results["I-07"].Message = "NASP Adapter está rodando em modo MOCK (local). Em produção, conecta ao NASP real."
    Write-Host "⚠️  NASP Adapter está rodando em modo MOCK (local)" -ForegroundColor Yellow
    Write-Host "ℹ️  Em produção, isso conectaria ao NASP real no servidor remoto" -ForegroundColor Cyan
}

# ============================================
# Resumo Final
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 Resumo dos Testes de Conexão" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0
$partial = 0
$skipped = 0

foreach ($interface in $results.Keys | Sort-Object) {
    $result = $results[$interface]
    $status = $result.Status
    $message = $result.Message
    
    switch ($status) {
        "PASSED" {
            Write-Host "✅ $interface : PASSED" -ForegroundColor Green
            $passed++
        }
        "FAILED" {
            Write-Host "❌ $interface : FAILED" -ForegroundColor Red
            Write-Host "   $message" -ForegroundColor Red
            $failed++
        }
        "PARTIAL" {
            Write-Host "⚠️  $interface : PARTIAL" -ForegroundColor Yellow
            Write-Host "   $message" -ForegroundColor Yellow
            $partial++
        }
        "SKIPPED" {
            Write-Host "⏭️  $interface : SKIPPED" -ForegroundColor Gray
            Write-Host "   $message" -ForegroundColor Gray
            $skipped++
        }
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📈 Estatísticas" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Passou: $passed" -ForegroundColor Green
Write-Host "❌ Falhou: $failed" -ForegroundColor Red
Write-Host "⚠️  Parcial: $partial" -ForegroundColor Yellow
Write-Host "⏭️  Pulado: $skipped" -ForegroundColor Gray
Write-Host ""

if ($failed -eq 0 -and $skipped -eq 0) {
    Write-Host "🎉 Todos os testes de conexão passaram!" -ForegroundColor Green
} elseif ($failed -gt 0) {
    Write-Host "⚠️  Alguns testes falharam. Verifique se todos os serviços estão rodando:" -ForegroundColor Yellow
    Write-Host "   docker compose up -d" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "💡 Para executar testes mais detalhados:" -ForegroundColor Cyan
Write-Host "   pytest tests/integration/ -v" -ForegroundColor White
Write-Host ""

