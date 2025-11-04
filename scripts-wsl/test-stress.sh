#!/bin/bash
# ===========================================================
# 🔥 Script de Teste de Estresse - TriSLA
# Executa múltiplas requisições simultâneas para testar capacidade
# ===========================================================

API_URL="${API_URL:-http://localhost:5000}"
OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/docs/evidencias/WU-005_avaliacao}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Configurações de teste
CONCURRENT_REQUESTS=${CONCURRENT_REQUESTS:-50}
TOTAL_REQUESTS=${TOTAL_REQUESTS:-200}
REQUEST_DELAY=${REQUEST_DELAY:-0.1}

mkdir -p "$OUTPUT_DIR"

echo "==============================================="
echo "🔥 Teste de Estresse - TriSLA"
echo "==============================================="
echo "API URL: $API_URL"
echo "Requisições simultâneas: $CONCURRENT_REQUESTS"
echo "Total de requisições: $TOTAL_REQUESTS"
echo "Delay entre requisições: ${REQUEST_DELAY}s"
echo "Timestamp: $TIMESTAMP"
echo ""

# Verificar se API está acessível
echo "🔍 Verificando conectividade com a API..."
health_check=$(curl -s "$API_URL/api/v1/health" --max-time 10)
if [ $? -ne 0 ]; then
    echo "❌ Erro: API não está acessível em $API_URL"
    exit 1
fi
echo "✅ API está acessível"
echo ""

# Função para fazer requisição e medir tempo
make_request() {
    local scenario=$1
    local request_num=$2
    local start_time=$(date +%s.%N)
    
    case $scenario in
        urllc)
            description="cirurgia remota 5G"
            ;;
        embb)
            description="streaming 4K alta vazão"
            ;;
        mmtc)
            description="sensores IoT massivos"
            ;;
        *)
            description="teste genérico"
            ;;
    esac
    
    response=$(curl -s -w "\n%{http_code}\n%{time_total}" -X POST "$API_URL/api/v1/slices" \
        -H "Content-Type: application/json" \
        -d "{\"descricao\": \"$description (stress test #$request_num)\"}" \
        --max-time 30 2>&1)
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    local http_code=$(echo "$response" | tail -n2 | head -n1)
    local time_total=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d' | sed '$d')
    
    # Retornar resultado como string delimitada por |
    echo "$request_num|$scenario|$http_code|$duration|$time_total|$(echo "$body" | jq -r '.job_id // .id // "N/A"' 2>/dev/null)"
}

# Função para executar requisições em paralelo
run_stress_test() {
    local scenario=$1
    local num_requests=$2
    local output_file="$OUTPUT_DIR/stress_test_${scenario}_${TIMESTAMP}.log"
    local results_file="$OUTPUT_DIR/stress_test_${scenario}_${TIMESTAMP}_results.json"
    
    echo "🔥 Iniciando teste de estresse para cenário: $scenario"
    echo "   Requisições: $num_requests"
    echo "   Arquivo de log: $output_file"
    
    local start_time=$(date +%s)
    local success_count=0
    local error_count=0
    local total_time=0
    local min_time=999
    local max_time=0
    
    # Array para armazenar resultados
    declare -a results
    
    # Executar requisições
    for i in $(seq 1 $num_requests); do
        # Executar requisição em background
        (
            result=$(make_request "$scenario" "$i")
            echo "$result" >> "$output_file"
        ) &
        
        # Controlar concorrência
        if [ $((i % CONCURRENT_REQUESTS)) -eq 0 ]; then
            wait
            echo -n "."
        fi
        
        sleep $REQUEST_DELAY
    done
    
    # Aguardar todas as requisições terminarem
    wait
    
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    
    echo ""
    echo "📊 Processando resultados..."
    
    # Processar resultados
    while IFS='|' read -r req_num scen http_code duration time_total job_id; do
        if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
            success_count=$((success_count + 1))
        else
            error_count=$((error_count + 1))
        fi
        
        duration_num=$(echo "$duration" | bc 2>/dev/null || echo "0")
        total_time=$(echo "$total_time + $duration_num" | bc 2>/dev/null || echo "$total_time")
        
        if (( $(echo "$duration_num < $min_time" | bc -l 2>/dev/null || echo 0) )); then
            min_time=$duration_num
        fi
        if (( $(echo "$duration_num > $max_time" | bc -l 2>/dev/null || echo 0) )); then
            max_time=$duration_num
        fi
        
        results+=("{\"request\":$req_num,\"scenario\":\"$scen\",\"http_code\":$http_code,\"duration\":$duration_num,\"job_id\":\"$job_id\"}")
    done < "$output_file"
    
    local avg_time=0
    if [ $success_count -gt 0 ]; then
        avg_time=$(echo "scale=3; $total_time / $success_count" | bc 2>/dev/null || echo "0")
    fi
    
    # Criar JSON de resultados
    local results_json="{\"scenario\":\"$scenario\",\"timestamp\":\"$TIMESTAMP\",\"total_requests\":$num_requests,\"concurrent\":$CONCURRENT_REQUESTS,\"duration_seconds\":$total_duration,\"success\":$success_count,\"errors\":$error_count,\"success_rate\":$(echo "scale=2; $success_count * 100 / $num_requests" | bc 2>/dev/null || echo "0"),\"avg_response_time\":$avg_time,\"min_response_time\":$min_time,\"max_response_time\":$max_time,\"requests_per_second\":$(echo "scale=2; $num_requests / $total_duration" | bc 2>/dev/null || echo "0"),\"results\":[$(IFS=','; echo "${results[*]}")]}"
    
    echo "$results_json" | jq . > "$results_file" 2>/dev/null || echo "$results_json" > "$results_file"
    
    echo "✅ Teste concluído para $scenario"
    echo "   Sucessos: $success_count / $num_requests"
    echo "   Erros: $error_count"
    echo "   Taxa de sucesso: $(echo "scale=2; $success_count * 100 / $num_requests" | bc)%"
    echo "   Tempo médio de resposta: ${avg_time}s"
    echo "   Requisições/segundo: $(echo "scale=2; $num_requests / $total_duration" | bc)"
    echo ""
}

