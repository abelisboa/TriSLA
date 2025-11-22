# Script PowerShell para iniciar ambiente E2E local completo do TriSLA
# Inicia infraestrutura, NASP Adapter e módulos TriSLA na ordem correta

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

Set-Location $PROJECT_ROOT

Write-Host "============================================================"
Write-Host "🚀 Iniciando Ambiente E2E Local - TriSLA"
Write-Host "============================================================" -ForegroundColor Cyan

# Função para verificar saúde de serviço
function Check-Health {
    param(
        [string]$ServiceName,
        [string]$Url,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "⏳ Aguardando $ServiceName ficar saudável..." -ForegroundColor Yellow
    
    $attempt = 0
    while ($attempt -lt $MaxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $ServiceName está saudável" -ForegroundColor Green
                return $true
            }
        } catch {
            # Continuar tentando
        }
        $attempt++
        Start-Sleep -Seconds 2
    }
    
    Write-Host "❌ $ServiceName não ficou saudável após $MaxAttempts tentativas" -ForegroundColor Red
    return $false
}

# 1. Subir infraestrutura básica
Write-Host ""
Write-Host "============================================================"
Write-Host "1️⃣ Subindo infraestrutura básica..."
Write-Host "============================================================" -ForegroundColor Cyan

docker compose up -d zookeeper kafka postgres

Write-Host "⏳ Aguardando Zookeeper e Kafka..."
Start-Sleep -Seconds 10

# Verificar Kafka
try {
    docker exec trisla-kafka kafka-broker-api-versions --bootstrap-server localhost:9092 2>&1 | Out-Null
    Write-Host "✅ Kafka está pronto" -ForegroundColor Green
} catch {
    Write-Host "❌ Kafka não está pronto" -ForegroundColor Red
    exit 1
}

# 2. Subir observabilidade
Write-Host ""
Write-Host "============================================================"
Write-Host "2️⃣ Subindo stack de observabilidade..."
Write-Host "============================================================" -ForegroundColor Cyan

docker compose up -d prometheus grafana otlp-collector

# Verificar Prometheus
Check-Health "Prometheus" "http://localhost:9090/-/healthy" 15 | Out-Null

# Verificar Grafana
Check-Health "Grafana" "http://localhost:3000/api/health" 15 | Out-Null

# 3. Subir Besu (Blockchain)
Write-Host ""
Write-Host "============================================================"
Write-Host "3️⃣ Subindo Besu (Ethereum Permissionado)..."
Write-Host "============================================================" -ForegroundColor Cyan

docker compose up -d besu-dev

# Verificar Besu
Check-Health "Besu" "http://localhost:8545" 20 | Out-Null

# Aguardar Besu inicializar completamente
Write-Host "⏳ Aguardando Besu inicializar completamente..."
Start-Sleep -Seconds 15

