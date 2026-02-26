#!/usr/bin/env bash
set -euo pipefail

# ==========================================================
# TriSLA — Digest-Aware Helm Helper + Cluster Compliance
# Objetivo:
#   - Tornar helper trisla.image digest-aware
#   - Permitir fixar imagens via digest apenas via values.yaml
#   - Aplicar compliance total no cluster sem regressão
# Componentes alvo:
#   BC-NSSMF, ML-NSMF, Decision Engine, SEM-CSMF,
#   SLA-Agent Layer, UI Dashboard, Traffic Exporter, Kafka
# ==========================================================

NS="${NS:-trisla}"
RELEASE="${RELEASE:-trisla}"
CHART_DIR="${CHART_DIR:-/home/porvir5g/gtp5g/trisla/helm/trisla}"
VALUES_FILE="${VALUES_FILE:-$CHART_DIR/values.yaml}"
RUNBOOK="${RUNBOOK:-/home/porvir5g/gtp5g/trisla/TRISLA_MASTER_RUNBOOK.md}"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="${BACKUP_DIR:-/home/porvir5g/gtp5g/trisla/evidencias_release_digest/$STAMP}"
mkdir -p "$BACKUP_DIR"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || fail "comando ausente: $1"; }

need helm
need kubectl
need grep
need sed
need awk
need diff
need mktemp
need tar
need sort
need tee
need head
need tr

log "=========================================================="
log "TriSLA DIGEST-AWARE PATCH + COMPLIANCE"
log "Namespace: $NS | Release: $RELEASE"
log "Chart: $CHART_DIR"
log "Values: $VALUES_FILE"
log "Runbook: $RUNBOOK"
log "Evidências: $BACKUP_DIR"
log "=========================================================="

# -------------------------------
# 0) Sanity + backups
# -------------------------------
[ -d "$CHART_DIR" ] || fail "CHART_DIR não existe: $CHART_DIR"
[ -f "$VALUES_FILE" ] || fail "VALUES_FILE não existe: $VALUES_FILE"

HELPERS="$CHART_DIR/templates/_helpers.tpl"
[ -f "$HELPERS" ] || fail "_helpers.tpl não encontrado em: $HELPERS"

log "[0/7] Backup de segurança"
cp -a "$VALUES_FILE" "$BACKUP_DIR/values.yaml.bak"
cp -a "$HELPERS" "$BACKUP_DIR/_helpers.tpl.bak"
tar -czf "$BACKUP_DIR/chart_templates.tgz" -C "$CHART_DIR" templates >/dev/null 2>&1 || true

# -------------------------------
# 1) Captura helper atual
# -------------------------------
log "[1/7] Capturando função atual trisla.image (se existir)"
if grep -n 'define "trisla.image"' -n "$HELPERS" >/dev/null 2>&1; then
  awk '
    $0 ~ /define "trisla.image"/ {p=1}
    p==1 {print}
    p==1 && $0 ~ /end/ {exit}
  ' "$HELPERS" > "$BACKUP_DIR/trisla.image.before.tpl"
else
  echo "NOT_FOUND" > "$BACKUP_DIR/trisla.image.before.tpl"
fi

# -------------------------------
# 2) Patch digest-aware no helper
# -------------------------------
log "[2/7] Aplicando patch digest-aware em trisla.image (idempotente)"

# Função alvo (modelo final)
# FIX: removido "read -d ''" para evitar travamento; usar heredoc via cat (robusto)
NEW_TRISLA_IMAGE_FUNC="$(
cat <<'EOF'
{{- define "trisla.image" -}}
{{- /*
TriSLA image resolver (digest-aware)

Prioridade:
  1) image.full (override total) -> usa exatamente como fornecido (com tag ou digest)
  2) image.repository + image.digest -> repository@sha256:...
  3) global.imageRegistry + image.repository + image.tag -> registry/repo:tag

Compatibilidade:
  - Suporta charts antigos (tag-only) e novos (digest pinning).
  - Se image.repository já vier com registry (ex.: ghcr.io/...), mantém como está (não prefixa global.imageRegistry).
  - Se quiser override total (incl. registry + @sha256 ou :tag), use image.full.
*/ -}}

{{- $img := .image -}}
{{- $vals := .Values -}}

