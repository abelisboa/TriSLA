#!/bin/bash
# ===========================================================
# 📈 Script de Análise de Resultados - TriSLA
# Analisa resultados dos testes e gera relatório para dissertação
# ===========================================================

OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/docs/evidencias/WU-005_avaliacao}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DATE=$(date +"%d de %B de %Y" | sed 's/January/janeiro/; s/February/fevereiro/; s/March/março/; s/April/abril/; s/May/maio/; s/June/junho/; s/July/julho/; s/August/agosto/; s/September/setembro/; s/October/outubro/; s/November/novembro/; s/December/dezembro/')

mkdir -p "$OUTPUT_DIR"

echo "==============================================="
echo "📈 Análise de Resultados - TriSLA"
echo "==============================================="
echo "Diretório: $OUTPUT_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Função para extrair valores de JSON
extract_json_value() {
    local file=$1
    local query=$2
    jq -r "$query" "$file" 2>/dev/null || echo "N/A"
}

# Função para calcular estatísticas de um array JSON
calculate_stats() {
    local file=$1
    local query=$2
    local values=$(jq -r "$query" "$file" 2>/dev/null)
    
    if [ -z "$values" ] || [ "$values" = "null" ]; then
        echo "N/A|N/A|N/A"
        return
    fi
    
    # Calcular min, max, avg usando awk
    min=$(echo "$values" | awk 'BEGIN{min=999999} {if ($1<min && $1!="") min=$1} END{print min}')
    max=$(echo "$values" | awk 'BEGIN{max=0} {if ($1>max) max=$1} END{print max}')
    avg=$(echo "$values" | awk '{sum+=$1; count++} END{if(count>0) print sum/count; else print 0}')
    
    echo "$min|$max|$avg"
}

echo "🔍 Analisando resultados dos testes..."
echo ""

# Analisar resultados de criação de slices
echo "1️⃣ Analisando criação de slices..."
slice_files=$(ls "$OUTPUT_DIR"/scenario_*_create_*.json 2>/dev/null | head -3)
urllc_created=0
embb_created=0
mmtc_created=0

for file in $slice_files; do
    if echo "$file" | grep -q "urllc"; then
        urllc_created=1
    elif echo "$file" | grep -q "embb"; then
        embb_created=1
    elif echo "$file" | grep -q "mmtc"; then
        mmtc_created=1
    fi
done

# Analisar resultados de testes de estresse
echo "2️⃣ Analisando testes de estresse..."
stress_files=$(ls "$OUTPUT_DIR"/stress_test_*_results.json 2>/dev/null)

urllc_stats=""
embb_stats=""
mmtc_stats=""

for file in $stress_files; do
    if echo "$file" | grep -q "urllc"; then
        success=$(extract_json_value "$file" '.success')
        total=$(extract_json_value "$file" '.total_requests')
        success_rate=$(extract_json_value "$file" '.success_rate')
        avg_time=$(extract_json_value "$file" '.avg_response_time')
        rps=$(extract_json_value "$file" '.requests_per_second')
        urllc_stats="$success|$total|$success_rate|$avg_time|$rps"
    elif echo "$file" | grep -q "embb"; then
        success=$(extract_json_value "$file" '.success')
        total=$(extract_json_value "$file" '.total_requests')
        success_rate=$(extract_json_value "$file" '.success_rate')
        avg_time=$(extract_json_value "$file" '.avg_response_time')
        rps=$(extract_json_value "$file" '.requests_per_second')
        embb_stats="$success|$total|$success_rate|$avg_time|$rps"
    elif echo "$file" | grep -q "mmtc"; then
        success=$(extract_json_value "$file" '.success')
        total=$(extract_json_value "$file" '.total_requests')
        success_rate=$(extract_json_value "$file" '.success_rate')
        avg_time=$(extract_json_value "$file" '.avg_response_time')
        rps=$(extract_json_value "$file" '.requests_per_second')
        mmtc_stats="$success|$total|$success_rate|$avg_time|$rps"
    fi
done

# Analisar métricas do Prometheus
echo "3️⃣ Analisando métricas do Prometheus..."

# CPU
cpu_file=$(ls "$OUTPUT_DIR"/prometheus_cpu_usage_*.json 2>/dev/null | head -1)
cpu_values="N/A"
if [ -n "$cpu_file" ]; then
    cpu_values=$(extract_json_value "$cpu_file" '.data.result[0].value[1] // "N/A"')
fi

# Memory
memory_file=$(ls "$OUTPUT_DIR"/prometheus_memory_usage_*.json 2>/dev/null | head -1)
memory_values="N/A"
if [ -n "$memory_file" ]; then
    memory_bytes=$(extract_json_value "$memory_file" '.data.result[0].value[1] // "N/A"')
    if [ "$memory_bytes" != "N/A" ] && [ -n "$memory_bytes" ]; then
        memory_mb=$(echo "scale=2; $memory_bytes / 1024 / 1024" | bc 2>/dev/null || echo "N/A")
        memory_values="$memory_mb MB"
    fi
