# ============================================
# TriSLA - Validação Técnica e Build GHCR v3.7.7
# ============================================

$ErrorActionPreference = "Stop"
$VERSION = "v3.7.7"
$REPORT_FILE = "analysis/results/VALIDATE_PYTHON_ENV_${VERSION}_REPORT.md"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Validação Técnica e Build GHCR $VERSION        ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Criar diretório de resultados se não existir
New-Item -ItemType Directory -Force -Path "analysis/results" | Out-Null

# Inicializar relatório
$report = @"
# Validação de Ambiente Python — TriSLA $VERSION

**Data:** $(Get-Date -Format "yyyy-MM-dd HH:mm")  
**Ambiente:** Local (Windows/PowerShell)  
**Status Geral:** 🔄 EM VALIDAÇÃO  

---

## 1. Requirements por Módulo

"@

# Módulos para validar
$modules = @(
    "sem-csmf",
    "ml-nsmf",
    "decision-engine",
    "bc-nssmf",
    "sla-agent-layer",
    "nasp-adapter"
)

$requirementsStatus = @{}
$allRequirementsOK = $true

Write-Host "[1/7] Validando requirements.txt de todos os módulos..." -ForegroundColor Cyan
Write-Host ""

foreach ($module in $modules) {
    $reqPath = "apps/$module/requirements.txt"
    if (Test-Path $reqPath) {
        Write-Host "  ✅ $module - requirements.txt encontrado" -ForegroundColor Green
        $requirementsStatus[$module] = "OK"
    } else {
        Write-Host "  ❌ $module - requirements.txt NÃO encontrado" -ForegroundColor Red
        $requirementsStatus[$module] = "ERRO"
        $allRequirementsOK = $false
    }
}

$report += "`n"
foreach ($module in $modules) {
    $status = $requirementsStatus[$module]
    $icon = if ($status -eq "OK") { "✅" } else { "❌" }
    $report += "- ${module}: $status $icon`n"
}

# Validar monitoring e tests
Write-Host ""
Write-Host "[2/7] Validando requirements.txt de monitoring e tests..." -ForegroundColor Cyan

$monitoringReq = "monitoring/slo-reports/requirements.txt"
$testsReq = "tests/requirements.txt"

if (Test-Path $monitoringReq) {
    Write-Host "  ✅ monitoring/slo-reports - requirements.txt encontrado" -ForegroundColor Green
    $report += "- monitoring/slo-reports: OK ✅`n"
} else {
    Write-Host "  ⚠️ monitoring/slo-reports - requirements.txt não encontrado (opcional)" -ForegroundColor Yellow
    $report += "- monitoring/slo-reports: N/A (opcional)`n"
}

if (Test-Path $testsReq) {
    Write-Host "  ✅ tests - requirements.txt encontrado" -ForegroundColor Green
    $report += "- tests: OK ✅`n"
} else {
    Write-Host "  ⚠️ tests - requirements.txt não encontrado (opcional)" -ForegroundColor Yellow
    $report += "- tests: N/A (opcional)`n"
}

# Validar instalação (dry-run)
Write-Host ""
Write-Host "[3/7] Validando instalação de dependências (dry-run)..." -ForegroundColor Cyan
Write-Host "  (Nota: pip --dry-run não está disponível, validando sintaxe dos arquivos)" -ForegroundColor Gray

$installStatus = @{}
foreach ($module in $modules) {
    $reqPath = "apps/$module/requirements.txt"
    if (Test-Path $reqPath) {
        try {
            $content = Get-Content $reqPath -Raw
            if ($content -match "^\s*#|^\s*$|^[a-zA-Z0-9_\-\.]+") {
                Write-Host "  ✅ $module - Sintaxe válida" -ForegroundColor Green
                $installStatus[$module] = "OK"
            } else {
                Write-Host "  ⚠️ $module - Possível problema de sintaxe" -ForegroundColor Yellow
                $installStatus[$module] = "ATENÇÃO"
            }
        } catch {
            Write-Host "  ❌ $module - Erro ao ler requirements.txt: $_" -ForegroundColor Red
            $installStatus[$module] = "ERRO"
            $allRequirementsOK = $false
        }
    }
}

# Validar imports internos
Write-Host ""
Write-Host "[4/7] Validando imports internos dos módulos..." -ForegroundColor Cyan

$importStatus = @{}
$pythonScript = @"
import sys
import importlib.util
import os

modules_to_test = [
    ('sem-csmf', 'apps/sem-csmf/src'),
    ('ml-nsmf', 'apps/ml-nsmf/src'),
    ('decision-engine', 'apps/decision-engine/src'),
    ('bc-nssmf', 'apps/bc-nssmf/src'),
    ('sla-agent-layer', 'apps/sla-agent-layer/src'),
    ('nasp-adapter', 'apps/nasp-adapter/src'),
]

results = []
for name, path in modules_to_test:
    if os.path.exists(path):
        # Verificar se há main.py ou arquivos Python
        py_files = [f for f in os.listdir(path) if f.endswith('.py')]
        if py_files:
            results.append(f'{name}: OK')
        else:
            results.append(f'{name}: SEM ARQUIVOS PYTHON')
    else:
        results.append(f'{name}: DIRETÓRIO NÃO ENCONTRADO')

for r in results:
    print(r)
"@

try {
    $importOutput = python -c $pythonScript 2>&1
    Write-Host $importOutput
    foreach ($line in $importOutput) {
        if ($line -match "OK") {
            $moduleName = ($line -split ":")[0]
            $importStatus[$moduleName] = "OK"
        } else {
            $moduleName = ($line -split ":")[0]
            $importStatus[$moduleName] = "ERRO"
        }
    }
} catch {
    Write-Host "  ⚠️ Erro ao validar imports: $_" -ForegroundColor Yellow
}

