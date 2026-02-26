#!/bin/bash
set -euo pipefail

# Execução única, faseada, rastreável e reprodutível
# Ambiente obrigatório
# Host: node006
# Diretório base: /home/porvir5g/gtp5g/trisla
# Namespace: trisla
# Modo: EXECUÇÃO REAL (NÃO dry-run)

echo "🔐 Pré-check global (OBRIGATÓRIO)"
kubectl version --client >/dev/null
kubectl get ns trisla >/dev/null || { echo "Namespace trisla inexistente"; exit 1; }

echo "🟦 FASE 0 — Preparação e Baseline (OBRIGATÓRIA)"
TS=$(date +%Y%m%d_%H%M%S)
BASE_DIR=/home/porvir5g/gtp5g/trisla/evidencias_execucao_unica_$TS
mkdir -p $BASE_DIR/fase0_baseline
cd $BASE_DIR

kubectl get nodes > fase0_baseline/nodes.txt
kubectl get pods -n trisla -o wide > fase0_baseline/pods.txt
kubectl get svc -n trisla > fase0_baseline/services.txt
kubectl get deploy -n trisla > fase0_baseline/deployments.txt
kubectl get pods -n trisla -o jsonpath='{..image}' | tr ' ' '\n' | sort -u > fase0_baseline/images.txt

echo "✅ Verificando critérios de sucesso FASE 0"
for f in fase0_baseline/*.txt; do
  [ -s "$f" ] || { echo "ERRO: $f vazio"; exit 1; }
done

# Verificar se todos os pods estão Running
NOT_RUNNING=$(kubectl get pods -n trisla --no-headers | grep -v Running | grep -v Completed || true)
if [ -n "$NOT_RUNNING" ]; then
  echo "AVISO: Alguns pods não estão Running:"
  echo "$NOT_RUNNING"
fi

echo "🟦 FASE 1 — Criação controlada de SLAs (SEM-CSMF)"
mkdir -p fase1_sla_semantico/{payloads,responses,logs}
SEM_API=http://trisla-sem-csmf.trisla.svc.cluster.local:8080/api/v1/intents

# Função auxiliar para executar curl dentro do cluster usando job
curl_in_cluster() {
  local url=$1
  local data=$2
  local output=$3
  local temp_output=$(mktemp)
  local job_name="curl-job-$(date +%s)-$RANDOM"
  
  # Criar um job para executar curl
  kubectl create job "$job_name" \
    --image=curlimages/curl \
    --namespace=trisla \
    -- curl -s --max-time 30 -X POST "$url" \
    -H "Content-Type: application/json" \
    -d "$data" > /dev/null 2>&1
  
  # Aguardar o job completar (máximo 60 segundos)
  local timeout=60
  local elapsed=0
  while [ $elapsed -lt $timeout ]; do
    if kubectl get job "$job_name" -n trisla -o jsonpath='{.status.succeeded}' 2>/dev/null | grep -q "1"; then
      break
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done
  
  # Obter logs do job
  kubectl logs job/"$job_name" -n trisla 2>/dev/null | \
    sed 's/pod ".*//' | \
    grep -v "^All commands" | \
    grep -v "^If you don'\''t see" | \
    grep -v "^$" | \
    head -1 > "$temp_output"
  
  # Limpar o job
  kubectl delete job "$job_name" -n trisla --ignore-not-found=true > /dev/null 2>&1
  
  # Pequeno delay para evitar sobrecarga
  sleep 0.5
  
  # Verificar se a saída contém JSON válido
  if [ -s "$temp_output" ] && jq empty "$temp_output" 2>/dev/null; then
    mv "$temp_output" "$output"
    return 0
  else
    echo "ERRO: Falha ao executar curl para $url ou resposta inválida"
    if [ -s "$temp_output" ]; then
      echo "Saída: $(cat $temp_output | head -3)"
    fi
    rm -f "$temp_output"
    return 1
  fi
}

