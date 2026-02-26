#!/usr/bin/env bash
set -euo pipefail

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="evidencias_runbook_audit_${TS}"
mkdir -p "$OUT"

log(){ echo -e "$*" | tee -a "$OUT/00_run.log" ; }

log "==============================================="
log "TriSLA — Auditoria SSOT (RUNBOOK)"
log "Evidence: ${OUT}"
log "==============================================="

# localizar runbook (aceita RISLA/TRISLA e variações)
RUNBOOK="$(ls -1 docs/*RUNBOOK*.md 2>/dev/null | head -n 1 || true)"
if [[ -z "${RUNBOOK}" ]]; then
  # fallback: procura em repo
  RUNBOOK="$(find . -maxdepth 4 -type f -iname "*runbook*.md" 2>/dev/null | head -n 1 || true)"
fi

if [[ -z "${RUNBOOK}" ]]; then
  log "ERRO: Nenhum RUNBOOK encontrado em docs/ ou no repositório (find)."
  exit 1
fi

log "RUNBOOK encontrado: ${RUNBOOK}"
cp -f "$RUNBOOK" "$OUT/RUNBOOK_SNAPSHOT.md"

# extrair tópicos essenciais para evitar regressão
{
  echo "## 1) Identificação"
  echo "Arquivo: $RUNBOOK"
  echo "Timestamp UTC: $TS"
  echo

  echo "## 2) Índice (linhas com headings)"
  nl -ba "$RUNBOOK" | egrep -n "^\s*[0-9]+\s+#{1,6}\s" || true
  echo

  echo "## 3) Trechos sobre Frontend/Backend/Portal/UI"
  nl -ba "$RUNBOOK" | egrep -i "frontend|backend|portal|ui|dashboard|nextjs|react|fastapi" || true
  echo

  echo "## 4) Trechos sobre Observability (Prometheus/Grafana/Tempo/OTel)"
  nl -ba "$RUNBOOK" | egrep -i "observab|prometheus|grafana|tempo|opentelemetry|otel|traces|metrics|exemplar" || true
  echo

  echo "## 5) Trechos sobre Deploy/Helm/Kubernetes (regras SSOT)"
  nl -ba "$RUNBOOK" | egrep -i "helm|kubectl|namespace|values\.yaml|chart|rollback|no regress|ssot|govern|snapshot|evidenc" || true
  echo

  echo "## 6) Referências a componentes TriSLA (lista rápida)"
  nl -ba "$RUNBOOK" | egrep -i "sem-csmf|ml-nsmf|decision-engine|bc-nssmf|nasp-adapter|sla-agent|besu|kafka|otel-collector|tempo" || true
} > "$OUT/RUNBOOK_EXTRACT.txt" 2>&1

log " - OK: $OUT/RUNBOOK_EXTRACT.txt"

# Auditoria leve de diretórios que normalmente acompanham SSOT
{
  echo "## 7) Estrutura docs/ e helm/"
  ls -la docs 2>/dev/null || true
  echo
  ls -la helm 2>/dev/null || true
  echo

  echo "## 8) Arquivos que parecem ser 'fonte' de observability"
  find . -maxdepth 4 -type f \( -iname "*grafana*" -o -iname "*prometheus*" -o -iname "*tempo*" -o -iname "*otel*" -o -iname "*observab*" \) \
    | sed 's|^\./||' | sort || true
} > "$OUT/REPO_OBS_FILES.txt" 2>&1

log " - OK: $OUT/REPO_OBS_FILES.txt"

log "✅ Auditoria SSOT concluída (sem alterações). Evidência: ${OUT}"
