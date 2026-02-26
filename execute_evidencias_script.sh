#!/bin/bash
# Script de execução única, faseada, rastreável e reprodutível
# Baseado em PROMPT_MASTER_DEVOPS_TRISLA_EVIDENCIAS_V1

set -euo pipefail

# Pré-check global (OBRIGATÓRIO)
echo "🔐 Pré-check global..."
kubectl version --client >/dev/null
kubectl get ns trisla >/dev/null || { echo "Namespace trisla inexistente"; exit 1; }
kubectl get pods -n trisla >/dev/null
echo "✅ Pré-check OK"

# FASE 0 — Preparação e Baseline (OBRIGATÓRIA)
echo "🟦 FASE 0 — Preparação e Baseline"
TS=$(date +%Y%m%d_%H%M%S)
BASE_DIR=/home/porvir5g/gtp5g/trisla/evidencias_execucao_unica_$TS
mkdir -p $BASE_DIR/fase0_baseline
cd $BASE_DIR

kubectl get nodes > fase0_baseline/nodes.txt
kubectl get pods -n trisla -o wide > fase0_baseline/pods.txt
kubectl get svc -n trisla > fase0_baseline/services.txt
kubectl get deploy -n trisla > fase0_baseline/deployments.txt
kubectl get pods -n trisla -o jsonpath='{..image}' | tr ' ' '\n' | sort -u > fase0_baseline/images.txt