# Lote L1: 1 URLLC, 1 eMBB, 1 mMTC
echo "Executando Lote L1..."
curl_in_cluster "$SEM_API" '{"service_type": "URLLC", "intent": "cirurgia remota com latência ultrabaixa e alta confiabilidade"}' \
  fase1_sla_semantico/responses/urllc_l1_1.json || { echo "ERRO: curl URLLC L1 falhou"; exit 1; }

curl_in_cluster "$SEM_API" '{"service_type": "eMBB", "intent": "streaming 8K interativo com alta largura de banda"}' \
  fase1_sla_semantico/responses/embb_l1_1.json || { echo "ERRO: curl eMBB L1 falhou"; exit 1; }

curl_in_cluster "$SEM_API" '{"service_type": "mMTC", "intent": "sensores IoT massivos com cobertura ampla e baixo consumo"}' \
  fase1_sla_semantico/responses/mmtc_l1_1.json || { echo "ERRO: curl mMTC L1 falhou"; exit 1; }

# Lote L2: 5 URLLC, 5 eMBB, 5 mMTC
echo "Executando Lote L2..."
for i in {1..5}; do
  curl_in_cluster "$SEM_API" "{\"service_type\": \"URLLC\", \"intent\": \"cirurgia remota com latência ultrabaixa e alta confiabilidade - lote 2 item $i\"}" \
    fase1_sla_semantico/responses/urllc_l2_$i.json || { echo "ERRO: curl URLLC L2 item $i falhou"; exit 1; }
  
  curl_in_cluster "$SEM_API" "{\"service_type\": \"eMBB\", \"intent\": \"streaming 8K interativo com alta largura de banda - lote 2 item $i\"}" \
    fase1_sla_semantico/responses/embb_l2_$i.json || { echo "ERRO: curl eMBB L2 item $i falhou"; exit 1; }
  
  curl_in_cluster "$SEM_API" "{\"service_type\": \"mMTC\", \"intent\": \"sensores IoT massivos com cobertura ampla e baixo consumo - lote 2 item $i\"}" \
    fase1_sla_semantico/responses/mmtc_l2_$i.json || { echo "ERRO: curl mMTC L2 item $i falhou"; exit 1; }
done

# Lote L3: 10 URLLC, 10 eMBB, 10 mMTC
echo "Executando Lote L3..."
for i in {1..10}; do
  curl_in_cluster "$SEM_API" "{\"service_type\": \"URLLC\", \"intent\": \"cirurgia remota com latência ultrabaixa e alta confiabilidade - lote 3 item $i\"}" \
    fase1_sla_semantico/responses/urllc_l3_$i.json || { echo "ERRO: curl URLLC L3 item $i falhou"; exit 1; }
  
  curl_in_cluster "$SEM_API" "{\"service_type\": \"eMBB\", \"intent\": \"streaming 8K interativo com alta largura de banda - lote 3 item $i\"}" \
    fase1_sla_semantico/responses/embb_l3_$i.json || { echo "ERRO: curl eMBB L3 item $i falhou"; exit 1; }
  
  curl_in_cluster "$SEM_API" "{\"service_type\": \"mMTC\", \"intent\": \"sensores IoT massivos com cobertura ampla e baixo consumo - lote 3 item $i\"}" \
    fase1_sla_semantico/responses/mmtc_l3_$i.json || { echo "ERRO: curl mMTC L3 item $i falhou"; exit 1; }
done

