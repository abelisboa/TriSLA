#!/bin/bash
set -e

cd /home/porvir5g/gtp5g/trisla

echo '=== FASE 5 - Verificando Rollout ==='
echo 'Status atual dos pods decision-engine:'
kubectl get pods -n trisla | grep decision-engine

echo ''
echo 'Aguardando rollout do decision-engine (timeout 300s)...'
kubectl rollout status deploy/trisla-decision-engine -n trisla --timeout=300s || {
    echo '⚠️ Rollout pode estar preso. Verificando pods...'
    kubectl get pods -n trisla | grep decision-engine
    
    echo 'Forçando substituição de pods antigos se necessário...'
    kubectl delete pod -n trisla -l app=trisla-decision-engine --force --grace-period=0 2>&1 || true
    
    echo 'Aguardando novamente...'
    kubectl rollout status deploy/trisla-decision-engine -n trisla --timeout=300s
}

echo ''
echo '=== Verificação Final ==='
kubectl get pods -n trisla | grep decision-engine
kubectl get deploy -n trisla trisla-decision-engine -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
kubectl get pods -n trisla -l app=trisla-decision-engine -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.spec.containers[0].image}{"\n"}{end}'

echo ''
echo '✅ FASE 5 concluída!'
