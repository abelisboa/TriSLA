# ============================================
# Script para Executar Testes de Carga
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Executar Testes de Carga                      ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar se Python está instalado
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Erro: Python não encontrado. Instale Python 3.8+"
    exit 1
}

# Verificar se dependências estão instaladas
Write-Host "Verificando dependências..."
try {
    python -c "import aiohttp" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Instalando dependências..."
        pip install -r tests/load/requirements.txt
    }
} catch {
    Write-Host "Instalando dependências..."
    pip install -r tests/load/requirements.txt
}

# Verificar se serviços estão rodando
Write-Host ""
Write-Host "Verificando se os serviços estão rodando..."
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET -TimeoutSec 5
    Write-Host "✅ SEM-CSMF está rodando"
} catch {
    Write-Host "❌ Erro: SEM-CSMF não está acessível em http://localhost:8080"
    Write-Host "   Execute: docker compose up -d"
    exit 1
}

# Executar teste
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "Iniciando teste de carga..."
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

python tests/load/test_load.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Teste de carga concluído com sucesso!"
    Write-Host ""
    Write-Host "Resultados salvos em: tests/load/results_*.json"
} else {
    Write-Host ""
    Write-Host "❌ Teste de carga falhou"
    exit 1
}