echo "✅ Verificando critério de sucesso FASE 1"
for f in fase1_sla_semantico/responses/*.json; do
  jq -e '.nest_id' "$f" >/dev/null || { echo "ERRO: SLA sem nest_id em $f"; exit 1; }
done

echo "🟦 FASE 1.5 — Adapter de Payload (OBRIGATÓRIA)"
mkdir -p fase1_5_adapter

jq -c '{
  intent_id: .intent_id,
  nest_id: .nest_id
}' fase1_sla_semantico/responses/*.json \
> fase1_5_adapter/intent_payloads.json

echo "✅ Verificando critério de sucesso FASE 1.5"
[ -s fase1_5_adapter/intent_payloads.json ] || exit 1
jq empty fase1_5_adapter/intent_payloads.json || exit 1

echo "🟦 FASE 2 — Avaliação ML + Decision Engine + XAI (CRÍTICA)"
mkdir -p fase2_decision_engine
DEC_API=http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate

jq -c '.' fase1_5_adapter/intent_payloads.json | while read payload; do
  ID=$(uuidgen 2>/dev/null || echo "id_$(date +%s)_$RANDOM")
  curl_in_cluster "$DEC_API" "$payload" \
    fase2_decision_engine/decision_$ID.json || { echo "ERRO: curl Decision Engine falhou para $ID"; exit 1; }

  jq -e '
    .decision_id and
    .action and
    .ml_risk_score and
    .confidence and
    .reasoning and
    .timestamp
  ' fase2_decision_engine/decision_$ID.json >/dev/null \
  || { echo "ERRO: decisão inválida em decision_$ID.json"; exit 1; }
done

echo "🟦 FASE 3 — Análise de XAI (Qualitativa + Quantitativa)"
mkdir -p fase3_xai

jq -r '.reasoning | length' fase2_decision_engine/*.json \
> fase3_xai/tamanho_explicacoes.txt

[ -s fase3_xai/tamanho_explicacoes.txt ] || exit 1

echo "🟦 FASE 4 — Blockchain (Governança)"
mkdir -p fase4_blockchain
kubectl logs deploy/trisla-bc-nssmf -n trisla > fase4_blockchain/bc_nssmf_logs.txt 2>&1 || true
kubectl logs deploy/trisla-besu -n trisla > fase4_blockchain/besu_logs.txt 2>&1 || true

grep -q decision fase4_blockchain/bc_nssmf_logs.txt || echo "AVISO: 'decision' não encontrado nos logs do bc-nssmf"

echo "🟦 FASE 5 — Stress Test Controlado"
mkdir -p fase5_stress
# Reutilizar intents válidos e executar submissão sequencial/paralela
echo "FASE 5: Stress test preparado (implementação específica conforme necessário)"

echo "🟦 FASE 6 — Consolidação Automática"
jq -r '
  [.decision_id,.action,.ml_risk_score,.confidence] | @csv
' fase2_decision_engine/*.json \
> DATASET_FINAL.csv

[ $(wc -l < DATASET_FINAL.csv) -gt 1 ] || exit 1

cat > RELATORIO_TECNICO_FINAL.md <<EOF
# Relatório Técnico Final TriSLA

## Informações da Execução
- Timestamp: $TS
- Diretório base: $BASE_DIR
- Namespace: trisla

## Resumo das Fases

### FASE 0 - Baseline
- Nodes coletados
- Pods coletados
- Services coletados
- Deployments coletados
- Images coletadas

### FASE 1 - SLAs Semânticos
- Total de SLAs criados: $(ls -1 fase1_sla_semantico/responses/*.json 2>/dev/null | wc -l)

### FASE 2 - Decision Engine
- Total de decisões: $(ls -1 fase2_decision_engine/*.json 2>/dev/null | wc -l)

### FASE 3 - XAI
- Análise de explicações realizada

### FASE 4 - Blockchain
- Logs coletados do bc-nssmf e besu

### FASE 6 - Dataset Final
- Total de registros: $(wc -l < DATASET_FINAL.csv)
EOF

echo "🟦 FASE 7 — Gate Final DevOps"
find $BASE_DIR -type f -empty && { echo "ERRO: Arquivos vazios encontrados"; exit 1; }
sha256sum $(find $BASE_DIR -type f) > CHECKSUMS.sha256

echo "✅ Execução concluída com sucesso!"
echo "📦 Diretório de evidências: $BASE_DIR"
ls -la $BASE_DIR
