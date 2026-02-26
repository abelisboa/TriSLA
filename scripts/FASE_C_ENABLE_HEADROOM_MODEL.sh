#!/usr/bin/env bash
set -euo pipefail

# ==============================
# FASE C — Enable Headroom Model (MDCE sustentável no Decision Engine)
# Objetivo: transformar thresholds estáticos (estado atual) em verificação determinística
#           de sustentabilidade: (estado atual + delta_por_slice) <= limite.
#
# Regras DevOps:
# - Tag sem sufixo (ex.: v3.9.25)
# - Sem "gambiarra": tudo via Git + build/push + Helm upgrade
# - Idempotente (reexecutável)
# ==============================

TS="$(date -u +%Y%m%dT%H%M%SZ)"
BASE="/home/porvir5g/gtp5g/trisla"
OUTDIR="$BASE/evidencias_guardiao_deterministico"
LOG="$OUTDIR/FASE_C_${TS}.log"

TAG="v3.9.25"  # ajuste somente aqui
IMAGE="ghcr.io/abelisboa/trisla-decision-engine:${TAG}"

mkdir -p "$OUTDIR"

log(){ echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"; }
run(){ log "+ $*"; bash -lc "$*" 2>&1 | tee -a "$LOG"; }

log "=============================="
log "FASE C — Headroom Model (Decision Engine / MDCE)"
log "=============================="
log "Base: $BASE"
log "Saída: $LOG"
log "Tag: $TAG"
log "Imagem: $IMAGE"

cd "$BASE"

log "=============================="
log "PASSO 1 — Sanidade: estado atual (imagem + arquivo mdce.py)"
log "=============================="
run 'kubectl get pod -n trisla -l app=trisla-decision-engine -o jsonpath="{.items[0].spec.containers[0].image}{\"\n\"}" || true'
run 'test -f apps/decision-engine/src/mdce.py && echo "OK: mdce.py existe"'
run 'grep -n "MDCE_URLLC_RTT_BUDGET_MS" -n apps/decision-engine/src/mdce.py | head -n 5 || true'
run 'grep -n "HEADROOM" -n apps/decision-engine/src/mdce.py || true'

log "=============================="
log "PASSO 2 — Aplicar MDCE v1 + Headroom determinístico (overwrite controlado)"
log "=============================="
cat > apps/decision-engine/src/mdce.py <<'PY'
"""
MDCE v1 — Multi-Domain Capacity Evaluation (PROMPT_SMDCE_V1_IMPLEMENTATION_v1.0).
Avalia capacidade multidomínio (Core, RAN, Transport) antes de ACCEPT.

Evolução (FASE C): Headroom determinístico
- Em vez de apenas comparar o estado atual com limites, avalia sustentabilidade:
  estado_atual + delta_por_slice (headroom) <= limite
- Modelo conservador e determinístico, com defaults por slice e override via SLA.
"""

import os
import logging
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Thresholds configuráveis (conservadores)
MDCE_CPU_PCT_LIMIT = float(os.getenv("MDCE_CPU_PCT_LIMIT", "85.0"))
MDCE_MEM_PCT_LIMIT = float(os.getenv("MDCE_MEM_PCT_LIMIT", "85.0"))
MDCE_UE_COUNT_LIMIT = int(os.getenv("MDCE_UE_COUNT_LIMIT", "10000"))
MDCE_URLLC_RTT_BUDGET_MS = float(os.getenv("MDCE_URLLC_RTT_BUDGET_MS", "20.0"))

# Forçar FAIL (sanity gate)
MDCE_FORCE_FAIL = os.getenv("MDCE_FORCE_FAIL", "false").lower() == "true"

# Headroom sustentável (FASE C)
MDCE_HEADROOM_ENABLED = os.getenv("MDCE_HEADROOM_ENABLED", "true").lower() == "true"
MDCE_HEADROOM_SAFETY_FACTOR = float(os.getenv("MDCE_HEADROOM_SAFETY_FACTOR", "0.10"))  # +10% conservador

# Defaults determinísticos de delta por slice (unidade: pontos percentuais para CPU/Mem; unidades para UE)
# Obs.: estes valores são propositadamente conservadores e devem ser calibrados posteriormente com base em evidência.
DEFAULT_COST = {
    "eMBB":  {"cpu_pct": float(os.getenv("MDCE_COST_EMBB_CPU_PCT", "3.0")),
              "mem_pct": float(os.getenv("MDCE_COST_EMBB_MEM_PCT", "3.0")),
              "ue":      int(os.getenv("MDCE_COST_EMBB_UE", "50"))},
    "URLLC": {"cpu_pct": float(os.getenv("MDCE_COST_URLLC_CPU_PCT", "5.0")),
              "mem_pct": float(os.getenv("MDCE_COST_URLLC_MEM_PCT", "5.0")),
              "ue":      int(os.getenv("MDCE_COST_URLLC_UE", "25"))},
    "mMTC":  {"cpu_pct": float(os.getenv("MDCE_COST_MMTC_CPU_PCT", "1.0")),
              "mem_pct": float(os.getenv("MDCE_COST_MMTC_MEM_PCT", "1.0")),
              "ue":      int(os.getenv("MDCE_COST_MMTC_UE", "200"))},
}

def _norm_slice(slice_type: str) -> str:
    s = (slice_type or "eMBB").strip().upper()
    if s == "EMBB":
        return "eMBB"
    if s == "URLLC":
        return "URLLC"
    if s == "MMTC":
        return "mMTC"
    # fallback seguro
    return "eMBB"

def _num(x: Any) -> Optional[float]:
    try:
        if isinstance(x, (int, float)):
            return float(x)
        return None
    except Exception:
        return None

def _int(x: Any) -> Optional[int]:
    try:
        if isinstance(x, int):
            return int(x)
        if isinstance(x, float) and float(x).is_integer():
            return int(x)
        return None
    except Exception:
        return None

def _get_headroom_from_sla(sla_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Permite override explícito via SLA (determinístico, sem heurística).
    Formatos aceitos:
      sla_requirements.headroom.cpu_pct
      sla_requirements.headroom.mem_pct
      sla_requirements.headroom.ue
    """
    hr = {}
    if not isinstance(sla_requirements, dict):
        return hr
    headroom = sla_requirements.get("headroom")
    if not isinstance(headroom, dict):
        return hr
    cpu = _num(headroom.get("cpu_pct"))
    mem = _num(headroom.get("mem_pct"))
    ue = _int(headroom.get("ue"))
    if cpu is not None: hr["cpu_pct"] = cpu
    if mem is not None: hr["mem_pct"] = mem
    if ue is not None:  hr["ue"] = ue
    return hr

def _apply_safety(x: float) -> float:
    # safety factor conservador (ex.: 3.0 -> 3.3 com 10%)
    return float(x) * (1.0 + float(MDCE_HEADROOM_SAFETY_FACTOR))

def evaluate(
    slice_type: str,
    sla_requirements: Dict[str, Any],
    metrics: Dict[str, Any],
) -> Tuple[str, List[str]]:
    """
    Avalia capacidade multidomínio (MDCE v1 + Headroom sustentável).

    Args:
        slice_type: URLLC | eMBB | mMTC
        sla_requirements: requisitos do SLA (ex.: latency, reliability, headroom override)
        metrics: schema SSOT do GET /api/v1/metrics/multidomain
                (core.upf.*, ran.ue.*, transport.*)

    Returns:
        ("PASS" | "FAIL", reasons[])
    """
    reasons: List[str] = []
    if MDCE_FORCE_FAIL:
        return ("FAIL", ["forced_fail_sanity"])

    slice_norm = _norm_slice(slice_type)

    core = metrics.get("core") or {}
    upf = core.get("upf") or {}
    ran = metrics.get("ran") or {}
    ue = ran.get("ue") or {}
    transport = metrics.get("transport") or {}

    cpu_pct = _num(upf.get("cpu_pct"))
    mem_pct = _num(upf.get("mem_pct"))
    ue_count = _int(ue.get("active_count"))
    rtt_p95 = _num(transport.get("rtt_p95_ms"))

    # ============================
    # HEADROOM (sustentabilidade)
    # ============================
    cost = DEFAULT_COST.get(slice_norm, DEFAULT_COST["eMBB"])
    override = _get_headroom_from_sla(sla_requirements)

    delta_cpu = float(override.get("cpu_pct", cost["cpu_pct"]))
    delta_mem = float(override.get("mem_pct", cost["mem_pct"]))
    delta_ue  = int(override.get("ue", cost["ue"]))

    # Aplica safety conservador apenas se headroom estiver habilitado
    if MDCE_HEADROOM_ENABLED:
        delta_cpu_eff = _apply_safety(delta_cpu)
        delta_mem_eff = _apply_safety(delta_mem)
        delta_ue_eff  = int(round(float(delta_ue) * (1.0 + float(MDCE_HEADROOM_SAFETY_FACTOR))))
    else:
        delta_cpu_eff, delta_mem_eff, delta_ue_eff = delta_cpu, delta_mem, delta_ue

    # Regra: FAIL se core.upf.cpu_pct + delta_cpu_eff > limite
    if cpu_pct is not None:
        effective_cpu = cpu_pct + float(delta_cpu_eff) if MDCE_HEADROOM_ENABLED else cpu_pct
        if effective_cpu > MDCE_CPU_PCT_LIMIT:
            reasons.append(
                f"core.upf.cpu_pct={cpu_pct} + headroom_cpu={round(delta_cpu_eff,3)} => {round(effective_cpu,3)} > {MDCE_CPU_PCT_LIMIT}"
            )

    # Regra: FAIL se core.upf.mem_pct + delta_mem_eff > limite
    if mem_pct is not None:
        effective_mem = mem_pct + float(delta_mem_eff) if MDCE_HEADROOM_ENABLED else mem_pct
        if effective_mem > MDCE_MEM_PCT_LIMIT:
            reasons.append(
                f"core.upf.mem_pct={mem_pct} + headroom_mem={round(delta_mem_eff,3)} => {round(effective_mem,3)} > {MDCE_MEM_PCT_LIMIT}"
            )

    # Transporte: FAIL se URLLC e RTT > budget
    if slice_norm == "URLLC" and rtt_p95 is not None:
        budget = sla_requirements.get("latency") if isinstance(sla_requirements, dict) else None
        if isinstance(budget, dict) and "max_ms" in budget:
            budget_ms = float(budget["max_ms"])
        elif isinstance(budget, (int, float)):
            budget_ms = float(budget)
        else:
            budget_ms = MDCE_URLLC_RTT_BUDGET_MS

        if rtt_p95 > budget_ms:
            reasons.append(f"URLLC transport.rtt_p95_ms={rtt_p95} > {budget_ms}")

    # RAN: FAIL se ran.ue.active_count + delta_ue_eff > limite
    if ue_count is not None:
        effective_ue = (ue_count + int(delta_ue_eff)) if MDCE_HEADROOM_ENABLED else ue_count
        if effective_ue > MDCE_UE_COUNT_LIMIT:
            reasons.append(
                f"ran.ue.active_count={ue_count} + headroom_ue={int(delta_ue_eff)} => {effective_ue} > {MDCE_UE_COUNT_LIMIT}"
            )

    if reasons:
        return ("FAIL", reasons)
    return ("PASS", [])
PY

run 'python3 -m py_compile apps/decision-engine/src/mdce.py && echo "OK: mdce.py syntax"'
run 'grep -n "MDCE_HEADROOM_ENABLED" -n apps/decision-engine/src/mdce.py'
run 'grep -n "headroom" -n apps/decision-engine/src/mdce.py | head -n 50'

log "=============================="
log "PASSO 3 — Build + Push imagem (Decision Engine)"
log "=============================="
run 'cd apps/decision-engine && podman build -t '"$IMAGE"' .'
run 'podman push '"$IMAGE"

log "=============================="
log "PASSO 4 — Deploy via Helm (tag + env headroom determinístico)"
log "=============================="
# Observação: assumimos que o chart aceita --set decisionEngine.image.tag
# e injeta envs via values. Se não aceitar, este passo vai acusar e você ajusta o chart.
run 'cd '"$BASE"' && helm upgrade trisla helm/trisla -n trisla \
  --set decisionEngine.image.tag='"$TAG"' \
  --set decisionEngine.env.MDCE_HEADROOM_ENABLED=true \
  --set decisionEngine.env.MDCE_HEADROOM_SAFETY_FACTOR=0.10 \
  --set decisionEngine.env.MDCE_COST_EMBB_CPU_PCT=3.0 \
  --set decisionEngine.env.MDCE_COST_EMBB_MEM_PCT=3.0 \
  --set decisionEngine.env.MDCE_COST_EMBB_UE=50 \
  --set decisionEngine.env.MDCE_COST_URLLC_CPU_PCT=5.0 \
  --set decisionEngine.env.MDCE_COST_URLLC_MEM_PCT=5.0 \
  --set decisionEngine.env.MDCE_COST_URLLC_UE=25 \
  --set decisionEngine.env.MDCE_COST_MMTC_CPU_PCT=1.0 \
  --set decisionEngine.env.MDCE_COST_MMTC_MEM_PCT=1.0 \
  --set decisionEngine.env.MDCE_COST_MMTC_UE=200
'
run 'kubectl rollout status -n trisla deploy/trisla-decision-engine --timeout=180s'

log "=============================="
log "PASSO 5 — Evidência: confirmar imagem e variáveis no pod"
log "=============================="
run 'kubectl get pod -n trisla -l app=trisla-decision-engine -o jsonpath="{.items[0].spec.containers[0].image}{\"\n\"}"'
run 'kubectl get pod -n trisla -l app=trisla-decision-engine -o jsonpath="{.items[0].spec.containers[0].env}{\"\n\"}" | jq ".[] | select(.name|test(\"MDCE_HEADROOM|MDCE_COST|MDCE_CPU_PCT_LIMIT|MDCE_MEM_PCT_LIMIT|MDCE_UE_COUNT_LIMIT|MDCE_URLLC_RTT_BUDGET_MS\"))"'

log "=============================="
log "FASE C CONCLUÍDA — Headroom model ativo no Decision Engine"
log "Próximo recomendado: FASE D (Transporte crítico para eMBB/mMTC) e FASE E (contrato único NASP+DE)"
log "=============================="