{{- if $img.full -}}
{{- $img.full -}}
{{- else if and $img.repository $img.digest -}}
{{- printf "%s@%s" $img.repository $img.digest -}}
{{- else -}}
  {{- $repo := $img.repository | default "" -}}
  {{- $tag := $img.tag | default "latest" -}}

  {{- /* Detecta registry embutido: domínio (.) ou porta (:) antes da primeira '/' */ -}}
  {{- $parts := splitList "/" $repo -}}
  {{- $first := first $parts | default "" -}}
  {{- $hasRegistry := or (contains "." $first) (contains ":" $first) -}}

  {{- if $hasRegistry -}}
    {{- printf "%s:%s" $repo $tag -}}
  {{- else -}}
    {{- printf "%s/%s:%s" ($vals.global.imageRegistry | default "ghcr.io/abelisboa") $repo $tag -}}
  {{- end -}}
{{- end -}}
{{- end -}}
EOF
)"

# Estratégia de patch:
# - Se função existe: substituir bloco define..end por NEW_TRISLA_IMAGE_FUNC
# - Se não existe: anexar NEW_TRISLA_IMAGE_FUNC ao final do arquivo

TMP_HELPERS="$(mktemp)"
cp "$HELPERS" "$TMP_HELPERS"

if grep -n 'define "trisla.image"' "$TMP_HELPERS" >/dev/null 2>&1; then
  # Substituição do bloco
  awk -v repl="$NEW_TRISLA_IMAGE_FUNC" '
    BEGIN{inblock=0}
    $0 ~ /define "trisla.image"/ {inblock=1; print repl; next}
    inblock==1 && $0 ~ /end/ {inblock=0; next}
    inblock==0 {print}
  ' "$TMP_HELPERS" > "${TMP_HELPERS}.patched"
  mv "${TMP_HELPERS}.patched" "$TMP_HELPERS"
else
  printf "\n\n%s\n" "$NEW_TRISLA_IMAGE_FUNC" >> "$TMP_HELPERS"
fi

# Idempotência: se não mudou, ok; se mudou, aplica
if diff -q "$HELPERS" "$TMP_HELPERS" >/dev/null 2>&1; then
  log "Helper já estava compatível (nenhuma mudança necessária)."
else
  cp "$TMP_HELPERS" "$HELPERS"
  log "Helper atualizado com sucesso."
fi

rm -f "$TMP_HELPERS"

# Captura helper novo
awk '
  $0 ~ /define "trisla.image"/ {p=1}
  p==1 {print}
  p==1 && $0 ~ /end/ {exit}
' "$HELPERS" > "$BACKUP_DIR/trisla.image.after.tpl" || true

# -------------------------------
# 3) Verificação de uso do helper
# -------------------------------
log "[3/7] Verificando templates que NÃO usam trisla.image para image:"
# Lista linhas com "image:" que não chamam include "trisla.image"
# (isto é diagnóstico, não altera automaticamente sem regra)
helm template "$RELEASE" "$CHART_DIR" -n "$NS" -f "$VALUES_FILE" >/tmp/helm_render.yaml

grep -n '^\s*image:\s*' /tmp/helm_render.yaml \
  | awk '!/trisla.image/ {print}' \
  > "$BACKUP_DIR/images_rendered_lines.txt" || true

log "Linhas image: renderizadas (diagnóstico) -> $BACKUP_DIR/images_rendered_lines.txt"

# -------------------------------
# 4) Lint + render parse (anti-regressão)
# -------------------------------
log "[4/7] Helm lint + validação de render"
helm lint "$CHART_DIR" -f "$VALUES_FILE" > "$BACKUP_DIR/helm_lint.txt" || fail "helm lint falhou (ver $BACKUP_DIR/helm_lint.txt)"
helm template "$RELEASE" "$CHART_DIR" -n "$NS" -f "$VALUES_FILE" > "$BACKUP_DIR/helm_template.yaml" || fail "helm template falhou"

# -------------------------------
# 5) Digest compliance check (render)
# -------------------------------
log "[5/7] Checando compliance por digest nas imagens renderizadas"
# Regras:
# - Se values possuir digest para determinado componente, o render deve conter @sha256:...
# - Se não tiver digest, aceita tag (sem forçar tudo agora)

# Extrai imagens do manifest renderizado
grep -oE 'image:\s*"?[^"]+"?' "$BACKUP_DIR/helm_template.yaml" \
  | sed 's/image:\s*//g' | sed 's/"//g' \
  | sort -u > "$BACKUP_DIR/rendered_images.txt"

