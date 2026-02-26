# ============================================
# Script para Analisar Resultados de Testes de Carga
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Análise de Resultados de Testes de Carga      ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Procurar arquivos de resultados
$resultsDir = "tests\load"
if (-not (Test-Path $resultsDir)) {
    Write-Host "❌ Diretório de resultados não encontrado: $resultsDir"
    exit 1
}

$resultFiles = Get-ChildItem -Path $resultsDir -Filter "results_*.json" | Sort-Object LastWriteTime -Descending

if ($resultFiles.Count -eq 0) {
    Write-Host "❌ Nenhum arquivo de resultados encontrado."
    Write-Host "   Execute primeiro: .\scripts\run-load-test.ps1"
    exit 1
}

Write-Host "Arquivos de resultados encontrados:"
$i = 1
foreach ($file in $resultFiles) {
    Write-Host "  $i. $($file.Name) - $($file.LastWriteTime)"
    $i++
}

Write-Host ""
$choice = Read-Host "Selecione o arquivo para analisar (número, ou 'todos' para comparar)"

if ($choice -eq 'todos' -or $choice -eq 'TODOS') {
    # Analisar todos
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "Análise Comparativa de Todos os Testes"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""
    
    foreach ($file in $resultFiles) {
        $data = Get-Content $file.FullName | ConvertFrom-Json
        Write-Host "📊 $($file.Name)"
        Write-Host "   Data: $($data.timestamp)"
        Write-Host "   Tempo Total: $([math]::Round($data.results.elapsed_time, 2))s"
        Write-Host "   Requisições: $($data.results.total_requests)"
        Write-Host "   Taxa de Sucesso: $([math]::Round($data.results.success_rate, 2))%"
        Write-Host "   RPS: $([math]::Round($data.results.requests_per_second, 2))"
        Write-Host "   Latência Média: $([math]::Round($data.results.response_times.avg * 1000, 2))ms"
        Write-Host "   Latência P95: $([math]::Round($data.results.response_times.p95 * 1000, 2))ms"
        Write-Host "   Latência P99: $([math]::Round($data.results.response_times.p99 * 1000, 2))ms"
        Write-Host ""
    }
} else {
    # Analisar arquivo específico
    $index = [int]$choice - 1
    if ($index -lt 0 -or $index -ge $resultFiles.Count) {
        Write-Host "❌ Escolha inválida"
        exit 1
    }
    
    $selectedFile = $resultFiles[$index]
    $data = Get-Content $selectedFile.FullName | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "Análise Detalhada: $($selectedFile.Name)"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""
    
    Write-Host "📅 Informações Gerais"
    Write-Host "   Data/Hora: $($data.timestamp)"
    Write-Host "   Configuração:"
    Write-Host "     - Usuários Concorrentes: $($data.config.concurrent_users)"
    Write-Host "     - Requisições por Usuário: $($data.config.requests_per_user)"
    Write-Host "     - Total de Requisições: $($data.config.total_requests)"
    Write-Host ""
    
    Write-Host "⏱️  Performance"
    Write-Host "   Tempo Total: $([math]::Round($data.results.elapsed_time, 2))s"
    Write-Host "   Requisições por Segundo: $([math]::Round($data.results.requests_per_second, 2)) RPS"
    Write-Host ""
    
    Write-Host "✅ Resultados"
    Write-Host "   Total de Requisições: $($data.results.total_requests)"
    Write-Host "   Bem-sucedidas: $($data.results.successful_requests)"
    Write-Host "   Falhadas: $($data.results.failed_requests)"
    Write-Host "   Taxa de Sucesso: $([math]::Round($data.results.success_rate, 2))%"
    Write-Host ""
    
    Write-Host "📊 Tempos de Resposta"
    Write-Host "   Média: $([math]::Round($data.results.response_times.avg * 1000, 2))ms"
    Write-Host "   Mediana: $([math]::Round($data.results.response_times.median * 1000, 2))ms"
    Write-Host "   Mínimo: $([math]::Round($data.results.response_times.min * 1000, 2))ms"
    Write-Host "   Máximo: $([math]::Round($data.results.response_times.max * 1000, 2))ms"
    Write-Host "   P95: $([math]::Round($data.results.response_times.p95 * 1000, 2))ms"
    Write-Host "   P99: $([math]::Round($data.results.response_times.p99 * 1000, 2))ms"
    Write-Host ""
    
    if ($data.results.errors.Count -gt 0) {
        Write-Host "❌ Erros Encontrados: $($data.results.errors.Count)"
        foreach ($error in $data.results.errors) {
            Write-Host "   - $error"
        }
        Write-Host ""
    } else {
        Write-Host "✅ Nenhum erro encontrado!"
        Write-Host ""
    }
    
    # Análise de performance
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "📈 Análise de Performance"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""
    
    $avgLatency = $data.results.response_times.avg * 1000
    $p95Latency = $data.results.response_times.p95 * 1000
    $p99Latency = $data.results.response_times.p99 * 1000
    
    if ($avgLatency -lt 100) {
        Write-Host "✅ Latência Média: EXCELENTE (< 100ms)"
    } elseif ($avgLatency -lt 200) {
        Write-Host "✅ Latência Média: BOA (< 200ms)"
    } elseif ($avgLatency -lt 500) {
        Write-Host "⚠️  Latência Média: ACEITÁVEL (< 500ms)"
    } else {
        Write-Host "❌ Latência Média: ALTA (> 500ms) - Requer otimização"
    }
    
    if ($p95Latency -lt 200) {
        Write-Host "✅ Latência P95: EXCELENTE (< 200ms)"
    } elseif ($p95Latency -lt 500) {
        Write-Host "✅ Latência P95: BOA (< 500ms)"
    } elseif ($p95Latency -lt 1000) {
        Write-Host "⚠️  Latência P95: ACEITÁVEL (< 1s)"
    } else {
        Write-Host "❌ Latência P95: ALTA (> 1s) - Requer otimização"
    }
    
    if ($data.results.success_rate -ge 99) {
        Write-Host "✅ Taxa de Sucesso: EXCELENTE (≥ 99%)"
    } elseif ($data.results.success_rate -ge 95) {
        Write-Host "✅ Taxa de Sucesso: BOA (≥ 95%)"
    } elseif ($data.results.success_rate -ge 90) {
        Write-Host "⚠️  Taxa de Sucesso: ACEITÁVEL (≥ 90%)"
    } else {
        Write-Host "❌ Taxa de Sucesso: BAIXA (< 90%) - Requer investigação"
    }
    
    if ($data.results.requests_per_second -ge 100) {
        Write-Host "✅ Throughput: EXCELENTE (≥ 100 RPS)"
    } elseif ($data.results.requests_per_second -ge 50) {
        Write-Host "✅ Throughput: BOA (≥ 50 RPS)"
    } elseif ($data.results.requests_per_second -ge 20) {
        Write-Host "⚠️  Throughput: ACEITÁVEL (≥ 20 RPS)"
    } else {
        Write-Host "❌ Throughput: BAIXO (< 20 RPS) - Requer otimização"
    }
    
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

Write-Host ""
Write-Host "✅ Análise concluída!"

