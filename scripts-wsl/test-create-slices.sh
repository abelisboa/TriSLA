#!/bin/bash
# ===========================================================
# 🧪 Script de Criação de Slices - TriSLA
# Cria slices via NLP para os três cenários: URLLC, eMBB, mMTC
# ===========================================================

API_URL="${API_URL:-http://localhost:5000}"
OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/docs/evidencias/WU-005_avaliacao}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Criar diretório de evidências se não existir
mkdir -p "$OUTPUT_DIR"

echo "==============================================="
echo "🧪 Teste de Criação de Slices - TriSLA"
echo "==============================================="
echo "API URL: $API_URL"
echo "Timestamp: $TIMESTAMP"
echo ""

# Função para criar slice via NLP
create_slice_nlp() {
    local scenario=$1
    local description=$2
    local output_file="$OUTPUT_DIR/scenario_${scenario}_create_${TIMESTAMP}.json"
    
    echo "📝 Criando slice ${scenario}: ${description}"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/slices" \
        -H "Content-Type: application/json" \
        -d "{\"descricao\": \"$description\"}" \
        --max-time 30)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Salvar resposta
    echo "$body" | jq . > "$output_file" 2>/dev/null || echo "$body" > "$output_file"
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ] || [ "$http_code" -eq 202 ]; then
        echo "✅ Slice ${scenario} criado com sucesso (HTTP $http_code)"
        echo "   Job ID: $(echo "$body" | jq -r '.job_id // .id // "N/A"' 2>/dev/null)"
        echo "   Arquivo: $output_file"
        return 0
    else
        echo "❌ Erro ao criar slice ${scenario} (HTTP $http_code)"
        echo "   Resposta: $body"
        return 1
    fi
}

# Função para verificar status do job
check_job_status() {
    local job_id=$1
    local max_wait=${2:-60}
    local wait_interval=${3:-5}
    local elapsed=0
    
    echo "   ⏳ Aguardando conclusão do job $job_id..."
    
    while [ $elapsed -lt $max_wait ]; do
        response=$(curl -s "$API_URL/api/v1/jobs/$job_id" --max-time 10)
        status=$(echo "$response" | jq -r '.status // "unknown"' 2>/dev/null)
        
        if [ "$status" = "finished" ] || [ "$status" = "complete" ] || [ "$status" = "completed" ]; then
            echo "   ✅ Job concluído: $status"
            return 0
        elif [ "$status" = "failed" ] || [ "$status" = "error" ]; then
            echo "   ❌ Job falhou: $status"
            return 1
        fi
        
        sleep $wait_interval
        elapsed=$((elapsed + wait_interval))
        echo -n "."
    done
    
    echo ""
    echo "   ⚠️ Timeout aguardando job $job_id"
    return 2
}

# Verificar se API está acessível
echo "🔍 Verificando conectividade com a API..."
health_check=$(curl -s "$API_URL/api/v1/health" --max-time 10)
if [ $? -ne 0 ]; then
    echo "❌ Erro: API não está acessível em $API_URL"
    echo "   Certifique-se de que o backend está rodando ou configure API_URL corretamente"
    exit 1
fi
echo "✅ API está acessível"

echo ""
echo "==============================================="
echo "📋 Criando Slices para os 3 Cenários"
echo "==============================================="
echo ""

# CENÁRIO 1: URLLC (Ultra-Reliable Low-Latency Communications)
echo "1️⃣ Cenário URLLC - Telemedicina / Cirurgia Remota"
URLLC_SUCCESS=$(create_slice_nlp "urllc" "cirurgia remota 5G com latência ultra baixa e alta confiabilidade para telemedicina")
URLLC_JOB=$(curl -s -X POST "$API_URL/api/v1/slices" \
    -H "Content-Type: application/json" \
    -d '{"descricao":"cirurgia remota 5G com latência ultra baixa e alta confiabilidade para telemedicina"}' \
    --max-time 30 | jq -r '.job_id // empty' 2>/dev/null)

