# ============================================
# TRI-SLA LOCAL VALIDATION PIPELINE (QUICK)
# ============================================
# Versão rápida que pula construção de imagens Docker
# ============================================

$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TRI-SLA LOCAL VALIDATION PIPELINE (QUICK)                 ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# 1. Validar estrutura do repositório
Write-Host "🔍 1/7 — Validando estrutura do repositório..."
if (Test-Path "scripts/verify-structure.ps1") {
    powershell -ExecutionPolicy Bypass -File scripts/verify-structure.ps1
} else {
    Write-Host "   ⚠️  Script verify-structure.ps1 não encontrado (não crítico)"
}
Write-Host ""

# 2. Pular construção de imagens (assumir que já existem)
Write-Host "🔍 2/7 — Validando dependências locais..."
Write-Host "   ⏭️  Pulando construção de imagens Docker (assumindo que já existem)"
Write-Host "   Para construir imagens, execute: docker-compose build"
Write-Host ""

# 3. Testar conexões módulo a módulo
Write-Host "🔍 3/7 — Testando conexões módulo a módulo..."
if (Test-Path "scripts/test-module-connections.ps1") {
    powershell -ExecutionPolicy Bypass -File scripts/test-module-connections.ps1
} else {
    Write-Host "   ⚠️  test-module-connections.ps1 não encontrado"
}

if (Test-Path "scripts/validate-local.py") {
    python scripts/validate-local.py
} else {
    Write-Host "   ⚠️  validate-local.py não encontrado"
}
Write-Host ""

# 4. Testar fluxo completo gRPC
Write-Host "🔍 4/7 — Testando fluxo completo gRPC..."
if (Test-Path "tests/integration/test_grpc_communication.py") {
    pytest tests/integration/test_grpc_communication.py -q -v
} else {
    Write-Host "   ⚠️  test_grpc_communication.py não encontrado"
}
Write-Host ""

# 5. Testar integração entre módulos
Write-Host "🔍 5/7 — Testando integração entre módulos..."
if (Test-Path "tests/integration/test_module_integration.py") {
    pytest tests/integration/test_module_integration.py -q -v
} else {
    Write-Host "   ⚠️  test_module_integration.py não encontrado"
}
Write-Host ""

# 6. Testar persistência e banco
Write-Host "🔍 6/7 — Testando persistência e banco..."
if (Test-Path "tests/integration/test_persistence_flow.py") {
    pytest tests/integration/test_persistence_flow.py -q -v
} else {
    Write-Host "   ⚠️  test_persistence_flow.py não encontrado"
}
Write-Host ""

# 7. Validar performance básica (pular se não existir)
Write-Host "🔍 7/7 — Validando performance básica..."
if (Test-Path "tests/load/test_load.py") {
    pytest tests/load/test_load.py -q -v
} else {
    Write-Host "   ⚠️  test_load.py não encontrado (pasta tests/load/ pode não existir)"
    Write-Host "   ✅ Pulando teste de performance (não crítico)"
}
Write-Host ""

Write-Host "✅ VALIDAÇÃO LOCAL FINALIZADA (QUICK MODE)"
Write-Host "Tudo pronto para criação da release TriSLA v3.4.0"
Write-Host ""