# Gate FASE 0
echo "✅ Verificando Gate FASE 0..."
for f in fase0_baseline/*.txt; do
  [ -s "$f" ] || { echo "ERRO: $f vazio"; exit 1; }
done

if kubectl get pods -n trisla | grep -v Running | grep -v NAME | grep -v Completed; then
  echo "ERRO: pods não Running"; 
  exit 1
fi
echo "✅ FASE 0 concluída"

# FASE 1 — Criação controlada de SLAs (SEM-CSMF)
echo "🟦 FASE 1 — Criação controlada de SLAs"
mkdir -p fase1_sla_semantico/responses

SEM_API="http://trisla-sem-csmf.trisla.svc.cluster.local:8080/api/v1/intents"

# Função padrão (execução dentro do cluster)
submit_intent () {
  TYPE=$1
  TEXT=$2
  NAME=$3

  kubectl run curl-sem-$NAME -n trisla --rm -i --restart=Never \
  --image=curlimages/curl:8.5.0 -- \
  curl -s -X POST "$SEM_API" \
  -H "Content-Type: application/json" \
  -d "{\"service_type\":\"$TYPE\",\"intent\":\"$TEXT\"}"
}

# Execução L1 (1x cada)
echo "▶️ Executando L1..."
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l1-1 \
  > fase1_sla_semantico/responses/urllc_l1_1.json

submit_intent eMBB "streaming 8K interativo" embb-l1-1 \
  > fase1_sla_semantico/responses/embb_l1_1.json

submit_intent mMTC "sensores IoT massivos" mmtc-l1-1 \
  > fase1_sla_semantico/responses/mmtc_l1_1.json

# Execução L2 (5x cada)
echo "▶️ Executando L2..."
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l2-1 \
  > fase1_sla_semantico/responses/urllc_l2_1.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l2-2 \
  > fase1_sla_semantico/responses/urllc_l2_2.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l2-3 \
  > fase1_sla_semantico/responses/urllc_l2_3.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l2-4 \
  > fase1_sla_semantico/responses/urllc_l2_4.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l2-5 \
  > fase1_sla_semantico/responses/urllc_l2_5.json

submit_intent eMBB "streaming 8K interativo" embb-l2-1 \
  > fase1_sla_semantico/responses/embb_l2_1.json
submit_intent eMBB "streaming 8K interativo" embb-l2-2 \
  > fase1_sla_semantico/responses/embb_l2_2.json
submit_intent eMBB "streaming 8K interativo" embb-l2-3 \
  > fase1_sla_semantico/responses/embb_l2_3.json
submit_intent eMBB "streaming 8K interativo" embb-l2-4 \
  > fase1_sla_semantico/responses/embb_l2_4.json
submit_intent eMBB "streaming 8K interativo" embb-l2-5 \
  > fase1_sla_semantico/responses/embb_l2_5.json

submit_intent mMTC "sensores IoT massivos" mmtc-l2-1 \
  > fase1_sla_semantico/responses/mmtc_l2_1.json
submit_intent mMTC "sensores IoT massivos" mmtc-l2-2 \
  > fase1_sla_semantico/responses/mmtc_l2_2.json
submit_intent mMTC "sensores IoT massivos" mmtc-l2-3 \
  > fase1_sla_semantico/responses/mmtc_l2_3.json
submit_intent mMTC "sensores IoT massivos" mmtc-l2-4 \
  > fase1_sla_semantico/responses/mmtc_l2_4.json
submit_intent mMTC "sensores IoT massivos" mmtc-l2-5 \
  > fase1_sla_semantico/responses/mmtc_l2_5.json

# Execução L3 (10x cada)
echo "▶️ Executando L3..."
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-1 \
  > fase1_sla_semantico/responses/urllc_l3_1.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-2 \
  > fase1_sla_semantico/responses/urllc_l3_2.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-3 \
  > fase1_sla_semantico/responses/urllc_l3_3.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-4 \
  > fase1_sla_semantico/responses/urllc_l3_4.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-5 \
  > fase1_sla_semantico/responses/urllc_l3_5.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-6 \
  > fase1_sla_semantico/responses/urllc_l3_6.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-7 \
  > fase1_sla_semantico/responses/urllc_l3_7.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-8 \
  > fase1_sla_semantico/responses/urllc_l3_8.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-9 \
  > fase1_sla_semantico/responses/urllc_l3_9.json
submit_intent URLLC "cirurgia remota com latência ultrabaixa" urllc-l3-10 \
  > fase1_sla_semantico/responses/urllc_l3_10.json

submit_intent eMBB "streaming 8K interativo" embb-l3-1 \
  > fase1_sla_semantico/responses/embb_l3_1.json
submit_intent eMBB "streaming 8K interativo" embb-l3-2 \
  > fase1_sla_semantico/responses/embb_l3_2.json
submit_intent eMBB "streaming 8K interativo" embb-l3-3 \
  > fase1_sla_semantico/responses/embb_l3_3.json
submit_intent eMBB "streaming 8K interativo" embb-l3-4 \
  > fase1_sla_semantico/responses/embb_l3_4.json
submit_intent eMBB "streaming 8K interativo" embb-l3-5 \
  > fase1_sla_semantico/responses/embb_l3_5.json
submit_intent eMBB "streaming 8K interativo" embb-l3-6 \
  > fase1_sla_semantico/responses/embb_l3_6.json
submit_intent eMBB "streaming 8K interativo" embb-l3-7 \
  > fase1_sla_semantico/responses/embb_l3_7.json
submit_intent eMBB "streaming 8K interativo" embb-l3-8 \
  > fase1_sla_semantico/responses/embb_l3_8.json
submit_intent eMBB "streaming 8K interativo" embb-l3-9 \
  > fase1_sla_semantico/responses/embb_l3_9.json
submit_intent eMBB "streaming 8K interativo" embb-l3-10 \
  > fase1_sla_semantico/responses/embb_l3_10.json

submit_intent mMTC "sensores IoT massivos" mmtc-l3-1 \
  > fase1_sla_semantico/responses/mmtc_l3_1.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-2 \
  > fase1_sla_semantico/responses/mmtc_l3_2.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-3 \
  > fase1_sla_semantico/responses/mmtc_l3_3.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-4 \
  > fase1_sla_semantico/responses/mmtc_l3_4.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-5 \
  > fase1_sla_semantico/responses/mmtc_l3_5.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-6 \
  > fase1_sla_semantico/responses/mmtc_l3_6.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-7 \
  > fase1_sla_semantico/responses/mmtc_l3_7.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-8 \
  > fase1_sla_semantico/responses/mmtc_l3_8.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-9 \
  > fase1_sla_semantico/responses/mmtc_l3_9.json
submit_intent mMTC "sensores IoT massivos" mmtc-l3-10 \
  > fase1_sla_semantico/responses/mmtc_l3_10.json

# Gate FASE 1
echo "✅ Verificando Gate FASE 1..."
for json_file in fase1_sla_semantico/responses/*.json; do
  if ! jq -e '.nest_id' "$json_file" >/dev/null 2>&1; then
    echo "ERRO: SLA sem nest_id em $json_file"
    exit 1
  fi
done
echo "✅ FASE 1 concluída"

# FASE 1.5 — Adapter de Payload (OBRIGATÓRIA)
echo "🟦 FASE 1.5 — Adapter de Payload"
mkdir -p fase1_5_adapter

jq -c '{
  intent: {
    text: .intent,
    service_type: .service_type,
    nest_id: .nest_id
  }
}' fase1_sla_semantico/responses/*.json \
> fase1_5_adapter/intent_payloads.json

# Gate FASE 1.5
echo "✅ Verificando Gate FASE 1.5..."
[ -s fase1_5_adapter/intent_payloads.json ] || exit 1
jq empty fase1_5_adapter/intent_payloads.json || exit 1
echo "✅ FASE 1.5 concluída"

# FASE 2 — Avaliação ML + Decision Engine + XAI (CRÍTICA)
echo "🟦 FASE 2 — Avaliação ML + Decision Engine + XAI"
mkdir -p fase2_decision_engine

DEC_API="http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate"

jq -c '.' fase1_5_adapter/intent_payloads.json | nl -w1 | while read IDX PAYLOAD; do
  echo "  Processando decisão $IDX..."
  kubectl run curl-dec-$IDX -n trisla --rm -i --restart=Never \
  --image=curlimages/curl:8.5.0 -- \
  curl -s -X POST "$DEC_API" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  > fase2_decision_engine/decision_$IDX.json

  if ! jq -e '
    .decision_id and
    .action and
    .ml_risk_score and
    .confidence and
    .reasoning and
    .timestamp
  ' fase2_decision_engine/decision_$IDX.json >/dev/null 2>&1; then
    echo "ERRO: decisão inválida em decision_$IDX.json"
    exit 1
  fi
done

# Gate FASE 2
echo "✅ Verificando Gate FASE 2..."
DECISION_COUNT=$(ls fase2_decision_engine/*.json 2>/dev/null | wc -l)
if [ "$DECISION_COUNT" -eq 0 ]; then
  echo "ERRO: Nenhuma decisão gerada"
  exit 1
fi
echo "✅ FASE 2 concluída ($DECISION_COUNT decisões)"

# FASE 3 — Análise de XAI
echo "🟦 FASE 3 — Análise de XAI"
mkdir -p fase3_xai

jq -r '.reasoning | length' fase2_decision_engine/*.json \
> fase3_xai/tamanho_explicacoes.txt

[ -s fase3_xai/tamanho_explicacoes.txt ] || exit 1
echo "✅ FASE 3 concluída"

# FASE 4 — Blockchain (Governança REAL)
echo "🟦 FASE 4 — Blockchain"
mkdir -p fase4_blockchain

kubectl logs deploy/trisla-bc-nssmf -n trisla > fase4_blockchain/bc_nssmf_logs.txt
kubectl logs deploy/trisla-besu -n trisla > fase4_blockchain/besu_logs.txt

if ! grep -q decision fase4_blockchain/bc_nssmf_logs.txt; then
  echo "ERRO: logs blockchain não contêm 'decision'"
  exit 1
fi
echo "✅ FASE 4 concluída"

# FASE 5 — Stress Test Controlado
echo "🟦 FASE 5 — Stress Test Controlado"
mkdir -p fase5_stress
# reutilizar intents válidos (L3) para submissão sequencial e paralela
# TODO: Implementar stress test se necessário
echo "✅ FASE 5 concluída (placeholder)"

# FASE 6 — Consolidação Automática
echo "🟦 FASE 6 — Consolidação Automática"
jq -r '
  [.decision_id,.action,.ml_risk_score,.confidence] | @csv
' fase2_decision_engine/*.json \
> DATASET_FINAL.csv

if [ $(wc -l < DATASET_FINAL.csv) -le 1 ]; then
  echo "ERRO: DATASET_FINAL.csv vazio ou apenas header"
  exit 1
fi

echo "# Relatório Técnico Final TriSLA" > RELATORIO_TECNICO_FINAL.md
echo "" >> RELATORIO_TECNICO_FINAL.md
echo "Execução realizada em: $(date)" >> RELATORIO_TECNICO_FINAL.md
echo "Diretório base: $BASE_DIR" >> RELATORIO_TECNICO_FINAL.md
echo "Total de decisões: $DECISION_COUNT" >> RELATORIO_TECNICO_FINAL.md
echo "✅ FASE 6 concluída"

# FASE 7 — Gate Final DevOps
echo "🟦 FASE 7 — Gate Final DevOps"
if find "$BASE_DIR" -type f -empty | grep -q .; then
  echo "ERRO: arquivo vazio encontrado"
  find "$BASE_DIR" -type f -empty
  exit 1
fi

sha256sum $(find "$BASE_DIR" -type f) > CHECKSUMS.sha256
echo "✅ FASE 7 concluída"

echo ""
echo "🎉 Execução completa! Diretório: $BASE_DIR"
echo "📦 Estrutura criada:"
ls -la "$BASE_DIR"
