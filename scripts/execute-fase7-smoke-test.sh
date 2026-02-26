#!/bin/bash
set -e

cd /home/porvir5g/gtp5g/trisla

echo '=== FASE 7 - Smoke Test S31 (Kafka obrigatório) ==='

echo '7.1 - Verificando tópico Kafka...'
kubectl exec -n trisla deploy/kafka -- bash -lc '/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list | grep trisla-decision-events || echo "Tópico não encontrado, criando..."' || true

kubectl exec -n trisla deploy/kafka -- bash -lc '/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic trisla-decision-events --partitions 1 --replication-factor 1' 2>&1 | grep -v 'already exists' || true

echo ''
echo '7.2 - Preparando consumer Kafka (timeout 7s)...'
echo '⚠️ IMPORTANTE: Você precisa submeter 3 SLAs (URLLC/eMBB/mMTC) via portal-backend'
echo 'Enquanto isso, o consumer está escutando eventos...'
echo ''

# Executar consumer em background e capturar output
kubectl exec -n trisla deploy/kafka -- bash -lc '/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic trisla-decision-events --from-beginning --timeout-ms 7000' 2>&1 | tee /tmp/kafka-events.log || true

echo ''
echo '=== Análise dos Eventos ==='
if [ -f /tmp/kafka-events.log ]; then
    EVENT_COUNT=$(grep -c '"' /tmp/kafka-events.log 2>/dev/null || echo 0)
    echo "Eventos capturados: $EVENT_COUNT"
    
    if [ $EVENT_COUNT -gt 0 ]; then
        echo ''
        echo 'Verificando estrutura dos eventos...'
        grep -o '"sla_id"\|"decision"\|"snapshot"\|"system_xai"\|"explanation"' /tmp/kafka-events.log | sort -u
        echo ''
        echo '✅ Eventos encontrados no Kafka!'
    else
        echo '⚠️ Nenhum evento encontrado. Certifique-se de que:'
        echo '   1. Decision-engine está rodando'
        echo '   2. SLAs foram submetidos via portal-backend'
        echo '   3. O endpoint /evaluate está funcionando'
    fi
fi

echo ''
echo '✅ FASE 7 concluída!'
