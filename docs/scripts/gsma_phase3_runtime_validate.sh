#!/usr/bin/env bash
# FASE 3 — Runtime Equivalence Validation (TriSLA cluster)
# Executar no host com kubectl + curl (ex.: node006).
# Não altera scoring, thresholds, pesos, nem deployments (salvo rollback backup YAML).
set -uo pipefail
# Erros explícitos em passos críticos; curl/jq não abortam o script prematuramente
set +e

REPO_ROOT="${REPO_ROOT:-/home/porvir5g/gtp5g/trisla}"
NS="${TRISLA_NS:-trisla}"
PF_LOCAL_PORT="${PF_LOCAL_PORT:-18001}"
PF_REMOTE_PORT="${PF_REMOTE_PORT:-8001}"
SLEEP_PF="${SLEEP_PF:-10}"

cd "$REPO_ROOT" || {
  echo "FAIL: REPO_ROOT not found: $REPO_ROOT" >&2
  exit 2
}

TS="${TS:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${OUT:-$REPO_ROOT/evidencias_gsma_alignment_phase3_runtime_${TS}}"

mkdir -p "$OUT"/{runtime,payloads,analysis,compare,logs,rollback,validation}

# ETAPA 1 — snapshot baseline
kubectl -n "$NS" get pods -o wide >"$OUT/runtime/pods.txt" || true
kubectl -n "$NS" get deploy >"$OUT/runtime/deployments.txt" || true
kubectl -n "$NS" get svc >"$OUT/runtime/services.txt" || true
kubectl -n "$NS" get events --sort-by=.metadata.creationTimestamp >"$OUT/runtime/events.txt" || true

# ETAPA 2 — rollback backup
kubectl -n "$NS" get deploy trisla-sem-csmf -o yaml >"$OUT/rollback/sem_csmf_before.yaml" 2>/dev/null || echo "# sem_csmf deploy not found or no permission" >"$OUT/rollback/sem_csmf_before.yaml"

# Payloads: Portal só aceita SLASubmitRequest (template_id + form_values + tenant_id).
# Para equivalência operacional com MESMO contrato e MESMO perfil semântico, Run B usa
# o mesmo corpo JSON que Run A (duas submissões consecutivas — drift temporal zero esperado).
# Se no futuro existir submit canónico explícito, substituir canonical_payload.json.
LEGACY_PAYLOAD="$OUT/payloads/legacy_payload.json"
CANON_PAYLOAD="$OUT/payloads/canonical_payload.json"

cat >"$LEGACY_PAYLOAD" <<'JSON'
{
  "tenant_id": "smart-port-beta",
  "template_id": "semantic-embb-template",
  "form_values": {
    "service_description": "Real-time autonomous port logistics with high throughput video analytics",
    "priority": "high",
    "expected_devices": 120,
    "mobility_profile": "mobile",
    "availability_target": "99.95",
    "security_profile": "enhanced",
    "service_continuity": true,
    "edge_processing": true
  }
}
JSON
cp -a "$LEGACY_PAYLOAD" "$CANON_PAYLOAD"

# ETAPA 4 — port-forward (background)
kubectl -n "$NS" port-forward "svc/trisla-portal-backend" "${PF_LOCAL_PORT}:${PF_REMOTE_PORT}" \
  >"$OUT/logs/port_forward.log" 2>&1 &
PF_PID=$!
cleanup() {
  kill "$PF_PID" 2>/dev/null || true
}
trap cleanup EXIT

sleep "$SLEEP_PF"

curl -sS "http://127.0.0.1:${PF_LOCAL_PORT}/api/v1/health/global" >"$OUT/runtime/health.json" || {
  echo '{"error":"health_global_failed"}' >"$OUT/runtime/health.json"
}

# ETAPA 6–7 — legacy submit + telemetry extract
curl -sS -X POST "http://127.0.0.1:${PF_LOCAL_PORT}/api/v1/sla/submit" \
  -H "Content-Type: application/json" \
  -d @"$LEGACY_PAYLOAD" >"$OUT/payloads/legacy_response.json" || true

jq '.metadata.telemetry_snapshot // null' "$OUT/payloads/legacy_response.json" >"$OUT/analysis/legacy_telemetry_snapshot.json" 2>/dev/null || echo "null" >"$OUT/analysis/legacy_telemetry_snapshot.json"

# ETAPA 9 — second submit (canonical file = same body; consecutive)
curl -sS -X POST "http://127.0.0.1:${PF_LOCAL_PORT}/api/v1/sla/submit" \
  -H "Content-Type: application/json" \
  -d @"$CANON_PAYLOAD" >"$OUT/payloads/canonical_response.json" || true

jq '.metadata.telemetry_snapshot // null' "$OUT/payloads/canonical_response.json" >"$OUT/analysis/canonical_telemetry_snapshot.json" 2>/dev/null || echo "null" >"$OUT/analysis/canonical_telemetry_snapshot.json"

