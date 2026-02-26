#!/usr/bin/env bash
set -euo pipefail

TS="$(date -u +%Y%m%dT%H%M%SZ)"
BASE="/home/porvir5g/gtp5g/trisla"
OUTDIR="$BASE/evidencias_guardiao_deterministico"
LOG="$OUTDIR/FASE_D_${TS}.log"

TAG="v3.9.26"
IMG="ghcr.io/abelisboa/trisla-decision-engine:${TAG}"

mkdir -p "$OUTDIR"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG" ; }

log "=============================="
log "FASE D — Transporte como domínio com Headroom (MDCE / Decision Engine)"
log "=============================="
log "Base: $BASE"
log "Saída: $LOG"
log "Tag: $TAG"
log "Imagem: $IMG"

cd "$BASE"

log "=============================="
log "PASSO 1 — Sanidade (estado atual)"
log "=============================="
log "+ kubectl get pod -n trisla -l app=trisla-decision-engine -o jsonpath='{.items[0].spec.containers[0].image}{"\n"}' || true"
kubectl get pod -n trisla -l app=trisla-decision-engine -o jsonpath='{.items[0].spec.containers[0].image}{"\n"}' 2>/dev/null | tee -a "$LOG" || true

test -f apps/decision-engine/src/mdce.py
log "OK: mdce.py existe"

log "=============================="
log "PASSO 2 — Patch controlado no MDCE (transport headroom all slices)"
log "=============================="

MDCE="apps/decision-engine/src/mdce.py"

# Patch: inserir variáveis + regra de headroom RTT para todos slices
python3 - <<'PY'
import re, pathlib

p = pathlib.Path("apps/decision-engine/src/mdce.py")
s = p.read_text(encoding="utf-8")

# 1) Garantir que MDCE_HEADROOM_ENABLED já exista (você já tem em v3.9.25)
if "MDCE_HEADROOM_ENABLED" not in s:
    raise SystemExit("ERRO: mdce.py não tem MDCE_HEADROOM_ENABLED (esperado da FASE C).")

# 2) Inserir variáveis de transporte (limites + custos) logo após MDCE_URLLC_RTT_BUDGET_MS
anchor = r'MDCE_URLLC_RTT_BUDGET_MS\s*=\s*float\(os\.getenv\("MDCE_URLLC_RTT_BUDGET_MS",\s*"[0-9.]+\"\)\)\s*'
m = re.search(anchor, s)
if not m:
    raise SystemExit("ERRO: não encontrei MDCE_URLLC_RTT_BUDGET_MS para ancorar variáveis.")

insert = """
# Transporte como domínio pleno (3GPP/5G pragmático):
# - URLLC: budget rígido (latency.max_ms ou default)
# - eMBB: limite conservador
# - mMTC: limite amplo (não crítico), mas ainda controlado
MDCE_TRANSPORT_ENABLED = os.getenv("MDCE_TRANSPORT_ENABLED", "true").lower() == "true"
MDCE_EMBB_RTT_LIMIT_MS = float(os.getenv("MDCE_EMBB_RTT_LIMIT_MS", "50.0"))
MDCE_MMTC_RTT_LIMIT_MS = float(os.getenv("MDCE_MMTC_RTT_LIMIT_MS", "200.0"))

# Headroom (delta RTT em ms) por slice (determinístico)
MDCE_COST_EMBB_RTT_MS = float(os.getenv("MDCE_COST_EMBB_RTT_MS", "5.0"))
MDCE_COST_URLLC_RTT_MS = float(os.getenv("MDCE_COST_URLLC_RTT_MS", "8.0"))
MDCE_COST_MMTC_RTT_MS = float(os.getenv("MDCE_COST_MMTC_RTT_MS", "2.0"))
"""

pos = m.end()
s = s[:pos] + insert + s[pos:]

# 3) Inserir/garantir função utilitária _num (se já existir, não duplica)
if "def _num(" not in s:
    # tenta ancorar após logger
    m2 = re.search(r'logger\s*=\s*logging\.getLogger\(__name__\)\s*', s)
    if not m2:
        raise SystemExit("ERRO: não encontrei logger para inserir helpers.")
    helper = """

def _num(v):
    try:
        return float(v)
    except Exception:
        return None

def _int(v):
    try:
        return int(v)
    except Exception:
        return None
"""
    s = s[:m2.end()] + helper + s[m2.end():]

# 4) Inserir regra de transporte com headroom dentro de evaluate()
# Localiza bloco onde lê rtt_p95 = transport.get("rtt_p95_ms")
pattern = r'# Regra: FAIL se URLLC e transport\.rtt_p95_ms > budget\s*\n\s*rtt_p95 = transport\.get\("rtt_p95_ms"\)[\s\S]*?# Regra: FAIL se ran\.ue\.active_count > limite'
m3 = re.search(pattern, s)
if not m3:
    raise SystemExit("ERRO: bloco RTT original não encontrado (mdce.py mudou?).")

