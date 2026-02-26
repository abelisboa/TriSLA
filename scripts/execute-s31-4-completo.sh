#!/bin/bash
# Script Master - PROMPT_S31.4 - Release v3.9.8
# Executa todas as fases após o build/push

set -e

cd /home/porvir5g/gtp5g/trisla

echo '========================================'
echo 'PROMPT_S31.4 - Release v3.9.8 - Execução Completa'
echo '========================================'
echo ''

# Verificar se FASE 3 foi concluída (imagens existem)
echo 'Verificando se imagens v3.9.8 existem...'
if ! docker manifest inspect ghcr.io/abelisboa/trisla-decision-engine:v3.9.8 >/dev/null 2>&1; then
    echo '⚠️ ATENÇÃO: Imagens v3.9.8 não encontradas!'
    echo 'Execute primeiro: ./scripts/execute-fase3-build-push.sh'
    exit 1
fi

echo '✅ Imagens encontradas. Prosseguindo...'
echo ''

# FASE 5 - Rollout
echo '>>> Executando FASE 5 - Rollout <<<'
./scripts/execute-fase5-rollout.sh
echo ''

# FASE 6 - Verificação de Imagem
echo '>>> Executando FASE 6 - Verificação de Imagem <<<'
echo 'Deployment configurado para:'
kubectl get deploy -n trisla trisla-decision-engine -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'

echo 'Pods em execução:'
kubectl get pods -n trisla -l app=trisla-decision-engine -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.spec.containers[0].image}{"  "}{.status.phase}{"\n"}{end}'

# Verificar se há versões antigas
OLD_VERSIONS=$(kubectl get pods -n trisla -l app=trisla-decision-engine -o jsonpath='{range .items[*]}{.spec.containers[0].image}{"\n"}{end}' | grep -E 'v3\.9\.[0-6]|v3\.9\.7' || true)
if [ -n "$OLD_VERSIONS" ]; then
    echo '⚠️ ATENÇÃO: Pods com versões antigas detectadas!'
    echo "$OLD_VERSIONS"
    exit 1
fi

echo '✅ FASE 6 concluída - Todas as imagens são v3.9.8'
echo ''

# FASE 7 - Smoke Test
echo '>>> Executando FASE 7 - Smoke Test Kafka <<<'
./scripts/execute-fase7-smoke-test.sh
echo ''

# FASE 8 - Evidências Finais
echo '>>> Executando FASE 8 - Evidências Finais <<<'
OUT=/home/porvir5g/gtp5g/trisla/evidencias_release_v3.9.8/s31
mkdir -p $OUT

kubectl get pods -n trisla -o wide > $OUT/pods_final.txt
kubectl get deploy -n trisla > $OUT/deploy_final.txt
kubectl logs -n trisla deploy/trisla-decision-engine --tail=400 > $OUT/decision-engine_tail_final.log 2>&1 || true

kubectl get pods -n trisla -l app=trisla-decision-engine -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.spec.containers[0].image}{"\n"}{end}' > $OUT/decision-engine_images_final.txt

sha256sum $OUT/*.txt $OUT/*.log 2>/dev/null > $OUT/CHECKSUMS.sha256 || true

echo '✅ Evidências coletadas em: $OUT'
echo ''

echo '========================================'
echo '✅✅✅ PROMPT_S31.4 EXECUTADO COM SUCESSO! ✅✅✅'
echo '========================================'
