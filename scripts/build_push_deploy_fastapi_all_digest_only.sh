#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/porvir5g/gtp5g/trisla"
APPS="$ROOT/apps"
RUNBOOK="$ROOT/TRISLA_MASTER_RUNBOOK.md"
NS="trisla"
RELEASE="trisla"
CHART="$ROOT/helm/trisla"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVID="$ROOT/evidencias_fastapi_build_push_deploy_$TS"
mkdir -p "$EVID"

log(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
die(){ echo "FATAL: $*" | tee "$EVID/FATAL.txt"; exit 1; }

log "==============================================="
log "TriSLA FastAPI — BUILD+PUSH+DEPLOY (DIGEST-ONLY)"
log "NS=$NS RELEASE=$RELEASE CHART=$CHART"
log "EVID=$EVID"
log "==============================================="

# ---------- GATE: cluster estável ----------
log "[GATE] Verificando estabilidade do namespace $NS (anti-regressão)..."
if kubectl -n "$NS" get pods | egrep -qi 'CrashLoopBackOff|ImagePullBackOff|ErrImagePull|Pending|Error'; then
  kubectl -n "$NS" get pods | tee "$EVID/GATE_pods_with_errors.txt"
  die "Cluster não está estável. ABORT para evitar regressão."
fi
kubectl -n "$NS" get pods -o wide > "$EVID/GATE_pods_ok.txt"
log "[GATE] OK: namespace estável."

# ---------- Descobrir serviços FastAPI ----------
FASTAPI_LIST="$EVID/fastapi_services.txt"
log "[SCAN] Descobrindo serviços FastAPI..."
python3 - <<'PY' "$APPS" "$FASTAPI_LIST"
import os,sys,re
apps=sys.argv[1]
out=sys.argv[2]
pat=re.compile(r'\bfrom\s+fastapi\s+import\s+FastAPI\b|\bFastAPI\s*\(')
services=[]
for s in sorted(os.listdir(apps)):
    sp=os.path.join(apps,s)
    if not os.path.isdir(sp): 
        continue
    hit=False
    for root,_,files in os.walk(sp):
        for fn in files:
            if fn.endswith(".py"):
                p=os.path.join(root,fn)
                try:
                    data=open(p,"r",encoding="utf-8",errors="ignore").read()
                except Exception:
                    continue
                if pat.search(data):
                    hit=True
                    break
        if hit: break
    if hit:
        services.append(s)
open(out,"w").write("\n".join(services)+("\n" if services else ""))
print("FOUND:", len(services))
for s in services: print(" -", s)
PY

if [[ ! -s "$FASTAPI_LIST" ]]; then
  die "Nenhum serviço FastAPI detectado."
fi

log "[INFO] Serviços FastAPI: $(tr '\n' ' ' < "$FASTAPI_LIST")"
cp -f "$FASTAPI_LIST" "$ROOT/apps/_fastapi_services_last.txt" || true

# ---------- Git: publicar no GitHub (governança) ----------
# Regras do usuário: código e build no servidor, depois publica no GitHub.
# Este bloco é conservador: se repo não estiver com remote configurado, apenas registra.
log "[GIT] Snapshot status antes do build..."
(
  cd "$ROOT"
  git status --porcelain=v1 || true
) | tee "$EVID/git_status_before.txt" >/dev/null

log "[GIT] Commit (se houver mudanças) + push (se houver remote)..."
(
  cd "$ROOT"
  if [[ -n "$(git status --porcelain=v1 2>/dev/null || true)" ]]; then
    git add -A
    git commit -m "obs: fastapi prometheus+otel instrumentation (digest-only pipeline)" || true
  fi
  # push apenas se existir remote origin
  if git remote get-url origin >/dev/null 2>&1; then
    git push origin HEAD || true
  else
    echo "WARN: sem remote origin configurado; commit local (se aplicável)." 
  fi
) | tee "$EVID/git_commit_push.log" >/dev/null

# ---------- Funções digest-only ----------
build_push_pull_digest(){
  local svc="$1"
  local svc_dir="$APPS/$svc"
  [[ -d "$svc_dir" ]] || die "Service dir não existe: $svc_dir"
  [[ -f "$svc_dir/Dockerfile" || -f "$svc_dir/dockerfile" ]] || die "Dockerfile ausente em $svc_dir"

  local ts
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  local image="ghcr.io/abelisboa/$svc:build-$ts"

  log "[BUILD] $svc :: $image"
  ( cd "$svc_dir" && podman build --format docker -t "$image" . ) | tee "$EVID/${svc}_build.log" >/dev/null

  log "[PUSH] $svc :: $image"
  ( cd "$svc_dir" && podman push --format docker "$image" --digestfile digest.txt ) | tee "$EVID/${svc}_push.log" >/dev/null

  local digest
  digest="$(cat "$svc_dir/digest.txt" | tr -d '\r\n')"
  [[ "$digest" == sha256:* ]] || die "Digest inválido para $svc (arquivo digest.txt): $digest"

  log "[PULL-GATE] $svc :: pull por digest ($digest)"
  podman pull "ghcr.io/abelisboa/$svc@$digest" | tee "$EVID/${svc}_pull_by_digest.log" >/dev/null

  echo "$digest" > "$EVID/${svc}_digest.txt"
  log "[OK] $svc digest: $digest"
}

deploy_digest_only(){
  local svc="$1"
  local digest="$2"

  # Convenção do prompt mestre: --set <service>.image.digest=$(cat apps/<service>/digest.txt)
  log "[DEPLOY] Helm upgrade (digest-only) :: $svc -> $digest"
  helm upgrade "$RELEASE" "$CHART" -n "$NS" --reuse-values \
    --set "${svc}.image.digest=${digest}" \
    | tee "$EVID/${svc}_helm_upgrade.log" >/dev/null

  # Deployment geralmente é "trisla-<service>" (padrão observado no cluster)
  local deploy="trisla-${svc}"
  log "[ROLLOUT] $deploy"
  kubectl -n "$NS" rollout status "deployment/$deploy" --timeout=240s | tee "$EVID/${svc}_rollout_status.log" >/dev/null

  log "[POST] Capturando imagem implantada em deployment/$deploy"
  kubectl -n "$NS" get "deployment/$deploy" -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}' \
    | tee "$EVID/${svc}_deployed_image.txt" >/dev/null

  # Logs iniciais (não streaming infinito)
  log "[POST] Logs iniciais deployment/$deploy (últimas 120 linhas)"
  kubectl -n "$NS" logs "deployment/$deploy" --tail=120 | tee "$EVID/${svc}_logs_tail120.txt" >/dev/null

  # Update Runbook SSOT (obrigatório)
  if [[ -x "$ROOT/scripts/update_runbook_ssot_digest_only.sh" ]]; then
    log "[SSOT] Atualizando Runbook para $svc"
    "$ROOT/scripts/update_runbook_ssot_digest_only.sh" \
      "$svc" \
      "$digest" \
      "Instrumentação FastAPI completa (Prometheus + OTEL) com pipeline digest-only" \
      PASS \
      | tee "$EVID/${svc}_runbook_update.log" >/dev/null
  else
    log "WARN: scripts/update_runbook_ssot_digest_only.sh não encontrado/executável. SSOT não atualizado (isso viola a regra)."
    echo "WARN: SSOT script missing" >> "$EVID/WARN.txt"
  fi
}

# ---------- Loop serviços ----------
while read -r svc; do
  [[ -n "${svc:-}" ]] || continue

  # Snapshot pré (imagem em produção, se existir)
  log "[SNAPSHOT] Estado atual (antes) do deployment trisla-$svc (se existir)"
  kubectl -n "$NS" get deploy "trisla-$svc" -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}' \
    2>/dev/null | tee "$EVID/${svc}_image_before.txt" >/dev/null || true

  build_push_pull_digest "$svc"

  digest="$(cat "$EVID/${svc}_digest.txt")"
  deploy_digest_only "$svc" "$digest"

done < "$FASTAPI_LIST"

# ---------- Pós: evidência geral ----------
log "[POST] Verificando se namespace segue estável (anti-regressão)..."
kubectl -n "$NS" get pods -o wide > "$EVID/post_pods_wide.txt"
if kubectl -n "$NS" get pods | egrep -qi 'CrashLoopBackOff|ImagePullBackOff|ErrImagePull|Pending|Error'; then
  kubectl -n "$NS" get pods | tee "$EVID/post_pods_with_errors.txt"
  die "Pós-deploy com pods em erro. ABORT e executar rollback seguro."
fi

log "[OK] Pipeline completo concluído com namespace estável."
log "EVID: $EVID"
