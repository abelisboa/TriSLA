# ============================================
# TriSLA - Iniciar Ambiente Local Completo (PowerShell)
# ============================================

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Iniciando Ambiente Local Completo          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
Write-Host "🔍 Verificando se Docker está rodando..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker não está acessível"
    }
    Write-Host "✅ Docker está rodando" -ForegroundColor Green
}
catch {
    Write-Host "" -ForegroundColor Red
    Write-Host "❌ ERRO: Docker Desktop não está rodando!" -ForegroundColor Red
    Write-Host "" -ForegroundColor Red
    Write-Host "📋 Para resolver:" -ForegroundColor Yellow
    Write-Host "   1. Abra o Docker Desktop no Windows" -ForegroundColor White
    Write-Host "   2. Aguarde até que o ícone do Docker na bandeja do sistema fique verde" -ForegroundColor White
    Write-Host "   3. Execute este script novamente" -ForegroundColor White
    Write-Host "" -ForegroundColor Red
    Write-Host "💡 Dica: Procure por 'Docker Desktop' no menu Iniciar do Windows" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Red
    exit 1
}

# Verificar se Docker Compose está disponível
$dockerComposeCmd = $null
if (Get-Command docker -ErrorAction SilentlyContinue) {
    try {
        docker compose version | Out-Null
        $dockerComposeCmd = "docker compose"
    }
    catch {
        if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
            $dockerComposeCmd = "docker-compose"
        }
    }
}

if (-not $dockerComposeCmd) {
    Write-Host "❌ Docker Compose não está instalado." -ForegroundColor Red
    exit 1
}

Write-Host "📦 Construindo imagens Docker..." -ForegroundColor Yellow
$buildResult = Invoke-Expression "$dockerComposeCmd build 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao construir imagens Docker" -ForegroundColor Red
    Write-Host $buildResult -ForegroundColor Red
    exit 1
}
Write-Host "✅ Imagens construídas com sucesso" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Iniciando todos os serviços..." -ForegroundColor Yellow
$upResult = Invoke-Expression "$dockerComposeCmd up -d 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao iniciar serviços" -ForegroundColor Red
    Write-Host $upResult -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Verifique os logs com: $dockerComposeCmd logs" -ForegroundColor Cyan
    exit 1
}
Write-Host "✅ Serviços iniciados" -ForegroundColor Green

Write-Host ""
Write-Host "⏳ Aguardando serviços iniciarem (30 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "📊 Verificando status dos serviços..." -ForegroundColor Yellow
$psResult = Invoke-Expression "$dockerComposeCmd ps 2>&1"
if ($LASTEXITCODE -eq 0) {
    Write-Host $psResult
} else {
    Write-Host "⚠️  Não foi possível verificar o status dos serviços" -ForegroundColor Yellow
    Write-Host $psResult -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Ambiente TriSLA iniciado com sucesso!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Endpoints disponíveis:" -ForegroundColor Cyan
Write-Host "   • UI Dashboard:        http://localhost:80"
Write-Host "   • SEM-CSMF:            http://localhost:8080"
Write-Host "   • ML-NSMF:             http://localhost:8081"
Write-Host "   • Decision Engine:     http://localhost:8082"
Write-Host "   • BC-NSSMF:            http://localhost:8083"
Write-Host "   • SLA-Agent Layer:      http://localhost:8084"
Write-Host "   • NASP Adapter:        http://localhost:8085 (MOCK)"
Write-Host "   • Prometheus:          http://localhost:9090"
Write-Host "   • Grafana:             http://localhost:3000 (admin/admin)"
Write-Host "   • Kafka:                localhost:29092"
Write-Host ""
Write-Host "📝 Comandos úteis:" -ForegroundColor Cyan
Write-Host "   • Ver logs:            $dockerComposeCmd logs -f [serviço]"
Write-Host "   • Parar serviços:     $dockerComposeCmd down"
Write-Host "   • Reiniciar serviço:  $dockerComposeCmd restart [serviço]"
Write-Host "   • Status:             $dockerComposeCmd ps"
Write-Host ""
Write-Host "🧪 Para executar testes:" -ForegroundColor Cyan
Write-Host "   • Testes unitários:   pytest tests\unit\ -v"
Write-Host "   • Testes integração:   pytest tests\integration\ -v"
Write-Host "   • Validação local:    .\scripts\validate-local.ps1"
Write-Host ""

