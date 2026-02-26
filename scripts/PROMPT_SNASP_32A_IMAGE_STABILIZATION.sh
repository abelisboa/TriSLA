#!/usr/bin/env bash
set -euo pipefail

BASE="/home/porvir5g/gtp5g/trisla"
EVID="$BASE/evidencias_nasp/32A_image_stabilization"
RUNBOOK="$BASE/docs/TRISLA_MASTER_RUNBOOK.md"
TS=$(date -u +"%Y%m%dT%H%M%SZ")

mkdir -p "$EVID/00_gate" "$EVID/01_inventory" "$EVID/02_badpods" "$EVID/03_cleanup" "$EVID/04_validation" "$EVID/10_runbook_update"

echo "TS=$TS" | tee "$EVID/00_gate/metadata.txt"
echo "HOST=$(hostname)" | tee -a "$EVID/00_gate/metadata.txt"
kubectl version --short | tee "$EVID/00_gate/kubectl_version.txt" || true

echo "=== INVENTÁRIO (pods / owners / imagens) ==="
kubectl get pods -n trisla -o wide | tee "$EVID/01_inventory/pods_wide.txt"

# Lista pods ruins (tudo que NÃO deveria existir em ambiente estabilizado)
kubectl get pods -n trisla --no-headers | \
  awk '$3 ~ /(ImagePullBackOff|ErrImagePull|Error|CrashLoopBackOff|Init:|InvalidImageName)/ {print $1" "$3}' \
  | tee "$EVID/02_badpods/badpods.txt" || true

if [[ ! -s "$EVID/02_badpods/badpods.txt" ]]; then
  echo "OK: nenhum pod em estado ruim encontrado." | tee "$EVID/04_validation/result.txt"
  exit 0
fi

echo
echo "=== DETALHE dos pods ruins (describe) ==="
while read -r POD STATUS; do
  echo "--- $POD ($STATUS) ---" | tee -a "$EVID/02_badpods/describes.txt"
  kubectl describe pod -n trisla "$POD" | tee -a "$EVID/02_badpods/describes.txt" >/dev/null
done < "$EVID/02_badpods/badpods.txt"

echo
echo "=== CLASSIFICAÇÃO por OWNER ==="
# Para cada pod ruim, descobrir owner.
# Se owner for ReplicaSet/Job antigo (debug/test), deletar.
# Se owner for Deployment/StatefulSet "core", ABORT para corrigir no Helm/values (não deletar no escuro).

CORE_REGEX='trisla-(portal|decision|ml|sem|sla-agent|nasp-adapter|bc-nssmf|traffic-exporter|ui-dashboard|analytics-adapter|besu)'

ABORT_CORE=0

