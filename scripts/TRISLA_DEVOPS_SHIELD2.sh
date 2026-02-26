#!/usr/bin/env bash
set -euo pipefail

NS="trisla"
TS=$(date -u +%Y%m%dT%H%M%SZ)

echo "==============================================="
echo "TRISLA DEVOPS SHIELD — LEVEL 2 (Hard Mode)"
echo "Timestamp: $TS"
echo "==============================================="

echo
echo "FASE 1 — Detectar imagens sem tag explícita"
echo "--------------------------------------------"

BAD_IMAGES=0

kubectl get pods -n $NS -o jsonpath='{range .items[*]}{.metadata.name}{"|"}{.spec.containers[*].image}{"\n"}{end}' \
| while IFS="|" read -r pod image; do
    if [[ "$image" != *":"* ]]; then
        echo "ERRO: $pod usa imagem sem tag -> $image"
        BAD_IMAGES=1
    fi
    if [[ "$image" == *":latest" ]]; then
        echo "ERRO: $pod usa latest -> $image"
        BAD_IMAGES=1
    fi
done

if [[ $BAD_IMAGES -eq 1 ]]; then
    echo "ABORT: Imagens não determinísticas detectadas."
    exit 10
fi

echo "OK: Todas imagens possuem tag fixa."

echo
echo "FASE 2 — Limpeza segura de ReplicaSets órfãos"
echo "--------------------------------------------"

kubectl get rs -n $NS --no-headers \
| awk '$2==0 && $3==0 && $4==0 {print $1}' \
| while read rs; do
    echo "Removendo RS órfão: $rs"
    kubectl delete rs $rs -n $NS
done

echo
echo "FASE 3 — Validação final"
echo "--------------------------------------------"

kubectl get pods -n $NS

echo
echo "==============================================="
echo "HARD SHIELD: SISTEMA DETERMINÍSTICO"
echo "==============================================="
