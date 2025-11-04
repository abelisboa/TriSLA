#!/bin/bash
# ===========================================================
# 🚀 Script Completo de Testes - TriSLA
# Executa todos os testes: criação de slices, estresse, coleta de métricas e análise
# ===========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/docs/evidencias/WU-005_avaliacao}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Configurações
API_URL="${API_URL:-http://localhost:5000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
NAMESPACE="${NAMESPACE:-trisla-nsp}"

# Configurações de teste de estresse
CONCURRENT_REQUESTS=${CONCURRENT_REQUESTS:-30}
TOTAL_REQUESTS=${TOTAL_REQUESTS:-150}

echo "==============================================="
echo "🚀 Testes Completos - TriSLA@NASP"
echo "==============================================="
echo "Data: $(date)"
echo "API URL: $API_URL"
echo "Prometheus URL: $PROMETHEUS_URL"
echo "Namespace: $NAMESPACE"
echo ""

# Verificar dependências
echo "🔍 Verificando dependências..."
missing_deps=0

for cmd in curl jq bc; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ $cmd não encontrado"
        missing_deps=1
    else
        echo "✅ $cmd instalado"
    fi
done

if [ $missing_deps -eq 1 ]; then
    echo ""
    echo "⚠️ Algumas dependências estão faltando. Instalando..."
    sudo apt-get update && sudo apt-get install -y curl jq bc 2>/dev/null || {
        echo "❌ Não foi possível instalar dependências automaticamente"
        echo "   Instale manualmente: sudo apt-get install curl jq bc"
        exit 1
    }
fi

echo ""
echo "==============================================="
echo "📋 Executando Sequência de Testes"
echo "==============================================="
echo ""

# PASSO 1: Criar slices
echo "1️⃣ PASSO 1: Criando Slices"
echo "-------------------------------------------"
cd "$SCRIPT_DIR"
bash test-create-slices.sh
CREATE_SLICES_STATUS=$?
echo ""

if [ $CREATE_SLICES_STATUS -ne 0 ]; then
    echo "⚠️ Aviso: Alguns slices podem não ter sido criados corretamente"
    echo "   Continuando com os próximos testes..."
fi

# Aguardar um pouco para garantir que os slices foram processados
echo "⏳ Aguardando 10 segundos para processamento dos slices..."
sleep 10

# PASSO 2: Testes de estresse
echo ""
echo "2️⃣ PASSO 2: Testes de Estresse"
echo "-------------------------------------------"
cd "$SCRIPT_DIR"
CONCURRENT_REQUESTS=$CONCURRENT_REQUESTS TOTAL_REQUESTS=$TOTAL_REQUESTS bash test-stress.sh
STRESS_TEST_STATUS=$?
echo ""

if [ $STRESS_TEST_STATUS -ne 0 ]; then
    echo "⚠️ Aviso: Testes de estresse podem ter tido problemas"
    echo "   Continuando com a coleta de métricas..."
fi

# PASSO 3: Coletar métricas do Prometheus
echo ""
echo "3️⃣ PASSO 3: Coletando Métricas do Prometheus"
echo "-------------------------------------------"
cd "$SCRIPT_DIR"
PROMETHEUS_URL=$PROMETHEUS_URL NAMESPACE=$NAMESPACE bash collect-prometheus-metrics.sh
METRICS_STATUS=$?
echo ""

if [ $METRICS_STATUS -ne 0 ]; then
    echo "⚠️ Aviso: Algumas métricas podem não ter sido coletadas"
    echo "   Verifique se o Prometheus está acessível e o túnel SSH está ativo"
fi

# PASSO 4: Analisar resultados
echo ""
echo "4️⃣ PASSO 4: Analisando Resultados"
echo "-------------------------------------------"
cd "$SCRIPT_DIR"
bash analyze-results.sh
ANALYSIS_STATUS=$?
echo ""

# Resumo final
echo ""
echo "==============================================="
echo "📊 Resumo da Execução"
echo "==============================================="
echo ""
echo "Criação de Slices:      $([ $CREATE_SLICES_STATUS -eq 0 ] && echo '✅ Sucesso' || echo '⚠️ Com problemas')"
echo "Testes de Estresse:     $([ $STRESS_TEST_STATUS -eq 0 ] && echo '✅ Sucesso' || echo '⚠️ Com problemas')"
echo "Coleta de Métricas:     $([ $METRICS_STATUS -eq 0 ] && echo '✅ Sucesso' || echo '⚠️ Com problemas')"
echo "Análise de Resultados:  $([ $ANALYSIS_STATUS -eq 0 ] && echo '✅ Sucesso' || echo '⚠️ Com problemas')"
echo ""
echo "📁 Todas as evidências foram salvas em:"
echo "   $OUTPUT_DIR"
echo ""
echo "📄 Arquivos principais gerados:"
ls -1 "$OUTPUT_DIR"/*${TIMESTAMP}* 2>/dev/null | head -5 | sed 's|^|   - |' || echo "   (verifique o diretório de evidências)"
echo ""

# Criar arquivo de índice
index_file="$OUTPUT_DIR/INDICE_TESTES_${TIMESTAMP}.txt"
cat > "$index_file" << EOF
===============================================
ÍNDICE DE TESTES - TriSLA@NASP
===============================================
Data: $(date)
Timestamp: $TIMESTAMP

ARQUIVOS GERADOS:
-----------------
$(ls -lh "$OUTPUT_DIR"/*${TIMESTAMP}* 2>/dev/null | awk '{print $9, "(" $5 ")"}' || echo "Nenhum arquivo encontrado")

PRÓXIMOS PASSOS:
----------------
1. Revisar relatório de análise: analise_resultados_${TIMESTAMP}.md
2. Verificar métricas do Prometheus nos arquivos JSON
3. Analisar resultados dos testes de estresse
4. Atualizar documento de resultados para dissertação

===============================================
EOF

echo "📑 Índice criado: $index_file"
echo ""
echo "✅ Execução completa dos testes concluída!"
echo ""
echo "💡 Para atualizar o documento de resultados da dissertação, execute:"
echo "   bash scripts-wsl/update-dissertation-results.sh"
echo ""