while read -r POD STATUS; do
  OWNER_KIND=$(kubectl get pod -n trisla "$POD" -o jsonpath='{.metadata.ownerReferences[0].kind}' 2>/dev/null || echo "")
  OWNER_NAME=$(kubectl get pod -n trisla "$POD" -o jsonpath='{.metadata.ownerReferences[0].name}' 2>/dev/null || echo "")
  IMG=$(kubectl get pod -n trisla "$POD" -o jsonpath='{.spec.containers[0].image}' 2>/dev/null || echo "")

  echo "$POD status=$STATUS owner=$OWNER_KIND/$OWNER_NAME image=$IMG" | tee -a "$EVID/03_cleanup/owner_map.txt"

  # Se não tem owner, é pod “solto”: deletar.
  if [[ -z "$OWNER_KIND" || -z "$OWNER_NAME" ]]; then
    echo "DELETE (standalone): $POD" | tee -a "$EVID/03_cleanup/actions.txt"
    kubectl delete pod -n trisla "$POD" --ignore-not-found | tee -a "$EVID/03_cleanup/actions.txt" >/dev/null || true
    continue
  fi

  # Jobs e pods de ferramentas: deletar o Job (e o pod junto).
  if [[ "$OWNER_KIND" == "Job" ]]; then
    echo "DELETE (job): $OWNER_NAME (pod $POD)" | tee -a "$EVID/03_cleanup/actions.txt"
    kubectl delete job -n trisla "$OWNER_NAME" --ignore-not-found | tee -a "$EVID/03_cleanup/actions.txt" >/dev/null || true
    continue
  fi

  # ReplicaSet antigo: deletar o pod; depois vamos validar se é RS core ou não.
  if [[ "$OWNER_KIND" == "ReplicaSet" ]]; then
    # Descobre deployment “pai” do RS, se existir
    PARENT_DEPLOY=$(kubectl get rs -n trisla "$OWNER_NAME" -o jsonpath='{.metadata.ownerReferences[0].name}' 2>/dev/null || echo "")
    if [[ -n "$PARENT_DEPLOY" && "$PARENT_DEPLOY" =~ $CORE_REGEX ]]; then
      echo "ABORT: RS de componente core em estado ruim: rs=$OWNER_NAME deploy=$PARENT_DEPLOY pod=$POD" | tee -a "$EVID/03_cleanup/actions.txt"
      ABORT_CORE=1
      continue
    fi
    echo "DELETE (replicaset old/non-core pod only): $POD (rs=$OWNER_NAME parent=$PARENT_DEPLOY)" | tee -a "$EVID/03_cleanup/actions.txt"
    kubectl delete pod -n trisla "$POD" --ignore-not-found | tee -a "$EVID/03_cleanup/actions.txt" >/dev/null || true
    continue
  fi

  # StatefulSet core com imagem inválida: abortar para correção via helm/values
  if [[ "$OWNER_KIND" == "StatefulSet" || "$OWNER_KIND" == "Deployment" ]]; then
    if [[ "$OWNER_NAME" =~ $CORE_REGEX ]]; then
      echo "ABORT: workload core com pod ruim: $OWNER_KIND/$OWNER_NAME (pod=$POD status=$STATUS image=$IMG)" | tee -a "$EVID/03_cleanup/actions.txt"
      ABORT_CORE=1
      continue
    fi
    echo "DELETE (non-core workload pod): $POD" | tee -a "$EVID/03_cleanup/actions.txt"
    kubectl delete pod -n trisla "$POD" --ignore-not-found | tee -a "$EVID/03_cleanup/actions.txt" >/dev/null || true
    continue
  fi

  # Default: deletar o pod, mas registrar
  echo "DELETE (fallback): $POD owner=$OWNER_KIND/$OWNER_NAME" | tee -a "$EVID/03_cleanup/actions.txt"
  kubectl delete pod -n trisla "$POD" --ignore-not-found | tee -a "$EVID/03_cleanup/actions.txt" >/dev/null || true

done < "$EVID/02_badpods/badpods.txt"

echo
echo "=== VALIDAÇÃO pós-cleanup ==="
kubectl get pods -n trisla -o wide | tee "$EVID/04_validation/pods_after.txt"

kubectl get pods -n trisla --no-headers | \
  awk '$3 ~ /(ImagePullBackOff|ErrImagePull|Error|CrashLoopBackOff|Init:|InvalidImageName)/ {print $1" "$3}' \
  | tee "$EVID/04_validation/badpods_after.txt" || true

if [[ -s "$EVID/04_validation/badpods_after.txt" ]]; then
  echo "FAIL: ainda existem pods em estado ruim. Verifique badpods_after.txt e describes.txt" | tee "$EVID/04_validation/result.txt"
else
  echo "PASS: namespace trisla sem pods ruins." | tee "$EVID/04_validation/result.txt"
fi

if [[ "$ABORT_CORE" -eq 1 ]]; then
  echo "ABORT_CORE=1: Existe workload core com imagem inválida/ruim. Corrigir via Helm/values (não deletar no escuro)." | tee -a "$EVID/04_validation/result.txt"
  exit 2
fi

HASH_BEFORE=$(sha256sum "$RUNBOOK" | awk '{print $1}')

cat <<EOF >> "$RUNBOOK"

### PROMPT_SNASP_32A — Image Stabilization & Garbage Cleanup

**Data:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

Ações:
- Inventário de pods e identificação de estados ruins (ImagePullBackOff/ErrImagePull/Error/Init:InvalidImageName).
- Remoção definitiva de pods/jobs/replicasets não-core (debug/test) que poluíam o namespace.
- Validação: namespace sem pods em estado ruim (quando PASS).

Evidências: evidencias_nasp/32A_image_stabilization/

EOF

HASH_AFTER=$(sha256sum "$RUNBOOK" | awk '{print $1}')
echo "RUNBOOK_HASH_BEFORE=$HASH_BEFORE" | tee -a "$EVID/10_runbook_update/hashes.txt"
echo "RUNBOOK_HASH_AFTER=$HASH_AFTER" | tee -a "$EVID/10_runbook_update/hashes.txt"