echo "==============================================="
echo "🚀 Iniciando Testes de Estresse"
echo "==============================================="
echo ""

# Verificar se bc está instalado (para cálculos)
if ! command -v bc &> /dev/null; then
    echo "⚠️ Aviso: 'bc' não está instalado. Instalando..."
    sudo apt-get update && sudo apt-get install -y bc 2>/dev/null || {
        echo "❌ Não foi possível instalar 'bc'. Cálculos podem ser limitados."
    }
fi

# Executar testes para cada cenário
run_stress_test "urllc" $((TOTAL_REQUESTS / 3))
sleep 5

run_stress_test "embb" $((TOTAL_REQUESTS / 3))
sleep 5

run_stress_test "mmtc" $((TOTAL_REQUESTS / 3))

echo ""
echo "==============================================="
echo "📊 Resumo dos Testes de Estresse"
echo "==============================================="
echo ""

# Consolidar resultados
summary_file="$OUTPUT_DIR/stress_test_summary_${TIMESTAMP}.txt"
cat > "$summary_file" << EOF
===============================================
RESUMO DE TESTES DE ESTRESSE - TriSLA
===============================================
Data: $(date)
API URL: $API_URL
Timestamp: $TIMESTAMP

CONFIGURAÇÕES:
--------------
Requisições simultâneas: $CONCURRENT_REQUESTS
Total de requisições: $TOTAL_REQUESTS
Delay entre requisições: ${REQUEST_DELAY}s

RESULTADOS POR CENÁRIO:
-----------------------
$(for scen in urllc embb mmtc; do
    results_file="$OUTPUT_DIR/stress_test_${scen}_${TIMESTAMP}_results.json"
    if [ -f "$results_file" ]; then
        echo ""
        echo "$scen:"
        jq -r '"  Sucessos: \(.success) / \(.total_requests)",
                "  Erros: \(.errors)",
                "  Taxa de sucesso: \(.success_rate)%",
                "  Tempo médio: \(.avg_response_time)s",
                "  Min/Max: \(.min_response_time)s / \(.max_response_time)s",
                "  RPS: \(.requests_per_second)"' "$results_file" 2>/dev/null || cat "$results_file"
    fi
done)

ARQUIVOS GERADOS:
-----------------
$(ls -lh "$OUTPUT_DIR"/stress_test_*_${TIMESTAMP}* 2>/dev/null || echo "Nenhum arquivo encontrado")

===============================================
EOF

cat "$summary_file"

echo ""
echo "✅ Testes de estresse concluídos!"
echo "📁 Evidências salvas em: $OUTPUT_DIR"
echo ""