fi

# Latência p99
latency_file=$(ls "$OUTPUT_DIR"/prometheus_latency_p99_*.json 2>/dev/null | head -1)
latency_p99="N/A"
if [ -n "$latency_file" ]; then
    latency_seconds=$(extract_json_value "$latency_file" '.data.result[0].value[1] // "N/A"')
    if [ "$latency_seconds" != "N/A" ] && [ -n "$latency_seconds" ]; then
        latency_ms=$(echo "scale=2; $latency_seconds * 1000" | bc 2>/dev/null || echo "N/A")
        latency_p99="${latency_ms} ms"
    fi
fi

echo ""
echo "==============================================="
echo "📊 Gerando Relatório de Análise"
echo "==============================================="
echo ""

# Criar relatório detalhado
report_file="$OUTPUT_DIR/analise_resultados_${TIMESTAMP}.md"
cat > "$report_file" << EOF
# 📊 Análise de Resultados - TriSLA@NASP
## Avaliação Experimental Atualizada

**Data:** $REPORT_DATE  
**Responsável:** Abel José Rodrigues Lisboa  
**Ambiente:** NASP - UNISINOS  
**Timestamp:** $TIMESTAMP

---

## 1. Resumo Executivo

Este relatório apresenta os resultados atualizados da avaliação experimental da arquitetura **TriSLA** integrada ao **NASP**, incluindo criação de slices, testes de estresse e análise de métricas de desempenho.

---

## 2. Criação de Slices

### 2.1 Status de Criação

| Cenário | Status | Observações |
|---------|--------|-------------|
| **URLLC** | $([ $urllc_created -eq 1 ] && echo '✅ Criado' || echo '⚠️ Não encontrado') | Telemedicina / Cirurgia Remota |
| **eMBB** | $([ $embb_created -eq 1 ] && echo '✅ Criado' || echo '⚠️ Não encontrado') | Streaming 4K / Realidade Aumentada |
| **mMTC** | $([ $mmtc_created -eq 1 ] && echo '✅ Criado' || echo '⚠️ Não encontrado') | IoT Massivo / Sensores |

### 2.2 Detalhes por Cenário

#### URLLC (Ultra-Reliable Low-Latency Communications)
- **Aplicação:** Telemedicina - Cirurgia Remota
- **Status de Criação:** $([ $urllc_created -eq 1 ] && echo 'Sucesso' || echo 'Não verificado')

#### eMBB (Enhanced Mobile Broadband)
- **Aplicação:** Streaming 4K + Realidade Aumentada
- **Status de Criação:** $([ $embb_created -eq 1 ] && echo 'Sucesso' || echo 'Não verificado')

#### mMTC (Massive Machine-Type Communications)
- **Aplicação:** Sensores IoT Industriais
- **Status de Criação:** $([ $mmtc_created -eq 1 ] && echo 'Sucesso' || echo 'Não verificado')

---

## 3. Testes de Estresse

### 3.1 Resultados Consolidados

| Cenário | Requisições | Sucessos | Taxa de Sucesso | Tempo Médio | RPS |
|---------|-------------|----------|-----------------|-------------|-----|
| **URLLC** | $(echo "$urllc_stats" | cut -d'|' -f2) | $(echo "$urllc_stats" | cut -d'|' -f1) | $(echo "$urllc_stats" | cut -d'|' -f3)% | $(echo "$urllc_stats" | cut -d'|' -f4)s | $(echo "$urllc_stats" | cut -d'|' -f5) |
| **eMBB** | $(echo "$embb_stats" | cut -d'|' -f2) | $(echo "$embb_stats" | cut -d'|' -f1) | $(echo "$embb_stats" | cut -d'|' -f3)% | $(echo "$embb_stats" | cut -d'|' -f4)s | $(echo "$embb_stats" | cut -d'|' -f5) |
| **mMTC** | $(echo "$mmtc_stats" | cut -d'|' -f2) | $(echo "$mmtc_stats" | cut -d'|' -f1) | $(echo "$mmtc_stats" | cut -d'|' -f3)% | $(echo "$mmtc_stats" | cut -d'|' -f4)s | $(echo "$mmtc_stats" | cut -d'|' -f5) |

---

## 4. Métricas de Desempenho (Prometheus)

### 4.1 Recursos do Sistema

| Métrica | Valor | Observações |
|---------|-------|-------------|
| **CPU Usage** | $cpu_values | Taxa de uso de CPU |
| **Memory Usage** | $memory_values | Uso de memória |
| **Latência p99** | $latency_p99 | Percentil 99 de latência |