if [ -n "$URLLC_JOB" ] && [ "$URLLC_JOB" != "null" ]; then
    check_job_status "$URLLC_JOB" 60 5
fi

echo ""

# CENÁRIO 2: eMBB (Enhanced Mobile Broadband)
echo "2️⃣ Cenário eMBB - Streaming 4K / Realidade Aumentada"
EMBB_SUCCESS=$(create_slice_nlp "embb" "streaming 4K e realidade aumentada com alta vazão de banda")
EMBB_JOB=$(curl -s -X POST "$API_URL/api/v1/slices" \
    -H "Content-Type: application/json" \
    -d '{"descricao":"streaming 4K e realidade aumentada com alta vazão de banda"}' \
    --max-time 30 | jq -r '.job_id // empty' 2>/dev/null)

if [ -n "$EMBB_JOB" ] && [ "$EMBB_JOB" != "null" ]; then
    check_job_status "$EMBB_JOB" 60 5
fi

echo ""

# CENÁRIO 3: mMTC (Massive Machine-Type Communications)
echo "3️⃣ Cenário mMTC - IoT Massivo / Sensores"
MMTC_SUCCESS=$(create_slice_nlp "mmtc" "sensores IoT industriais massivos com milhares de dispositivos")
MMTC_JOB=$(curl -s -X POST "$API_URL/api/v1/slices" \
    -H "Content-Type: application/json" \
    -d '{"descricao":"sensores IoT industriais massivos com milhares de dispositivos"}' \
    --max-time 30 | jq -r '.job_id // empty' 2>/dev/null)

if [ -n "$MMTC_JOB" ] && [ "$MMTC_JOB" != "null" ]; then
    check_job_status "$MMTC_JOB" 60 5
fi

echo ""
echo "==============================================="
echo "📊 Resumo da Criação de Slices"
echo "==============================================="
echo "URLLC: $([ $URLLC_SUCCESS -eq 0 ] && echo '✅ Sucesso' || echo '❌ Falhou')"
echo "eMBB:  $([ $EMBB_SUCCESS -eq 0 ] && echo '✅ Sucesso' || echo '❌ Falhou')"
echo "mMTC:  $([ $MMTC_SUCCESS -eq 0 ] && echo '✅ Sucesso' || echo '❌ Falhou')"
echo ""
echo "📁 Evidências salvas em: $OUTPUT_DIR"
echo ""

# Criar arquivo de resumo
summary_file="$OUTPUT_DIR/slices_creation_summary_${TIMESTAMP}.txt"
cat > "$summary_file" << EOF
===============================================
RESUMO DE CRIAÇÃO DE SLICES - TriSLA
===============================================
Data: $(date)
API URL: $API_URL
Timestamp: $TIMESTAMP

CENÁRIOS CRIADOS:
-----------------
1. URLLC (Telemedicina)
   Status: $([ $URLLC_SUCCESS -eq 0 ] && echo 'SUCESSO' || echo 'FALHA')
   Job ID: ${URLLC_JOB:-N/A}
   Descrição: cirurgia remota 5G com latência ultra baixa e alta confiabilidade

2. eMBB (Streaming 4K)
   Status: $([ $EMBB_SUCCESS -eq 0 ] && echo 'SUCESSO' || echo 'FALHA')
   Job ID: ${EMBB_JOB:-N/A}
   Descrição: streaming 4K e realidade aumentada com alta vazão de banda

3. mMTC (IoT Massivo)
   Status: $([ $MMTC_SUCCESS -eq 0 ] && echo 'SUCESSO' || echo 'FALHA')
   Job ID: ${MMTC_JOB:-N/A}
   Descrição: sensores IoT industriais massivos com milhares de dispositivos

ARQUIVOS GERADOS:
-----------------
$(ls -lh "$OUTPUT_DIR"/scenario_*_create_${TIMESTAMP}.json 2>/dev/null || echo "Nenhum arquivo JSON encontrado")

===============================================
EOF

echo "📄 Resumo salvo em: $summary_file"
echo ""
echo "✅ Teste de criação de slices concluído!"
echo ""