# ETAPA 10 — extractions + compare helpers
jq -n \
  --argjson a "$(jq -c . "$OUT/payloads/legacy_response.json" 2>/dev/null || echo '{}')" \
  --argjson b "$(jq -c . "$OUT/payloads/canonical_response.json" 2>/dev/null || echo '{}')" \
  '{
    legacy_decision: ($a.decision // null),
    canonical_decision: ($b.decision // null),
    decision_match: (($a.decision // "") == ($b.decision // "")),
    legacy_confidence: ($a.confidence // null),
    canonical_confidence: ($b.confidence // null),
    confidence_diff: ((($b.confidence // 0) | tonumber) - (($a.confidence // 0) | tonumber))
  }' >"$OUT/compare/decision_compare.json" 2>/dev/null || echo '{"error":"jq_failed"}' >"$OUT/compare/decision_compare.json"

# score: use ml_prediction or metadata final scores if present
jq -n \
  --argjson a "$(jq -c . "$OUT/payloads/legacy_response.json" 2>/dev/null || echo '{}')" \
  --argjson b "$(jq -c . "$OUT/payloads/canonical_response.json" 2>/dev/null || echo '{}')" \
  '{
    legacy_ml: ($a.ml_prediction // null),
    canonical_ml: ($b.ml_prediction // null),
    note: "Compare ml_prediction.risk_score and slice_adjusted fields if present"
  }' >"$OUT/compare/score_compare.json"

# XAI / domains
jq -n \
  --argjson a "$(jq -c . "$OUT/payloads/legacy_response.json" 2>/dev/null || echo '{}')" \
  --argjson b "$(jq -c . "$OUT/payloads/canonical_response.json" 2>/dev/null || echo '{}')" \
  '{
    legacy_domains: ($a.domains // null),
    canonical_domains: ($b.domains // null),
    domains_match: (($a.domains | @json) == ($b.domains | @json)),
    legacy_reasoning_len: (($a.reasoning // "") | tostring | length),
    canonical_reasoning_len: (($b.reasoning // "") | tostring | length)
  }' >"$OUT/compare/xai_compare.json"

# orchestration
jq -n \
  --argjson a "$(jq -c . "$OUT/payloads/legacy_response.json" 2>/dev/null || echo '{}')" \
  --argjson b "$(jq -c . "$OUT/payloads/canonical_response.json" 2>/dev/null || echo '{}')" \
  '{
    legacy_orch: {status: ($a.orchestration_status // null), ref: ($a.orchestration_reference // null), meta: ($a.metadata.nasp_orchestration_status // null)},
    canonical_orch: {status: ($b.orchestration_status // null), ref: ($b.orchestration_reference // null), meta: ($b.metadata.nasp_orchestration_status // null)}
  }' >"$OUT/compare/orchestration_compare.json"

# governance
jq -n \
  --argjson a "$(jq -c . "$OUT/payloads/legacy_response.json" 2>/dev/null || echo '{}')" \
  --argjson b "$(jq -c . "$OUT/payloads/canonical_response.json" 2>/dev/null || echo '{}')" \
  '{
    legacy_tx: ($a.tx_hash // $a.blockchain_tx_hash // null),
    canonical_tx: ($b.tx_hash // $b.blockchain_tx_hash // null),
    legacy_block: ($a.block_number // null),
    canonical_block: ($b.block_number // null),
    tx_match: ((($a.tx_hash // $a.blockchain_tx_hash // "") | tostring) == (($b.tx_hash // $b.blockchain_tx_hash // "") | tostring)),
    block_match: ($a.block_number == $b.block_number)
  }' >"$OUT/compare/governance_compare.json"

# runtime assurance
jq -n \
  --argjson a "$(jq -c . "$OUT/payloads/legacy_response.json" 2>/dev/null || echo '{}')" \
  --argjson b "$(jq -c . "$OUT/payloads/canonical_response.json" 2>/dev/null || echo '{}')" \
  '{
    legacy_sla_agent: ($a.sla_agent_status // null),
    canonical_sla_agent: ($b.sla_agent_status // null),
    legacy_tel_complete: ($a.telemetry_complete // null),
    canonical_tel_complete: ($b.telemetry_complete // null),
    sla_agent_match: (($a.sla_agent_status // "") == ($b.sla_agent_status // "")),
    telemetry_complete_match: ($a.telemetry_complete == $b.telemetry_complete)
  }' >"$OUT/compare/runtime_assurance_compare.json"

# telemetry snapshot: comparar PRB agregado (evita falha por ruído temporal em outros campos)
PRB_A=$(jq -r '(.ran // {}) | .prb_utilization // empty' "$OUT/analysis/legacy_telemetry_snapshot.json" 2>/dev/null || true)
PRB_B=$(jq -r '(.ran // {}) | .prb_utilization // empty' "$OUT/analysis/canonical_telemetry_snapshot.json" 2>/dev/null || true)
jq -n \
  --arg prb_a "${PRB_A:-}" \
  --arg prb_b "${PRB_B:-}" \
  --argjson a "$(jq -c . "$OUT/analysis/legacy_telemetry_snapshot.json" 2>/dev/null || echo 'null')" \
  --argjson b "$(jq -c . "$OUT/analysis/canonical_telemetry_snapshot.json" 2>/dev/null || echo 'null')" \
  '{
    prb_utilization_legacy: (if $prb_a == "" then null else ($prb_a|tonumber? // $prb_a) end),
    prb_utilization_canonical: (if $prb_b == "" then null else ($prb_b|tonumber? // $prb_b) end),
    prb_match: (if $prb_a == "" and $prb_b == "" then true else ($prb_a == $prb_b) end),
    full_json_match: ($a == $b),
    note: "prb_match primary; empty PRB on both sides => match (no PRB in snapshot)"
  }' >"$OUT/compare/telemetry_compare.json"

# canonical_sla presence in metadata (SEM path)
jq -n \
  --argjson a "$(jq -c .metadata "$OUT/payloads/legacy_response.json" 2>/dev/null || echo '{}')" \
  '{
    canonical_sla_present: ($a | type == "object" and (.canonical_sla != null)),
    metadata_keys: (if ($a|type)=="object" then ($a|keys) else [] end)
  }' >"$OUT/validation/canonical_sla_metadata_check.json" 2>/dev/null || echo '{}' >"$OUT/validation/canonical_sla_metadata_check.json"

# ETAPA 11 — PASS/FAIL rules (score drift <= 1e-4 on confidence if numeric)
export OUT
python3 <<'PY' >"$OUT/validation/gate_result.json"
import json, pathlib, os

root = pathlib.Path(os.environ["OUT"])


def load(rel):
    p = root / rel
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


leg = load("payloads/legacy_response.json")
can = load("payloads/canonical_response.json")
dc = load("compare/decision_compare.json")
rac = load("compare/runtime_assurance_compare.json")
tc = load("compare/telemetry_compare.json")

failures = []
if leg.get("status") == "error" or can.get("status") == "error":
    failures.append("submit_response_status_error")
if not dc.get("decision_match", False):
    failures.append("decision_mismatch")
try:
    ca, cb = leg.get("confidence"), can.get("confidence")
    if ca is not None and cb is not None:
        if abs(float(cb) - float(ca)) > 1e-4:
            failures.append("confidence_drift_gt_1e-4")
except (TypeError, ValueError):
    if leg.get("confidence") is not None or can.get("confidence") is not None:
        failures.append("confidence_not_numeric")

if (leg.get("domains") or []) != (can.get("domains") or []):
    failures.append("domains_mismatch")

if not rac.get("sla_agent_match", True):
    failures.append("sla_agent_mismatch")
if rac.get("legacy_tel_complete") is True or rac.get("canonical_tel_complete") is True:
    if not rac.get("telemetry_complete_match", False):
        failures.append("telemetry_complete_mismatch")

if not tc.get("prb_match", True):
    if tc.get("prb_utilization_legacy") not in (None, "", "null") or tc.get("prb_utilization_canonical") not in (
        None,
        "",
        "null",
    ):
        failures.append("prb_mismatch_when_prb_present")

for label, resp in ("legacy", leg), ("canonical", can):
    if resp.get("decision") == "ACCEPT" and resp.get("bc_status") not in (None, "ERROR", ""):
        if not (resp.get("tx_hash") or resp.get("blockchain_tx_hash")):
            failures.append(f"{label}_missing_tx_on_accept")

result = "PASS" if not failures else "FAIL"
print(
    json.dumps(
        {
            "result": result,
            "failures": failures,
            "note": "Two consecutive submits with identical SLASubmitRequest body; tx_hash expected to differ between runs.",
        },
        indent=2,
    )
)
PY

GATE=$(jq -r .result "$OUT/validation/gate_result.json")
cat >"$OUT/validation/validation_report.md" <<MD
# FASE 3 — Runtime equivalence validation

**OUT:** \`$OUT\`  
**Namespace:** \`$NS\`  
**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Modo de comparação

- Dois POSTs consecutivos a \`/api/v1/sla/submit\` com **o mesmo corpo JSON** (\`legacy_payload.json\` == \`canonical_payload.json\`), conforme limite do contrato \`SLASubmitRequest\` no Portal.
- **Nota:** \`tx_hash\` / \`block_number\` **esperam-se diferentes** entre duas submissões bem-sucedidas (dois registos BC). O gate **não** exige igualdade de \`tx_hash\` entre runs; exige presença quando \`decision=ACCEPT\` e BC não ERROR.

## Gate automático

**$(cat "$OUT/validation/gate_result.json")**

## canonical_sla no metadata da resposta

\`\`\`json
$(cat "$OUT/validation/canonical_sla_metadata_check.json")
\`\`\`

## Resultado global

**${GATE}**

MD

echo "$OUT"
exit 0
