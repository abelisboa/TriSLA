#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="trisla"
RELEASE="trisla"
CHART_PATH="helm/trisla"
LOG_DIR="evidencias_guardiao_deterministico"
TS=$(date -u +%Y%m%dT%H%M%SZ)
LOG_FILE="${LOG_DIR}/DEVOPS_SHIELD_${TS}.log"

mkdir -p "$LOG_DIR"

echo "==================================================" | tee "$LOG_FILE"
echo "TRISLA DEVOPS SHIELD — Blindagem Definitiva" | tee -a "$LOG_FILE"
echo "Timestamp: $TS" | tee -a "$LOG_FILE"
echo "Hostname: $(hostname)" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"

echo
echo "FASE 1 — Verificação de TAGs obrigatórias no values.yaml" | tee -a "$LOG_FILE"
echo "--------------------------------------------------" | tee -a "$LOG_FILE"

MISSING_TAG=0

while read -r repo_line; do
    tag_line=$(echo "$repo_line" | sed 's/repository:/tag:/')
    tag_value=$(grep -A1 "$repo_line" "$CHART_PATH/values.yaml" | grep tag | awk '{print $2}' || true)

    if [[ -z "$tag_value" ]]; then
        echo "ERRO: Tag ausente para $repo_line" | tee -a "$LOG_FILE"
        MISSING_TAG=1
    fi
done < <(grep "repository:" "$CHART_PATH/values.yaml")

if [[ $MISSING_TAG -eq 1 ]]; then
    echo "ABORT: Existem imagens sem tag definida." | tee -a "$LOG_FILE"
    exit 1
fi

echo "OK: Todas imagens possuem tag explícita." | tee -a "$LOG_FILE"

echo
echo "FASE 2 — Render Helm Dry-Run (anti-%!s(<nil>))" | tee -a "$LOG_FILE"
echo "--------------------------------------------------" | tee -a "$LOG_FILE"

RENDER_OUTPUT=$(helm template "$RELEASE" "$CHART_PATH" -n "$NAMESPACE")

if echo "$RENDER_OUTPUT" | grep -q "%!s(<nil>)"; then
    echo "ABORT: Renderização contém imagem inválida (%!s(<nil>))." | tee -a "$LOG_FILE"
    exit 2
fi

echo "OK: Renderização limpa." | tee -a "$LOG_FILE"

echo
echo "FASE 3 — Auditoria de Pods com erro" | tee -a "$LOG_FILE"
echo "--------------------------------------------------" | tee -a "$LOG_FILE"

BAD_PODS=$(kubectl get pods -n "$NAMESPACE" | egrep 'ImagePullBackOff|Err|Invalid|CrashLoopBackOff' || true)

if [[ -n "$BAD_PODS" ]]; then
    echo "ERRO: Existem pods em estado inválido:" | tee -a "$LOG_FILE"
    echo "$BAD_PODS" | tee -a "$LOG_FILE"
    exit 3
fi

echo "OK: Nenhum pod inválido." | tee -a "$LOG_FILE"

echo
echo "FASE 4 — Verificação de ReplicaSets órfãos ativos" | tee -a "$LOG_FILE"
echo "--------------------------------------------------" | tee -a "$LOG_FILE"

ORPHAN_RS=$(kubectl get rs -n "$NAMESPACE" --no-headers | awk '$2==0 && $3==0 && $4==0 {print $1}')

if [[ -n "$ORPHAN_RS" ]]; then
    echo "ReplicaSets inativos encontrados:" | tee -a "$LOG_FILE"
    echo "$ORPHAN_RS" | tee -a "$LOG_FILE"
    echo "Sugestão: kubectl delete rs <nome> -n $NAMESPACE" | tee -a "$LOG_FILE"
else
    echo "OK: Nenhum ReplicaSet órfão ativo." | tee -a "$LOG_FILE"
fi

echo
echo "FASE 5 — Validação de integridade das imagens em execução" | tee -a "$LOG_FILE"
echo "--------------------------------------------------" | tee -a "$LOG_FILE"

kubectl get pods -n "$NAMESPACE" -o jsonpath='{range .items[*]}{.metadata.name}{" -> "}{.spec.containers[*].image}{"\n"}{end}' \
| tee -a "$LOG_FILE"

echo
echo "FASE 6 — Política preventiva contra latest" | tee -a "$LOG_FILE"
echo "--------------------------------------------------" | tee -a "$LOG_FILE"

if grep -R "latest" "$CHART_PATH/values.yaml"; then
    echo "ABORT: Uso de 'latest' detectado." | tee -a "$LOG_FILE"
    exit 4
fi

echo "OK: Nenhuma imagem usando latest." | tee -a "$LOG_FILE"

echo
echo "==================================================" | tee -a "$LOG_FILE"
echo "DEVOPS SHIELD: STATUS = BLINDADO" | tee -a "$LOG_FILE"
echo "==================================================" | tee -a "$LOG_FILE"

exit 0
