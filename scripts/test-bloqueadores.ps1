# ============================================
# Script de Teste dos Bloqueadores Críticos
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Teste dos Bloqueadores Críticos               ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

$results = @{
    "Autenticação JWT" = $false
    "HTTPS/TLS" = $false
    "Retry Logic" = $false
    "Alertas" = $false
    "Backup" = $false
    "Módulos" = $false
}

# 1. Testar Autenticação JWT
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "1️⃣  Testando Autenticação JWT..."
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

try {
    # Fazer login
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body (@{username="admin"; password="admin"} | ConvertTo-Json)
    
    if ($loginResponse.access_token) {
        $token = $loginResponse.access_token
        Write-Host "✅ Login bem-sucedido! Token obtido."
        
        # Testar endpoint protegido
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        
        $protectedResponse = Invoke-RestMethod -Uri "http://localhost:8080/health" `
            -Method GET `
            -Headers $headers
        
        Write-Host "✅ Endpoint protegido acessível com token!"
        $results["Autenticação JWT"] = $true
    } else {
        Write-Host "❌ Falha: Token não retornado"
    }
} catch {
    Write-Host "❌ Erro ao testar autenticação: $_"
}

Write-Host ""

# 2. Testar HTTPS/TLS (verificar se nginx está configurado)
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "2️⃣  Verificando HTTPS/TLS..."
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if (Test-Path "nginx/nginx.conf") {
    Write-Host "✅ Configuração do Nginx encontrada"
    if (Test-Path "nginx/ssl/cert.pem") {
        Write-Host "✅ Certificado SSL encontrado"
        $results["HTTPS/TLS"] = $true
    } else {
        Write-Host "⚠️  Certificado SSL não encontrado (gerar com nginx/generate-self-signed-cert.sh)"
    }
} else {
    Write-Host "❌ Configuração do Nginx não encontrada"
}

Write-Host ""

# 3. Testar Retry Logic (verificar se arquivos existem)
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "3️⃣  Verificando Retry Logic..."
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if (Test-Path "apps/sem-csmf/src/grpc_client_retry.py") {
    Write-Host "✅ Cliente gRPC com retry encontrado"
    if (Test-Path "apps/sem-csmf/src/kafka_producer_retry.py") {
        Write-Host "✅ Producer Kafka com retry encontrado"
        $results["Retry Logic"] = $true
    } else {
        Write-Host "⚠️  Producer Kafka com retry não encontrado"
    }
} else {
    Write-Host "❌ Cliente gRPC com retry não encontrado"
}

Write-Host ""

# 4. Testar Alertas
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "4️⃣  Verificando Alertas..."
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if (Test-Path "monitoring/prometheus/rules/alerts.yml") {
    Write-Host "✅ Regras de alerta encontradas"
    
    # Verificar se Prometheus está configurado para usar as regras
    $prometheusConfig = Get-Content "monitoring/prometheus/prometheus.yml" -Raw
    if ($prometheusConfig -match "alerts.yml") {
        Write-Host "✅ Prometheus configurado para usar alertas"
        $results["Alertas"] = $true
    } else {
        Write-Host "⚠️  Prometheus não configurado para usar alertas"
    }
} else {
    Write-Host "❌ Regras de alerta não encontradas"
}

Write-Host ""

# 5. Testar Backup
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "5️⃣  Verificando Backup..."
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if (Test-Path "scripts/backup-postgres.sh") {
    Write-Host "✅ Script de backup Linux encontrado"
    if (Test-Path "scripts/backup-postgres.ps1") {
        Write-Host "✅ Script de backup PowerShell encontrado"
        $results["Backup"] = $true
    } else {
        Write-Host "⚠️  Script de backup PowerShell não encontrado"
    }
} else {
    Write-Host "❌ Script de backup não encontrado"
}

Write-Host ""

# 6. Verificar Módulos
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "6️⃣  Verificando Módulos..."
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

$modules = @("ml-nsmf", "bc-nssmf", "nasp-adapter")
$allModulesOk = $true

foreach ($module in $modules) {
    $mainFile = "apps/$module/src/main.py"
    if (Test-Path $mainFile) {
        Write-Host "✅ $module - Estrutura encontrada"
    } else {
        Write-Host "❌ $module - Estrutura não encontrada"
        $allModulesOk = $false
    }
}

if ($allModulesOk) {
    $results["Módulos"] = $true
}

Write-Host ""

# Resumo
Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║                    Resumo dos Testes                     ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

$total = $results.Count
$passed = ($results.Values | Where-Object { $_ -eq $true }).Count

foreach ($key in $results.Keys) {
    $status = if ($results[$key]) { "✅ PASSOU" } else { "❌ FALHOU" }
    Write-Host "  $key : $status"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Total: $passed/$total testes passaram"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ($passed -eq $total) {
    Write-Host ""
    Write-Host "🎉 Todos os bloqueadores críticos foram resolvidos!"
    exit 0
} else {
    Write-Host ""
    Write-Host "⚠️  Alguns bloqueadores ainda precisam de atenção."
    exit 1
}

