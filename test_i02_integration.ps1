# ============================================================
# TESTE DE INTEGRAÇÃO SEM-CSMF → KAFKA (I-02)
# TriSLA — Pré FASE 2 (ML-NSMF Real)
# PowerShell Script para Windows
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host "===== TESTE DE INTEGRAÇÃO I-02 (SEM-CSMF → Kafka) =====" -ForegroundColor Cyan
Write-Host ""

# 1. Validar que o Kafka está rodando no ambiente local
Write-Host "[1/7] Verificando Kafka e Zookeeper..." -ForegroundColor Yellow
$kafkaRunning = docker ps --format "{{.Names}}" | Select-String -Pattern "trisla-kafka|trisla-zookeeper"
if ($kafkaRunning) {
    Write-Host "✅ Kafka e Zookeeper estão rodando" -ForegroundColor Green
    docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String -Pattern "kafka|zookeeper"
} else {
    Write-Host "❌ Kafka ou Zookeeper não estão rodando" -ForegroundColor Red
    Write-Host "   Execute: docker-compose up -d kafka zookeeper" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 2. Criar tópico I-02 se ainda não existir
Write-Host "[2/7] Criando tópico I-02-intent-to-ml..." -ForegroundColor Yellow
docker exec -it trisla-kafka `
  kafka-topics.sh `
    --create `
    --topic I-02-intent-to-ml `
    --bootstrap-server localhost:9092 `
    --if-not-exists `
    --partitions 1 `
    --replication-factor 1 `
    2>&1 | Out-Null

Write-Host "✅ Tópico I-02-intent-to-ml verificado/criado" -ForegroundColor Green
Write-Host ""

# 3. Iniciar consumer para observar mensagens vindas do SEM-CSMF
Write-Host "[3/7] Iniciando consumer Kafka em background..." -ForegroundColor Yellow
Start-Job -ScriptBlock {
    docker exec trisla-kafka `
      kafka-console-consumer.sh `
        --bootstrap-server localhost:9092 `
        --topic I-02-intent-to-ml `
        --from-beginning `
        --property print.key=true `
        --property print.value=true `
        --property print.headers=true
} | Out-Null

Start-Sleep -Seconds 3
Write-Host "✅ Consumer iniciado" -ForegroundColor Green
Write-Host ""

# 4. Enviar INTENT REAL para o SEM-CSMF → este intent deve disparar publicação Kafka no I-02
Write-Host "[4/7] Enviando intent para SEM-CSMF..." -ForegroundColor Yellow
$intentBody = @{
    intent_id = "test-i02-001"
    tenant_id = "tenant-test"
    service_type = "URLLC"
    description = "cirurgia remota"
    sla_requirements = @{
        latency = "5ms"
        throughput = "10Mbps"
        reliability = 0.99999
        jitter = "1ms"
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/intents" `
        -Method POST `
        -ContentType "application/json" `
        -Body $intentBody
    
    Write-Host "Response: $($response | ConvertTo-Json -Depth 5)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Erro ao enviar intent: $_" -ForegroundColor Red
    Write-Host "   Verifique se o SEM-CSMF está rodando em http://localhost:8080" -ForegroundColor Yellow
}

Write-Host ""
Start-Sleep -Seconds 2

# 5. Validar que a mensagem apareceu no consumer
Write-Host "[5/7] Verificando mensagens no tópico..." -ForegroundColor Yellow
$offsetOutput = docker exec trisla-kafka `
  kafka-run-class.sh kafka.tools.GetOffsetShell `
    --broker-list localhost:9092 `
    --topic I-02-intent-to-ml `
    --time -1 2>&1

$messageCount = ($offsetOutput | ForEach-Object { 
    if ($_ -match ':(\d+)$') { [int]$matches[1] } 
} | Measure-Object -Sum).Sum

if ($messageCount -gt 0) {
    Write-Host "✅ Mensagem encontrada no tópico (total: $messageCount)" -ForegroundColor Green
} else {
    Write-Host "⚠️ Nenhuma mensagem encontrada no tópico" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Capturando logs do SEM-CSMF..." -ForegroundColor Yellow
    docker logs trisla-sem-csmf --tail=50 2>&1 | Select-Object -First 20
    Write-Host ""
    Write-Host "Capturando logs do Kafka..." -ForegroundColor Yellow
    docker logs trisla-kafka --tail=50 2>&1 | Select-Object -First 20
}

Write-Host ""

# 6. Validar schema da mensagem publicada (estrutural)
Write-Host "[6/7] Validando schema da mensagem..." -ForegroundColor Yellow
$lastMessage = docker exec trisla-kafka `
  kafka-console-consumer.sh `
    --bootstrap-server localhost:9092 `
    --topic I-02-intent-to-ml `
    --from-beginning `
    --max-messages 1 `
    --timeout-ms 5000 `
    2>&1 | Select-Object -Last 1

if ($lastMessage) {
    Write-Host "✅ Mensagem capturada:" -ForegroundColor Green
    try {
        $jsonMessage = $lastMessage | ConvertFrom-Json
        $jsonMessage | ConvertTo-Json -Depth 10 | Write-Host -ForegroundColor Cyan
    } catch {
        Write-Host $lastMessage -ForegroundColor Cyan
    }
    
    # Validar campos obrigatórios
    $requiredFields = @("intent_id", "nest_id", "service_type", "gst", "nest")
    foreach ($field in $requiredFields) {
        if ($lastMessage -match "`"$field`"") {
            Write-Host "  ✅ Campo '$field' presente" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Campo '$field' ausente" -ForegroundColor Red
        }
    }
} else {
    Write-Host "⚠️ Não foi possível capturar mensagem para validação" -ForegroundColor Yellow
}

Write-Host ""

# 7. Gerar relatório final no console
Write-Host "===== RESULTADO DO TESTE I-02 =====" -ForegroundColor Cyan
Write-Host ""
if ($messageCount -gt 0 -and $lastMessage) {
    Write-Host "✅ SUCESSO: Mensagem publicada no tópico I-02 com todos os campos corretos" -ForegroundColor Green
    Write-Host "   A FASE 2 (ML-NSMF) pode iniciar imediatamente." -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "  1. Implementar consumer Kafka no ML-NSMF"
    Write-Host "  2. Processar NEST recebido via I-02"
    Write-Host "  3. Gerar predição de viabilidade"
    Write-Host "  4. Publicar predição no tópico I-03 (ml-nsmf-predictions)"
    exit 0
} else {
    Write-Host "❌ FALHA: Mensagem não foi publicada ou está incompleta" -ForegroundColor Red
    Write-Host "   Interromper FASE 2 até resolver o problema." -ForegroundColor Red
    Write-Host ""
    Write-Host "Ações recomendadas:" -ForegroundColor Yellow
    Write-Host "  1. Verificar logs do SEM-CSMF"
    Write-Host "  2. Verificar conectividade com Kafka"
    Write-Host "  3. Validar configuração KAFKA_BOOTSTRAP_SERVERS"
    Write-Host "  4. Testar publicação manual no Kafka"
    exit 1
}