# Verificar se Besu está respondendo
try {
    $besuResponse = Invoke-WebRequest -Uri "http://localhost:8545" `
        -Method Post `
        -ContentType "application/json" `
        -Body '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' `
        -UseBasicParsing `
        -ErrorAction SilentlyContinue
    
    if ($besuResponse.StatusCode -eq 200) {
        Write-Host "✅ Besu está respondendo" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Besu pode não estar totalmente pronto, mas continuando..." -ForegroundColor Yellow
}

# 4. Subir NASP Adapter
Write-Host ""
Write-Host "============================================================"
Write-Host "4️⃣ Subindo NASP Adapter..."
Write-Host "============================================================" -ForegroundColor Cyan

docker compose up -d nasp-adapter mock-nasp-ran mock-nasp-transport mock-nasp-core

# Verificar NASP Adapter
Check-Health "NASP Adapter" "http://localhost:8085/health" 15 | Out-Null

# 5. Subir módulos TriSLA na ordem correta
Write-Host ""
Write-Host "============================================================"
Write-Host "5️⃣ Subindo módulos TriSLA..."
Write-Host "============================================================" -ForegroundColor Cyan

# 1. SEM-CSMF
Write-Host "📦 Iniciando SEM-CSMF..."
docker compose up -d sem-csmf
Check-Health "SEM-CSMF" "http://localhost:8080/health" 20 | Out-Null

# 2. ML-NSMF
Write-Host "📦 Iniciando ML-NSMF..."
docker compose up -d ml-nsmf
Check-Health "ML-NSMF" "http://localhost:8081/health" 20 | Out-Null

# 3. Decision Engine
Write-Host "📦 Iniciando Decision Engine..."
docker compose up -d decision-engine
Check-Health "Decision Engine" "http://localhost:8082/health" 20 | Out-Null

# 4. BC-NSSMF
Write-Host "📦 Iniciando BC-NSSMF..."
docker compose up -d bc-nssmf
Check-Health "BC-NSSMF" "http://localhost:8083/health" 20 | Out-Null

# 5. SLA-Agent Layer
Write-Host "📦 Iniciando SLA-Agent Layer..."
docker compose up -d sla-agent-layer
Check-Health "SLA-Agent Layer" "http://localhost:8084/health" 20 | Out-Null

# 6. Criar tópicos Kafka necessários
Write-Host ""
Write-Host "============================================================"
Write-Host "6️⃣ Criando tópicos Kafka..."
Write-Host "============================================================" -ForegroundColor Cyan

$KAFKA_TOPICS = @(
    "I-02-intent-to-ml",
    "I-03-ml-predictions",
    "trisla-i04-decisions",
    "trisla-i05-actions",
    "trisla-i06-agent-events",
    "trisla-i07-agent-actions"
)

foreach ($topic in $KAFKA_TOPICS) {
    try {
        docker exec trisla-kafka kafka-topics --create `
            --topic $topic `
            --bootstrap-server localhost:9092 `
            --if-not-exists `
            --partitions 1 `
            --replication-factor 1 2>&1 | Out-Null
        Write-Host "✅ Tópico $topic criado" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Tópico $topic já existe ou erro ao criar" -ForegroundColor Yellow
    }
}

# 7. Verificação final
Write-Host ""
Write-Host "============================================================"
Write-Host "7️⃣ Verificação final de saúde..."
Write-Host "============================================================" -ForegroundColor Cyan

$SERVICES = @(
    @{Name="SEM-CSMF"; Url="http://localhost:8080/health"},
    @{Name="ML-NSMF"; Url="http://localhost:8081/health"},
    @{Name="Decision Engine"; Url="http://localhost:8082/health"},
    @{Name="BC-NSSMF"; Url="http://localhost:8083/health"},
    @{Name="SLA-Agent Layer"; Url="http://localhost:8084/health"},
    @{Name="NASP Adapter"; Url="http://localhost:8085/health"}
)

$ALL_HEALTHY = $true
foreach ($service in $SERVICES) {
    if (Check-Health $service.Name $service.Url 5) {
        Write-Host "✅ $($service.Name): OK" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.Name): FALHOU" -ForegroundColor Red
        $ALL_HEALTHY = $false
    }
}

# 8. Resumo
Write-Host ""
Write-Host "============================================================"
Write-Host "📊 Resumo do Ambiente E2E"
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Serviços rodando:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
if ($ALL_HEALTHY) {
    Write-Host "✅ Ambiente E2E iniciado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Endpoints disponíveis:"
    Write-Host "  - SEM-CSMF:        http://localhost:8080"
    Write-Host "  - ML-NSMF:          http://localhost:8081"
    Write-Host "  - Decision Engine:  http://localhost:8082"
    Write-Host "  - BC-NSSMF:         http://localhost:8083"
    Write-Host "  - SLA-Agent Layer:  http://localhost:8084"
    Write-Host "  - NASP Adapter:     http://localhost:8085"
    Write-Host "  - Prometheus:       http://localhost:9090"
    Write-Host "  - Grafana:          http://localhost:3000 (admin/admin)"
    Write-Host "  - Besu RPC:         http://localhost:8545"
    Write-Host ""
    Write-Host "Para executar testes E2E:"
    Write-Host "  pytest tests/e2e/test_trisla_e2e.py -v"
    Write-Host ""
    Write-Host "Para parar o ambiente:"
    Write-Host "  docker compose down"
} else {
    Write-Host "⚠️ Alguns serviços podem não estar totalmente saudáveis" -ForegroundColor Yellow
    Write-Host "Verifique os logs com: docker compose logs [service-name]"
}

Write-Host ""
Write-Host "============================================================"

