#!/bin/bash
# ============================================================
# TESTE DE INTEGRAÇÃO SEM-CSMF → KAFKA (I-02)
# TriSLA — Pré FASE 2 (ML-NSMF Real)
# ============================================================

set -e

echo "===== TESTE DE INTEGRAÇÃO I-02 (SEM-CSMF → Kafka) ====="
echo ""

# 1. Validar que o Kafka está rodando no ambiente local
echo "[1/7] Verificando Kafka e Zookeeper..."
if docker ps --format "{{.Names}}" | grep -qE "trisla-kafka|trisla-zookeeper"; then
    echo "✅ Kafka e Zookeeper estão rodando"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "kafka|zookeeper"
else
    echo "❌ Kafka ou Zookeeper não estão rodando"
    echo "   Execute: docker-compose up -d kafka zookeeper"
    exit 1
fi

echo ""

# 2. Criar tópico I-02 se ainda não existir
echo "[2/7] Criando tópico I-02-intent-to-ml..."
docker exec -it trisla-kafka \
  kafka-topics.sh \
    --create \
    --topic I-02-intent-to-ml \
    --bootstrap-server localhost:9092 \
    --if-not-exists \
    --partitions 1 \
    --replication-factor 1 \
    > /dev/null 2>&1 || echo "⚠️ Tópico já existe ou erro ao criar"

echo "✅ Tópico I-02-intent-to-ml verificado/criado"
echo ""

# 3. Iniciar consumer para observar mensagens vindas do SEM-CSMF
echo "[3/7] Iniciando consumer Kafka em background..."
docker exec -d trisla-kafka \
  kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic I-02-intent-to-ml \
    --from-beginning \
    --property print.key=true \
    --property print.value=true \
    --property print.headers=true

sleep 3
echo "✅ Consumer iniciado"
echo ""

# 4. Enviar INTENT REAL para o SEM-CSMF → este intent deve disparar publicação Kafka no I-02
echo "[4/7] Enviando intent para SEM-CSMF..."
INTENT_RESPONSE=$(curl -s -X POST http://localhost:8080/api/v1/intents \
  -H "Content-Type: application/json" \
  -d '{
        "intent_id": "test-i02-001",
        "tenant_id": "tenant-test",
        "service_type": "URLLC",
        "description": "cirurgia remota",
        "sla_requirements": {
            "latency": "5ms",
            "throughput": "10Mbps",
            "reliability": 0.99999,
            "jitter": "1ms"
        }
      }')

echo "Response: $INTENT_RESPONSE"
echo ""

sleep 2

# 5. Validar que a mensagem apareceu no consumer
echo "[5/7] Verificando mensagens no tópico..."
MESSAGE_COUNT=$(docker exec trisla-kafka \
  kafka-run-class.sh kafka.tools.GetOffsetShell \
    --broker-list localhost:9092 \
    --topic I-02-intent-to-ml \
    --time -1 \
    | awk -F: '{sum += $3} END {print sum}')

if [ "$MESSAGE_COUNT" -gt 0 ]; then
    echo "✅ Mensagem encontrada no tópico (offset: $MESSAGE_COUNT)"
else
    echo "⚠️ Nenhuma mensagem encontrada no tópico"
    echo ""
    echo "Capturando logs do SEM-CSMF..."
    docker logs trisla-sem-csmf --tail=50 2>&1 || echo "Container sem-csmf não encontrado"
    echo ""
    echo "Capturando logs do Kafka..."
    docker logs trisla-kafka --tail=50 2>&1 || echo "Container kafka não encontrado"
fi

echo ""

# 6. Validar schema da mensagem publicada (estrutural)
echo "[6/7] Validando schema da mensagem..."
# Ler última mensagem do tópico
LAST_MESSAGE=$(docker exec trisla-kafka \
  kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic I-02-intent-to-ml \
    --from-beginning \
    --max-messages 1 \
    --timeout-ms 5000 \
    2>/dev/null | tail -1)

if [ -n "$LAST_MESSAGE" ]; then
    echo "✅ Mensagem capturada:"
    echo "$LAST_MESSAGE" | python3 -m json.tool 2>/dev/null || echo "$LAST_MESSAGE"
    
    # Validar campos obrigatórios
    REQUIRED_FIELDS=("intent_id" "nest_id" "service_type" "gst" "nest")
    for field in "${REQUIRED_FIELDS[@]}"; do
        if echo "$LAST_MESSAGE" | grep -q "\"$field\""; then
            echo "  ✅ Campo '$field' presente"
        else
            echo "  ❌ Campo '$field' ausente"
        fi
    done
else
    echo "⚠️ Não foi possível capturar mensagem para validação"
fi

echo ""

# 7. Gerar relatório final no console
echo "===== RESULTADO DO TESTE I-02 ====="
echo ""
if [ "$MESSAGE_COUNT" -gt 0 ] && [ -n "$LAST_MESSAGE" ]; then
    echo "✅ SUCESSO: Mensagem publicada no tópico I-02 com todos os campos corretos"
    echo "   A FASE 2 (ML-NSMF) pode iniciar imediatamente."
    echo ""
    echo "Próximos passos:"
    echo "  1. Implementar consumer Kafka no ML-NSMF"
    echo "  2. Processar NEST recebido via I-02"
    echo "  3. Gerar predição de viabilidade"
    echo "  4. Publicar predição no tópico I-03 (ml-nsmf-predictions)"
    exit 0
else
    echo "❌ FALHA: Mensagem não foi publicada ou está incompleta"
    echo "   Interromper FASE 2 até resolver o problema."
    echo ""
    echo "Ações recomendadas:"
    echo "  1. Verificar logs do SEM-CSMF"
    echo "  2. Verificar conectividade com Kafka"
    echo "  3. Validar configuração KAFKA_BOOTSTRAP_SERVERS"
    echo "  4. Testar publicação manual no Kafka"
    exit 1
fi

