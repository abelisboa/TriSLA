#!/usr/bin/env bash
# PROMPT_230 — enriquecimento do CSV complementar (Prometheus + colunas alinhadas ao corpus Fase 2).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 1
[ -f /tmp/kubeconfig.node2 ] && export KUBECONFIG=/tmp/kubeconfig.node2

SSOT="$ROOT/evidencias_resultados_trisla_baseline_v8"
OUTDIR="$SSOT/dataset/fase2_contrast"
ANADIR="$SSOT/analysis/fase2_contrast"
mkdir -p "$OUTDIR" "$ANADIR"

export TRISLA_PROMETHEUS_QUERY_URL="${TRISLA_PROMETHEUS_QUERY_URL:-http://127.0.0.1:19090/api/v1/query}"
export TRISLA_FASE2_RAW_PATH="$OUTDIR/dataset_fase2_contrast_raw.csv"
export TRISLA_FASE2_ENRICHED_PATH="$OUTDIR/dataset_fase2_contrast_enriched.csv"
export TRISLA_FASE2_ENRICHMENT_META_PATH="$ANADIR/transport_enrichment_meta.json"

if [[ ! -f "$TRISLA_FASE2_RAW_PATH" ]]; then
  echo "[FAIL] Falta $TRISLA_FASE2_RAW_PATH — execute primeiro prompt230_contrast_campaign.sh" >&2
  exit 1
fi

python3 docs/scripts/run_fase2_enrichment_with_paths.py

python3 - <<'PY'
import json
from pathlib import Path
import pandas as pd

root = Path.cwd()
enr = root / "evidencias_resultados_trisla_baseline_v8/dataset/fase2_contrast/dataset_fase2_contrast_enriched.csv"
out = root / "evidencias_resultados_trisla_baseline_v8/analysis/fase2_contrast/fase2_contrast_summary.json"
if not enr.is_file():
    raise SystemExit("[FAIL] enriched contrast em falta")
df = pd.read_csv(enr)
summary = {
    "rows": len(df),
    "decision_counts": df["decision_trisla"].astype(str).value_counts().to_dict() if "decision_trisla" in df.columns else {},
    "prb_std": float(df["prb_utilization_real"].std(ddof=0) or 0) if "prb_utilization_real" in df.columns else None,
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(f"[OK] Resumo -> {out}")
PY

echo "[OK] Pós-processamento PROMPT_230 concluído."