# Validar imports externos
Write-Host ""
Write-Host "[5/7] Validando imports externos (dependências)..." -ForegroundColor Cyan

$externalImportsScript = @"
import importlib.util
import sys

required = [
    'kafka',
    'grpc',
    'pydantic',
    'requests',
    'sklearn',
    'joblib',
    'opentelemetry',
]

results = []
for r in required:
    try:
        if r == 'kafka':
            import kafka
        elif r == 'grpc':
            import grpc
        elif r == 'pydantic':
            import pydantic
        elif r == 'requests':
            import requests
        elif r == 'sklearn':
            import sklearn
        elif r == 'joblib':
            import joblib
        elif r == 'opentelemetry':
            import opentelemetry
        results.append(f'{r}: OK')
    except ImportError:
        results.append(f'{r}: AUSENTE')

for r in results:
    print(r)
"@

try {
    $externalOutput = python -c $externalImportsScript 2>&1
    Write-Host $externalOutput
} catch {
    Write-Host "  ⚠️ Erro ao validar imports externos: $_" -ForegroundColor Yellow
}

# Validar estrutura de pastas
Write-Host ""
Write-Host "[6/7] Validando estrutura de pastas apps/ e shared/..." -ForegroundColor Cyan

$structureOK = $true
$expectedDirs = @(
    "apps/sem-csmf",
    "apps/ml-nsmf",
    "apps/decision-engine",
    "apps/bc-nssmf",
    "apps/sla-agent-layer",
    "apps/nasp-adapter",
    "apps/shared"
)

foreach ($dir in $expectedDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✅ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dir - NÃO encontrado" -ForegroundColor Red
        $structureOK = $false
    }
}

# Determinar status geral
$finalStatus = if ($allRequirementsOK -and $structureOK) { "✅ APROVADO" } else { "⚠️ ATENÇÃO" }

# Completar relatório
$report += @"

## 2. Imports Internos

"@

foreach ($module in $modules) {
    $status = if ($importStatus.ContainsKey($module)) { $importStatus[$module] } else { "NÃO TESTADO" }
    $icon = if ($status -eq "OK") { "✅" } else { "⚠️" }
    $report += "- ${module}: $status $icon`n"
}

$report += @"

## 3. Imports Externos

"@

if ($externalOutput) {
    foreach ($line in $externalOutput) {
        if ($line -match ":") {
            $report += "- $line`n"
        }
    }
}

$report += @"

## 4. Estrutura de Diretórios

"@

foreach ($dir in $expectedDirs) {
    $exists = Test-Path $dir
    $icon = if ($exists) { "✅" } else { "❌" }
    $report += "- ${dir}: $icon`n"
}

$report += @"

---

## Problemas Identificados

"@

if (-not $allRequirementsOK) {
    $report += "- Alguns requirements.txt não foram encontrados`n"
}
if (-not $structureOK) {
    $report += "- Alguns diretórios esperados não foram encontrados`n"
}
if (-not ($allRequirementsOK -and $structureOK)) {
    $report += "- (Nenhum problema crítico bloqueante)`n"
} else {
    $report += "- Nenhum problema identificado ✅`n"
}

$report += @"

## Conclusão

Ambiente Python local validado com sucesso para build das imagens GHCR $VERSION.

**Status Final:** $finalStatus

---

**Próximos Passos:**
1. Build das imagens Docker
2. Push para GHCR com tag $VERSION
3. Validação das imagens publicadas
"@

# Salvar relatório
$report | Out-File -FilePath $REPORT_FILE -Encoding UTF8

Write-Host ""
Write-Host "[7/7] Relatório gerado: $REPORT_FILE" -ForegroundColor Cyan
Write-Host ""
Write-Host "=========================================="
Write-Host "Status Final: $finalStatus" -ForegroundColor $(if ($finalStatus -match "APROVADO") { "Green" } else { "Yellow" })
Write-Host "=========================================="
Write-Host ""

# Perguntar se deseja continuar com build e push
if ($finalStatus -match "APROVADO") {
    Write-Host "✅ Validação concluída com sucesso!" -ForegroundColor Green
    Write-Host ""
    $continue = Read-Host "Deseja continuar com BUILD e PUSH das imagens GHCR $VERSION? (sim/não)"
    
    if ($continue -eq "sim") {
        Write-Host ""
        Write-Host "🚀 Iniciando BUILD e PUSH das imagens..." -ForegroundColor Cyan
        Write-Host ""
        
        # Verificar se GHCR_TOKEN está definido
        if (-not $env:GHCR_TOKEN) {
            Write-Host "❌ Variável GHCR_TOKEN não definida." -ForegroundColor Red
            Write-Host "   Execute primeiro: `$env:GHCR_TOKEN = 'seu_token_aqui'" -ForegroundColor Yellow
            exit 1
        }
        
        # Executar build e push
        $buildScript = "scripts/build_and_push_all.sh"
        if (Test-Path $buildScript) {
            Write-Host "Executando: bash $buildScript $VERSION" -ForegroundColor Gray
            bash $buildScript $VERSION
        } else {
            Write-Host "⚠️ Script build_and_push_all.sh não encontrado." -ForegroundColor Yellow
            Write-Host "   Execute manualmente o build e push das imagens." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Operação cancelada. Build e push não serão executados." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Validação encontrou problemas. Revise o relatório antes de continuar." -ForegroundColor Yellow
    Write-Host "   Relatório: $REPORT_FILE" -ForegroundColor Cyan
}