log "Imagens renderizadas -> $BACKUP_DIR/rendered_images.txt"

# Valida que kafka está com digest (se definido no values)
# (Implementação robusta: checa especificamente a seção kafka.image.digest)
KAFKA_DIGEST="$(awk '
  $0 ~ /^[[:space:]]*kafka:[[:space:]]*$/ {in_k=1; next}
  in_k==1 && $0 ~ /^[[:space:]]*image:[[:space:]]*$/ {in_img=1; next}
  in_k==1 && in_img==1 && $1=="digest:" {gsub(/"/,"",$2); print $2; exit}
  in_k==1 && $0 ~ /^[^[:space:]]/ {in_k=0; in_img=0}
' "$VALUES_FILE" 2>/dev/null || true)"

if [ -n "${KAFKA_DIGEST:-}" ]; then
  if ! grep -q "@${KAFKA_DIGEST}" "$BACKUP_DIR/rendered_images.txt"; then
    fail "Kafka digest definido no values.yaml (${KAFKA_DIGEST}), mas não encontrado no render (rendered_images.txt)."
  fi
  log "Kafka digest OK no render: @$KAFKA_DIGEST"
else
  log "Kafka digest não definido no values.yaml (nenhuma exigência aplicada para kafka)."
fi

# -------------------------------
# 6) Aplicar no cluster (sem --force)
# -------------------------------
log "[6/7] Deploy controlado no cluster (helm upgrade sem --force)"
helm upgrade --install "$RELEASE" "$CHART_DIR" -n "$NS" -f "$VALUES_FILE" > "$BACKUP_DIR/helm_upgrade.txt" || fail "helm upgrade falhou"

log "Rollout status (deployments principais)"
# Ajuste a lista se necessário. Mantive core + kafka + exporter.
for d in kafka trisla-bc-nssmf trisla-decision-engine trisla-sem-csmf trisla-ml-nsmf trisla-sla-agent-layer trisla-ui-dashboard trisla-traffic-exporter; do
  if kubectl get deploy -n "$NS" "$d" >/dev/null 2>&1; then
    kubectl rollout status deploy/"$d" -n "$NS" --timeout=180s | tee -a "$BACKUP_DIR/rollout_status.txt" || fail "rollout falhou em $d"
  else
    echo "SKIP: deploy $d não existe" | tee -a "$BACKUP_DIR/rollout_status.txt"
  fi
done

log "Capturando imagens runtime (pods) pós-upgrade"
kubectl get pods -n "$NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .status.containerStatuses[*]}{.image}{"\t"}{.imageID}{"\n"}{end}{end}' \
  > "$BACKUP_DIR/runtime_images.txt" || true

# -------------------------------
# 7) Update Runbook (append seguro)
# -------------------------------
log "[7/7] Atualizando Runbook (append) — evidência e regra digest-aware"

if [ -f "$RUNBOOK" ]; then
  {
    echo ""
    echo "## SXX — Digest-Aware Helm Image Resolver + Compliance (Auto) ($STAMP)"
    echo ""
    echo "- **Objetivo:** Tornar o helper Helm \`trisla.image\` compatível com digest (\`@sha256\`) e permitir pinning total via \`values.yaml\`."
    echo "- **Escopo:** BC-NSSMF, ML-NSMF, Decision Engine, SEM-CSMF, SLA-Agent, UI, Traffic Exporter, Kafka."
    echo "- **Mudança controlada:** Atualização do helper \`helm/trisla/templates/_helpers.tpl\` (digest-aware), sem alterar lógica de aplicação."
    echo "- **Validações executadas:** \`helm lint\`, \`helm template\`, \`helm upgrade\`, rollouts, snapshot de imagens runtime."
    echo "- **Evidências:** \`$BACKUP_DIR/\` (helpers before/after, template render, lint, upgrade, runtime_images)."
    echo "- **Regra:** Para fixar por digest, definir \`*.image.digest: \"sha256:...\"\` no \`values.yaml\`."
    echo ""
  } >> "$RUNBOOK"
else
  log "Runbook não encontrado em $RUNBOOK — apenas evidências geradas em $BACKUP_DIR"
fi

log "=========================================================="
log "PATCH CONCLUÍDO COM SUCESSO"
log "Evidências: $BACKUP_DIR"
log "Próximo passo: popular digests dos demais componentes no values.yaml e reexecutar compliance."
log "=========================================================="
