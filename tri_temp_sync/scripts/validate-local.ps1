# ============================================
# Script: Validação e Testes Locais do TriSLA (PowerShell)
# ============================================
# Executa validações e testes que podem ser feitos na máquina local
# ============================================

$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Validação e Testes Locais                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$BASE_DIR = $PSScriptRoot | Split-Path -Parent
Set-Location $BASE_DIR

# Função para verificar se um serviço está rodando
function Test-Service {
    param(
        [string]$Name,
        [int]$Port
    )
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $Name está rodando na porta $Port" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "⚠️  $Name não está rodando na porta $Port" -ForegroundColor Yellow
        return $false
    }
    return $false
}

# Função para testar endpoint de health
function Test-HealthEndpoint {
    param(
        [string]$Module,
        [int]$Port
    )
    
    $url = "http://localhost:$Port/health"
    
    Write-Host "Testando $Module ($url)..."
    try {
        $response = Invoke-RestMethod -Uri $url -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✅ $Module`: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
        Write-Host ""
        return $response
    }
    catch {
        Write-Host "⚠️  $Module não está acessível" -ForegroundColor Yellow
        Write-Host ""
        return $null
    }
}

# 1. Verificar Health dos Módulos
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "1️⃣  Verificando Health dos Módulos" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$null = Test-Service -Name "SEM-CSMF" -Port 8080
$null = Test-Service -Name "ML-NSMF" -Port 8081
$null = Test-Service -Name "Decision Engine" -Port 8082
$null = Test-Service -Name "BC-NSSMF" -Port 8083
$null = Test-Service -Name "SLA-Agent Layer" -Port 8084
$null = Test-Service -Name "NASP Adapter" -Port 8085

Write-Host ""

# 2. Testar Endpoints de Health
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "2️⃣  Testando Endpoints de Health" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Test-HealthEndpoint -Module "SEM-CSMF" -Port 8080
Test-HealthEndpoint -Module "ML-NSMF" -Port 8081
Test-HealthEndpoint -Module "Decision Engine" -Port 8082
Test-HealthEndpoint -Module "BC-NSSMF" -Port 8083
Test-HealthEndpoint -Module "SLA-Agent Layer" -Port 8084
Test-HealthEndpoint -Module "NASP Adapter" -Port 8085

# 3. Testar Interfaces I-01 a I-07
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "3️⃣  Testando Interfaces I-01 a I-07" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "Executando testes de integração..."
if (Test-Path "tests\integration\test_interfaces.py") {
    if (Get-Command pytest -ErrorAction SilentlyContinue) {
        # Verificar se kafka-python está instalado
        try {
            $kafkaCheck = python -c "import kafka; print('OK')" 2>&1
            if ($LASTEXITCODE -ne 0 -or $kafkaCheck -notmatch "OK") {
                Write-Host "⚠️  kafka-python não está instalado ou tem problemas. Instale com: pip install kafka-python" -ForegroundColor Yellow
                Write-Host "   Nota: kafka-python 2.0.2 pode ter problemas com Python 3.12. Tente: pip install 'kafka-python>=2.0.2'" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "⚠️  kafka-python não está instalado. Instale com: pip install kafka-python" -ForegroundColor Yellow
        }
        
        # Executar testes, mas não falhar se serviços não estiverem rodando
        $testOutput = pytest tests/integration/test_interfaces.py -v 2>&1 | Out-String
        Write-Host $testOutput
        
        # Verificar se os erros são apenas de conectividade (esperado sem serviços)
        if ($testOutput -match "getaddrinfo failed|NoBrokersAvailable|ConnectError") {
            Write-Host ""
            Write-Host "ℹ️  Nota: Alguns testes falharam porque os serviços não estão rodando." -ForegroundColor Cyan
            Write-Host "   Isso é esperado quando testando localmente sem Docker Compose." -ForegroundColor Cyan
            Write-Host "   Para testes completos, inicie os serviços com: docker-compose up -d" -ForegroundColor Cyan
        }
    }
    else {
        Write-Host "⚠️  pytest não está instalado. Instale com: pip install pytest pytest-asyncio httpx kafka-python" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️  Arquivo de testes não encontrado: tests/integration/test_interfaces.py" -ForegroundColor Yellow
}

Write-Host ""

# 4. Verificar OTLP Collector
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "4️⃣  Verificando OTLP Collector" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$null = Test-Service -Name "OTLP Collector (gRPC)" -Port 4317
$null = Test-Service -Name "OTLP Collector (HTTP)" -Port 4318

if (Test-Path "monitoring\otel-collector\config.yaml") {
    Write-Host "✅ Configuração do OTLP Collector encontrada" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Configuração do OTLP Collector não encontrada" -ForegroundColor Yellow
}

Write-Host ""

# 5. Verificar Métricas TriSLA
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "5️⃣  Verificando Métricas TriSLA" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$null = Test-Service -Name "Prometheus" -Port 9090

if (Test-Path "monitoring\prometheus\prometheus.yml") {
    Write-Host "✅ Configuração do Prometheus encontrada" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Configuração do Prometheus não encontrada" -ForegroundColor Yellow
}

if (Test-Path "monitoring\prometheus\rules\slo-rules.yml") {
    Write-Host "✅ Regras SLO do Prometheus encontradas" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Regras SLO do Prometheus não encontradas" -ForegroundColor Yellow
}

Write-Host ""

# 6. Verificar Traces
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "6️⃣  Verificando Traces" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$otlpRunning = Test-Service -Name "OTLP Collector" -Port 4317
if ($otlpRunning) {
    Write-Host "✅ OTLP Collector está disponível para receber traces" -ForegroundColor Green
}
else {
    Write-Host "⚠️  OTLP Collector não está disponível" -ForegroundColor Yellow
}

Write-Host ""

# 7. Verificar SLO Reports
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "7️⃣  Verificando SLO Reports" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "monitoring\slo-reports\generator.py") {
    Write-Host "✅ Gerador de SLO Reports encontrado" -ForegroundColor Green
    
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "Testando gerador de SLO Reports..."
        Push-Location "monitoring\slo-reports"
        try {
            # Verificar se requirements.txt existe e instalar dependências
            if (Test-Path "requirements.txt") {
                Write-Host "   Verificando dependências do gerador de SLO Reports..."
                $requirements = Get-Content "requirements.txt"
                $missing = @()
                foreach ($req in $requirements) {
                    if ($req -match "^([a-zA-Z0-9_-]+)") {
                        $packageName = $matches[1]
                        # Converter nome do pacote para nome do módulo
                        # prometheus-client -> prometheus_client
                        # python-dateutil -> dateutil
                        $moduleName = $packageName -replace "-", "_"
                        if ($packageName -eq "python-dateutil") {
                            $moduleName = "dateutil"
                        }
                        
                        try {
                            $importCheck = python -c "import $moduleName; print('OK')" 2>&1
                            if ($LASTEXITCODE -ne 0 -or $importCheck -notmatch "OK") {
                                $missing += $packageName
                            }
                        }
                        catch {
                            $missing += $packageName
                        }
                    }
                }
                if ($missing.Count -eq 0) {
                    Write-Host "✅ Gerador de SLO Reports está funcional" -ForegroundColor Green
                }
                else {
                    Write-Host "⚠️  Gerador de SLO Reports tem dependências faltando: $($missing -join ', ')" -ForegroundColor Yellow
                    Write-Host "   Instale com: pip install -r monitoring\slo-reports\requirements.txt" -ForegroundColor Cyan
                }
            }
            else {
                Write-Host "⚠️  requirements.txt não encontrado para o gerador de SLO Reports" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "⚠️  Não foi possível testar o gerador" -ForegroundColor Yellow
        }
        Pop-Location
    }
    else {
        Write-Host "⚠️  Python não está instalado" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️  Gerador de SLO Reports não encontrado" -ForegroundColor Yellow
}

Write-Host ""

# 8. Verificar Logs do SLO Reporter
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "8️⃣  Verificando Logs do SLO Reporter" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "monitoring\slo-reports") {
    if (Test-Path "monitoring\slo-reports\generator.py") {
        Write-Host "✅ Script do SLO Reporter encontrado" -ForegroundColor Green
        Write-Host ""
        Write-Host "ℹ️  Para ver logs do SLO Reporter, execute:" -ForegroundColor Cyan
        Write-Host "   python monitoring\slo-reports\generator.py" -ForegroundColor White
    }
    else {
        Write-Host "⚠️  Script do SLO Reporter não encontrado" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️  Diretório de SLO Reports não encontrado" -ForegroundColor Yellow
}

Write-Host ""

# Resumo
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📋 Resumo da Validação" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para executar testes completos, certifique-se de que:" -ForegroundColor White
Write-Host "  1. Todos os módulos estão rodando (ou use Docker Compose)" -ForegroundColor White
Write-Host "  2. OTLP Collector está configurado e rodando" -ForegroundColor White
Write-Host "  3. Prometheus está configurado e rodando" -ForegroundColor White
Write-Host "  4. Kafka está disponível (para testes de interfaces I-03, I-04, I-05)" -ForegroundColor White
Write-Host ""
Write-Host "Para iniciar todos os serviços localmente:" -ForegroundColor White
Write-Host "  docker-compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para executar testes automatizados:" -ForegroundColor White
Write-Host "  pytest tests\ -v" -ForegroundColor Cyan
Write-Host ""