new_block = r'''# Transporte (RTT p95) — domínio pleno com headroom determinístico
    rtt_p95 = transport.get("rtt_p95_ms")
    if MDCE_TRANSPORT_ENABLED:
        # Política DevOps: sem RTT não há decisão sustentável (FAIL determinístico)
        if rtt_p95 is None:
            reasons.append("metric_unavailable:transport.rtt_p95_ms")
        else:
            safety = float(os.getenv("MDCE_HEADROOM_SAFETY_FACTOR", "0.10"))
            # Delta por slice
            if slice_upper == "URLLC":
                delta = MDCE_COST_URLLC_RTT_MS
            elif slice_upper == "eMBB":
                delta = MDCE_COST_EMBB_RTT_MS
            else:
                delta = MDCE_COST_MMTC_RTT_MS

            delta_eff = delta * (1.0 + safety) if MDCE_HEADROOM_ENABLED else delta
            effective_rtt = float(rtt_p95) + float(delta_eff) if MDCE_HEADROOM_ENABLED else float(rtt_p95)

            # Limite por slice
            if slice_upper == "URLLC":
                budget = sla_requirements.get("latency")
                if isinstance(budget, dict) and "max_ms" in budget:
                    limit_ms = float(budget["max_ms"])
                elif isinstance(budget, (int, float)):
                    limit_ms = float(budget)
                else:
                    limit_ms = MDCE_URLLC_RTT_BUDGET_MS
            elif slice_upper == "eMBB":
                limit_ms = MDCE_EMBB_RTT_LIMIT_MS
            else:
                limit_ms = MDCE_MMTC_RTT_LIMIT_MS

            if effective_rtt > limit_ms:
                reasons.append(
                    f"transport.rtt_p95_ms={rtt_p95} + headroom_rtt={round(delta_eff,3)} => {round(effective_rtt,3)} > {limit_ms} ({slice_upper})"
                )

    # Regra: FAIL se ran.ue.active_count > limite
'''
s = s[:m3.start()] + new_block + s[m3.end()-len("# Regra: FAIL se ran.ue.active_count > limite"):]

p.write_text(s, encoding="utf-8")
print("OK: mdce.py patch aplicado.")
PY

log "+ python3 -m py_compile apps/decision-engine/src/mdce.py"
python3 -m py_compile apps/decision-engine/src/mdce.py | tee -a "$LOG"
log "OK: mdce.py syntax"

log "=============================="
log "PASSO 3 — Build + Push imagem (Decision Engine)"
log "=============================="
log "+ cd apps/decision-engine && podman build -t $IMG ."
cd "$BASE/apps/decision-engine"
podman build -t "$IMG" . | tee -a "$LOG"
log "+ podman push $IMG"
podman push "$IMG" | tee -a "$LOG"

log "=============================="
log "PASSO 4 — Deploy via Helm (tag + env transporte/headroom)"
log "=============================="
cd "$BASE"

log "+ helm upgrade trisla helm/trisla -n trisla --set decisionEngine.image.tag=$TAG (e vars)"
helm upgrade trisla helm/trisla -n trisla \
  --set decisionEngine.image.tag="$TAG" \
  --set decisionEngine.env.MDCE_TRANSPORT_ENABLED=true \
  --set decisionEngine.env.MDCE_HEADROOM_ENABLED=true \
  --set decisionEngine.env.MDCE_HEADROOM_SAFETY_FACTOR=0.10 \
  --set decisionEngine.env.MDCE_EMBB_RTT_LIMIT_MS=50.0 \
  --set decisionEngine.env.MDCE_MMTC_RTT_LIMIT_MS=200.0 \
  --set decisionEngine.env.MDCE_COST_EMBB_RTT_MS=5.0 \
  --set decisionEngine.env.MDCE_COST_URLLC_RTT_MS=8.0 \
  --set decisionEngine.env.MDCE_COST_MMTC_RTT_MS=2.0 \
  | tee -a "$LOG"

log "+ kubectl rollout status -n trisla deploy/trisla-decision-engine"
kubectl rollout status -n trisla deploy/trisla-decision-engine --timeout=180s | tee -a "$LOG"

log "=============================="
log "PASSO 5 — Evidência: imagem + env no pod + RTT do NASP"
log "=============================="

log "+ kubectl get pod -n trisla -l app=trisla-decision-engine -o jsonpath='{.items[0].spec.containers[0].image}{\"\\n\"}'"
kubectl get pod -n trisla -l app=trisla-decision-engine -o jsonpath='{.items[0].spec.containers[0].image}{"\n"}' | tee -a "$LOG"

log "+ kubectl get pod -n trisla -l app=trisla-decision-engine -o json | jq (vars principais)"
kubectl get pod -n trisla -l app=trisla-decision-engine -o json \
  | jq -r '.items[0].spec.containers[0].env[] | select(.name|test("MDCE_TRANSPORT|MDCE_.*RTT|MDCE_HEADROOM"))' \
  | tee -a "$LOG" || true

log "+ curl multidomain (NASP) para confirmar rtt_p95_ms não-null"
kubectl run curl-md --rm -i --restart=Never -n trisla --image=curlimages/curl --command -- \
  curl -s http://trisla-nasp-adapter:8085/api/v1/metrics/multidomain \
  | tee -a "$LOG"

log "✅ FASE D CONCLUÍDA — Transporte com headroom ativo para todos slices."