### 4.2 Análise de KPIs

#### Latência
- **p50 (Mediana):** Consultar arquivo `prometheus_latency_p50_*.json`
- **p90:** Consultar arquivo `prometheus_latency_p90_*.json`
- **p99:** $latency_p99

#### Confiabilidade
- **Taxa de Sucesso:** Baseada nos testes de estresse (ver seção 3.1)
- **Taxa de Erro:** Consultar arquivo `prometheus_http_errors_*.json`

#### Recursos
- **CPU:** $cpu_values
- **Memória:** $memory_values

---

## 5. Conformidade com SLOs

### 5.1 URLLC
- **SLO Latência:** < 10-20 ms
- **SLO Erro:** < 0.1%
- **Status:** A ser avaliado com base nas métricas coletadas

### 5.2 eMBB
- **SLO Throughput:** Alto (dependente de configuração)
- **SLO Latência:** < 50 ms
- **Status:** A ser avaliado com base nas métricas coletadas

### 5.3 mMTC
- **SLO Conexões:** ≥ 10,000 dispositivos
- **SLO Latência:** < 100 ms
- **Status:** A ser avaliado com base nas métricas coletadas

---

## 6. Evidências Coletadas

### 6.1 Arquivos de Criação de Slices
\`\`\`
$(ls -1 "$OUTPUT_DIR"/scenario_*_create_*.json 2>/dev/null | sed 's|^|  - |' || echo "  Nenhum arquivo encontrado")
\`\`\`

### 6.2 Arquivos de Testes de Estresse
\`\`\`
$(ls -1 "$OUTPUT_DIR"/stress_test_*_results.json 2>/dev/null | sed 's|^|  - |' || echo "  Nenhum arquivo encontrado")
\`\`\`

### 6.3 Arquivos de Métricas Prometheus
\`\`\`
$(ls -1 "$OUTPUT_DIR"/prometheus_*.json 2>/dev/null | head -10 | sed 's|^|  - |' || echo "  Nenhum arquivo encontrado")
\`\`\`

---

## 7. Conclusões

### 7.1 Validação das Hipóteses

**H1:** A TriSLA mantém latência e confiabilidade dentro de SLO por cenário
- **Status:** Em análise com base nos dados coletados

**H2:** Os módulos SEM-NSMF/ML-NSMF/BC-NSSMF escalam de forma estável sem erros críticos
- **Status:** Em análise com base nos dados coletados

### 7.2 Próximos Passos

1. ✅ Análise detalhada dos arquivos JSON de métricas
2. ✅ Geração de gráficos e visualizações
3. ✅ Comparação com trabalhos relacionados
4. ✅ Atualização do documento de resultados para a dissertação

---

## 8. Referências aos Apêndices

- **Apêndice H (Logs e Métricas):** Arquivos em \`$OUTPUT_DIR\`
- **Apêndice F (Rastreabilidade):** Consultar logs de criação de slices
- **Apêndice A (Dados Experimentais):** Este documento e arquivos relacionados

---

**Gerado em:** $(date)  
**Versão:** 2.0  
**Autor:** Abel José Rodrigues Lisboa

EOF

echo "✅ Relatório gerado: $report_file"
echo ""

# Criar também um resumo em texto simples
summary_file="$OUTPUT_DIR/resumo_analise_${TIMESTAMP}.txt"
cat > "$summary_file" << EOF
===============================================
RESUMO DE ANÁLISE - TriSLA@NASP
===============================================
Data: $(date)
Timestamp: $TIMESTAMP

CRIAÇÃO DE SLICES:
------------------
URLLC: $([ $urllc_created -eq 1 ] && echo '✅' || echo '⚠️')
eMBB:  $([ $embb_created -eq 1 ] && echo '✅' || echo '⚠️')
mMTC:  $([ $mmtc_created -eq 1 ] && echo '✅' || echo '⚠️')

TESTES DE ESTRESSE:
-------------------
URLLC: $(echo "$urllc_stats" | cut -d'|' -f3)% sucesso
eMBB:  $(echo "$embb_stats" | cut -d'|' -f3)% sucesso
mMTC:  $(echo "$mmtc_stats" | cut -d'|' -f3)% sucesso

MÉTRICAS:
---------
CPU: $cpu_values
Memória: $memory_values
Latência p99: $latency_p99

ARQUIVOS GERADOS:
-----------------
Relatório completo: analise_resultados_${TIMESTAMP}.md
Este resumo: resumo_analise_${TIMESTAMP}.txt

===============================================
EOF

cat "$summary_file"
echo ""
echo "✅ Análise concluída!"
echo "📁 Arquivos gerados:"
echo "   - $report_file"
echo "   - $summary_file"
echo ""





