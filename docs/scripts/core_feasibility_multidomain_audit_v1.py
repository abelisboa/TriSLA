#!/usr/bin/env python3
"""
PROMPT_TRISLA_CORE_FEASIBILITY_MULTIDOMAIN_AUDIT_V1 — audit-only evidence generator.
No code/deploy/weight changes. Reads repo + frozen evidence folders.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(os.environ.get("TRISLA_REPO", "/home/porvir5g/gtp5g/trisla"))

SSOT_DIRS = {
    "true_multidomain": REPO / "evidencias_trisla_true_multidomain_runtime_20260517T031129Z",
    "phase4_publication": REPO / "evidencias_trisla_phase4_publication_consolidation_20260517T140548Z",
    "phase2_integration": REPO / "evidencias_trisla_phase2_de_runtime_integration_20260517T125400Z",
    "phase3_revalidation": REPO / "evidencias_trisla_phase3_runtime_revalidation_20260517T133134Z",
    "boundary_de": REPO / "evidencias_trisla_boundary_de_semantics_20260517T021533Z",
    "score_semantics": REPO / "evidencias_trisla_score_semantics_20260517T022203Z",
    "operational_score": REPO / "evidencias_trisla_operational_score_semantics_20260517T023343Z",
    "goodness_agg": REPO / "evidencias_trisla_goodness_aggregation_20260517T024013Z",
    "multidomain_balance": REPO / "evidencias_trisla_runtime_dominance_20260517T030200Z",
}

CODE_PATHS = {
    "decision_score_mode": REPO / "apps/decision-engine/src/decision_score_mode.py",
    "engine": REPO / "apps/decision-engine/src/engine.py",
    "slice_helpers": REPO / "apps/decision-engine/src/trisla09_slice_aware_helpers.py",
    "helm_values": REPO / "helm/trisla/values.yaml",
    "sem_intent": REPO / "apps/sem-csmf/src/models/intent.py",
    "sem_main": REPO / "apps/sem-csmf/src/main.py",
    "canonical_sla": REPO / "apps/sem-csmf/src/canonical_sla.py",
    "standards_3gpp": REPO / "docs/AUDIT_INTERFACES_3GPP_MAPPING.md",
    "standards_iface": REPO / "docs/interfaces/INTERFACE_STANDARDS_MAPPING.md",
    "paper_alignment": REPO / "docs/interfaces/PAPER_ALIGNMENT_NOTE.md",
    "publication_baseline": REPO
    / "evidencias_trisla_phase4_publication_consolidation_20260517T140548Z/analysis/publication_baseline_v1.json",
}

# Documented conceptual references (no .bib in repo — keys are audit placeholders)
DOC_REFERENCES = [
    ("network_slicing", "docs/TRISLA_CANONICAL_SLA_MODEL.md", "conceptual", "slice lifecycle / SLA model"),
    ("sla_management", "docs/TRISLA_E2E_FLOW_CANONICAL.md", "conceptual", "E2E SLA flow"),
    ("3gpp_slice_types", "docs/AUDIT_INTERFACES_3GPP_MAPPING.md", "conceptual", "CSMF/NSMF/NSSMF functional map"),
    ("etsi_nfv", "docs/interfaces/INTERFACE_STANDARDS_MAPPING.md", "conceptual", "ETSI ZSM management/assurance analogy"),
    ("oran", "docs/interfaces/INTERFACE_STANDARDS_MAPPING.md", "conceptual", "O-RAN O1-like observability (not protocol)"),
    ("urllc_embb_mmtc", "apps/sem-csmf/src/models/intent.py", "code", "SliceType enum URLLC/eMBB/mMTC"),
    ("sla_admission", "apps/decision-engine/src/decision_score_mode.py", "code", "score_mode admission"),
    ("feasibility", "apps/decision-engine/src/decision_score_mode.py:_extract_feasibility", "code", "latent term"),
    ("resource_headroom", "apps/decision-engine/src/decision_score_mode.py:resource_headroom", "code", "latent term"),
    ("multidomain_orchestration", "evidencias_trisla_true_multidomain_runtime_20260517T031129Z", "evidence", "master plan phases 1-8"),
    ("transport_informed_scoring", "evidencias_trisla_phase4_publication_consolidation_20260517T140548Z", "evidence", "frozen publication baseline"),
]


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_csv(path: Path, header: List[str], rows: List[List[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def _run_kubectl_freeze(out: Path) -> Tuple[bool, str]:
    freeze = out / "freeze"
    freeze.mkdir(parents=True, exist_ok=True)
    try:
        for scope, fname in [("deploy,svc,pods -A -o wide", "runtime_after.txt"), ("deploy,svc,pods -A -o yaml", "runtime_after.yaml")]:
            r = subprocess.run(
                ["kubectl", "get"] + scope.split(),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if r.returncode != 0:
                return False, r.stderr or r.stdout
            _write(freeze / fname, r.stdout)
        return True, "ok"
    except Exception as e:
        return False, str(e)


def _parse_phase3_raw() -> Dict[str, Any]:
    raw = SSOT_DIRS["phase3_revalidation"] / "phase_2_full_nasp_campaign/phase_1_extreme_runtime_stress/raw"
    stats: Dict[str, Any] = {
        "n": 0,
        "decision_source": Counter(),
        "contributing_factors": Counter(),
        "feasibility_present": 0,
        "pressure_present": 0,
        "transport_goodness_present": 0,
        "core_in_metadata": 0,
        "score_mode_n": 0,
        "slice_profile": Counter(),
        "slice_md_decision": Counter(),
        "INPUT_DEGRADED": 0,
    }
    if not raw.is_dir():
        return stats
    for p in raw.rglob("submit_*.json"):
        stats["n"] += 1
        m = json.loads(p.read_text(encoding="utf-8"))["payload"]["metadata"]
        ds = m.get("decision_source") or "unknown"
        stats["decision_source"][ds] += 1
        if m.get("core_cpu_input") is not None:
            stats["core_in_metadata"] += 1
        sm = m.get("slice_aware_multidomain") or {}
        if sm:
            stats["slice_md_decision"][sm.get("decision", "?")] += 1
        if ds == "decision_score_mode":
            stats["score_mode_n"] += 1
            ni = m.get("normalized_inputs") or {}
            sp = ni.get("slice_profile") or {}
            stats["slice_profile"][sp.get("slice", "?")] += 1
            if (ni.get("feasibility") or {}).get("value") is not None:
                stats["feasibility_present"] += 1
            if (ni.get("resource_pressure") or {}).get("value") is not None:
                stats["pressure_present"] += 1
            if (ni.get("transport_rtt") or {}).get("goodness") is not None:
                stats["transport_goodness_present"] += 1
            rc = m.get("reason_codes") or []
            if "INPUT_DEGRADED" in rc:
                stats["INPUT_DEGRADED"] += 1
            for t in m.get("contributing_factors") or []:
                stats["contributing_factors"][t.get("factor", "?")] += 1
    return stats


def phase1(out: Path) -> str:
    pdir = out / "phase_1_ssot_and_bib_audit"
    bib_found = list(REPO.rglob("*.bib"))
    ssot_ok = all(SSOT_DIRS[k].is_dir() for k in ("true_multidomain", "phase3_revalidation", "phase4_publication"))

    bib_rows = []
    for topic, loc, kind, note in DOC_REFERENCES:
        bib_rows.append([topic, f"DOC_REF_{topic.upper()}", loc, kind, note, "placeholder_no_bib_file"])

    _write_csv(
        pdir / "BIB_KEYS_MATRIX.csv",
        ["topic", "bib_key", "source_path", "source_kind", "notes", "bib_status"],
        bib_rows,
    )

    missing = """# Missing References

**Verdict context:** No official TriSLA `.bib` file exists in the repository (`find . -name '*.bib'` → 0).

## Impact

- Claims in papers must **not** cite BibTeX keys that are not in a committed bibliography file.
- Standards alignment (3GPP TS, ETSI GS, O-RAN WG) must use **explicit document IDs** from an external bib maintained outside this repo, or be labeled **missing reference**.

## Recommended external keys (NOT in repo — do not cite without adding bib)

| Intended topic | Status |
|----------------|--------|
| 3GPP TS 23.501 (5G system architecture) | missing reference |
| 3GPP TS 28.541 (NSI/NSSI management) | missing reference |
| ETSI GS NFV-MAN | missing reference |
| O-RAN Alliance architecture / O1 | missing reference |
| GSMA 5G Slicing documents | missing reference (see `docs/TRISLA_GSMA_ALIGNMENT_MASTER_RUNBOOK.md` for editorial notes only) |

## In-repo substitutes (audit-allowed)

| Artifact | Role |
|----------|------|
| `docs/AUDIT_INTERFACES_3GPP_MAPPING.md` | Functional 3GPP role mapping |
| `docs/interfaces/INTERFACE_STANDARDS_MAPPING.md` | Conceptual 3GPP/O-RAN/ETSI ZSM |
| `docs/interfaces/PAPER_ALIGNMENT_NOTE.md` | Allowed vs forbidden paper claims |
| `evidencias_trisla_true_multidomain_runtime_20260517T031129Z` | Program SSOT |
| `evidencias_trisla_phase4_publication_consolidation_20260517T140548Z` | Frozen publication baseline |
"""
    _write(pdir / "MISSING_REFERENCES.md", missing)

    ssot_lines = []
    for name, path in SSOT_DIRS.items():
        ssot_lines.append(f"- **{name}:** `{path}` — {'present' if path.is_dir() else 'MISSING'}")

    md = f"""# Phase 1 — SSOT and Bibliography Audit

**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}  
**Output:** `{out.name}`

## Verdict

**`{'SSOT_BIB_AUDIT_COMPLETE' if ssot_ok else 'SSOT_BIB_AUDIT_BLOCKED'}`**

---

## 1. SSOT program inventory

{chr(10).join(ssot_lines)}

**Master plan:** `evidencias_trisla_true_multidomain_runtime_20260517T031129Z/phase_0_master_plan/MASTER_PLAN.md`

States baseline: 3 active goodness terms (pre-transport); program goal ≥4 domains in score_mode (Phase 8). Transport Phase 1 **implemented** per Phase 4 baseline; Core/Feasibility/Headroom Phases 2–4 **planned, not approved for implementation** in this audit.

## 2. Publication baseline chain

| Step | Evidence folder |
|------|-----------------|
| Transport normalization | `evidencias_trisla_transport_normalization_20260517T120042Z` |
| Phase 2 DE integration | `evidencias_trisla_phase2_de_runtime_integration_20260517T125400Z` |
| Phase 3 revalidation (n=150) | `evidencias_trisla_phase3_runtime_revalidation_20260517T133134Z` |
| Phase 4 consolidation | `evidencias_trisla_phase4_publication_consolidation_20260517T140548Z` |

Frozen semantics: **RAN-dominant runtime-active transport-informed SLA scoring** (`publication_baseline_v1.json`).

## 3. Bibliography audit

| Finding | Evidence |
|---------|----------|
| Official `.bib` in repo | **None** ({len(bib_found)} files) |
| Documented conceptual refs | `BIB_KEYS_MATRIX.csv` (placeholder keys `DOC_REF_*`) |
| Missing normative bib keys | `MISSING_REFERENCES.md` |

## 4. Topic coverage (document/code/evidence)

| Topic | Supported by |
|-------|----------------|
| Network slicing / SLA | `docs/TRISLA_CANONICAL_SLA_MODEL.md`, SEM `SliceType` |
| 3GPP functional roles | `docs/AUDIT_INTERFACES_3GPP_MAPPING.md` |
| ETSI / O-RAN (conceptual) | `docs/interfaces/INTERFACE_STANDARDS_MAPPING.md` |
| URLLC/eMBB/mMTC | `apps/sem-csmf/src/models/intent.py`, DE profiles + `trisla09_slice_aware_helpers.py` |
| Feasibility / headroom | Code in `decision_score_mode.py`; runtime inactive in Phase 3 |
| Multidomain orchestration | Master plan + interface catalog |

## 5. HARD STOP

Await **`PHASE_1_APPROVED`** before treating Phase 2+ deliverables as approved for external claims.
"""
    _write(pdir / "SSOT_AND_BIB_AUDIT.md", md)
    return "SSOT_BIB_AUDIT_COMPLETE" if ssot_ok else "SSOT_BIB_AUDIT_BLOCKED"


def phase2(out: Path, p3: Dict[str, Any]) -> str:
    pdir = out / "phase_2_runtime_implementation_audit"
    sm_n = p3.get("score_mode_n", 0)
    factors = p3.get("contributing_factors", Counter())

    active_rows = [
        ["core_goodness", "NO", "decision_score_mode.py", "core_cpu_input in XAI only", "NOT_IMPLEMENTED"],
        ["transport_rtt_goodness", "YES" if p3.get("transport_goodness_present") else "PARTIAL", "decision_score_mode.py", f"{p3.get('transport_goodness_present',0)}/{sm_n} score_mode", "IMPLEMENTED_RUNTIME_ACTIVE"],
        ["feasibility", "CODE_ONLY", "_extract_feasibility", f"{p3.get('feasibility_present',0)}/{sm_n}", "IMPLEMENTED_LATENT"],
        ["resource_headroom", "CODE_ONLY", "g_press term", f"{p3.get('pressure_present',0)}/{sm_n}", "IMPLEMENTED_LATENT"],
        ["ran_prb_goodness", "YES", "score_mode + hard gates", "60/60 score_mode; 90 hard-gate paths", "IMPLEMENTED_RUNTIME_ACTIVE"],
        ["risk_inverse", "YES", "score_mode", "60/60", "IMPLEMENTED_RUNTIME_ACTIVE"],
        ["semantic_priority", "YES", "score_mode (default 0.55 if missing)", "60/60", "IMPLEMENTED_RUNTIME_ACTIVE"],
        ["core in legacy composite", "YES", "engine.py 0.7/0.2/0.1", "bypassed when score_mode or PRB hard gate", "IMPLEMENTED_OBSERVATIONAL_ONLY"],
    ]
    _write_csv(
        pdir / "ACTIVE_FACTORS_MATRIX.csv",
        ["factor", "in_score_numerator", "code_location", "runtime_evidence", "classification"],
        active_rows,
    )

    path_rows = [
        ["PRB_HARD_REJECT", "86/150", "engine.py hard gate", "Dominant path; no score_mode"],
        ["PRB_HARD_RENEGOTIATE", "4/150", "engine.py hard gate", "Dominant path"],
        ["decision_score_mode", "60/150", "decision_score_mode.py", "Weighted mean over active terms only"],
        ["slice_multidomain_severity_merge", "0 upgrades", "engine.py _merge_slice_multidomain_severity", "All slice_md.decision=ACCEPT in Phase 3"],
        ["legacy_composite", "fallback", "engine.py", "Not primary when DECISION_SCORE_MODE"],
    ]
    _write_csv(
        pdir / "SCORE_PATHS_MATRIX.csv",
        ["path", "count_or_role", "code", "notes"],
        path_rows,
    )

    md = f"""# Phase 2 — Runtime Implementation Audit

**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}

## Verdict

**`RUNTIME_IMPLEMENTATION_AUDIT_COMPLETE`**

---

## 1. Executive summary

| Capability | Status | Evidence |
|------------|--------|----------|
| Core-aware runtime scoring (score_mode numerator) | **NOT IMPLEMENTED** | No `core_goodness` in `contributing_factors`; `core_cpu_input` present 150/150 metadata only |
| Transport runtime scoring | **ACTIVE** | `transport_rtt_goodness` 60/60 score_mode; w=0.05, RTT_REF=12.21 ms |
| Feasibility admission term | **LATENT** | Code adds term if `feasibility_score` present; 0/60 runtime |
| Resource headroom term | **LATENT** | Code adds `resource_headroom` if pressure present; 0/60 runtime |
| Slice-specific score weights | **CODE YES / RUNTIME URLLC-ONLY** | Profiles URLLC/eMBB/mMTC in `default_profile()`; Phase 3 campaign uses URLLC template |
| PRB hard gates dominant | **YES** | 90/150 decisions via hard PRB thresholds |

## 2. Score_mode formula (frozen)

Active terms (Phase 3, n=60): {dict(factors)}

```
decision_score = sum(w_i * g_i) / sum(w_i)   # active terms only
g_transport = clamp01(1 - RTT_ms / 12.21)
w_transport = 0.05 (helm/trisla/values.yaml)
```

Inactive at runtime: `feasibility`, `resource_headroom` → `INPUT_DEGRADED` on all 60 score_mode samples.

## 3. Core telemetry vs scoring

- `engine.py` extracts `core_cpu_input` from telemetry snapshot.
- Passed to `score_mode_decide` but **never** enters numerator (only XAI metadata).
- Legacy path: `final_score = 0.7*ran + 0.2*transport + 0.1*core` when not hard-gated and not score_mode.

## 4. Helm / env evidence

`helm/trisla/values.yaml`: `TRISLA_TRANSPORT_RTT_REF_MS`, `TRISLA_TRANSPORT_SCORE_WEIGHT`, `TRISLA_TRANSPORT_RTT_GOODNESS_ENABLED`.

No helm keys for core goodness activation in score_mode.

## 5. Dataset evidence

Source: `evidencias_trisla_phase3_runtime_revalidation_20260517T133134Z` (n=150, NASP-hard+, real iperf).

Decision sources: {dict(p3.get('decision_source', {}))}

## 6. HARD STOP

Await **`PHASE_2_APPROVED`**.
"""
    _write(pdir / "RUNTIME_IMPLEMENTATION_AUDIT.md", md)
    return "RUNTIME_IMPLEMENTATION_AUDIT_COMPLETE"


def phase3_audit(out: Path, p3: Dict[str, Any]) -> str:
    pdir = out / "phase_3_slice_semantics_audit"
    # URLLC-only campaign evidence
    verdict = "SLICE_SEMANTICS_PARTIAL"

    behavior_rows = [
        ["URLLC", "default_profile w_feas=0.22 w_prb=0.22", "NASP-hard+ PAYLOAD type=URLLC", "60/60 score_mode use URLLC profile", "ACTIVE_WEIGHTS"],
        ["eMBB", "default_profile w_feas=0.20 w_prb=0.18", "SEM templates exist", "0 score_mode in Phase 3 campaign", "CODE_ONLY"],
        ["mMTC", "default_profile lower accept_min", "SEM templates exist", "0 score_mode in Phase 3 campaign", "CODE_ONLY"],
        ["slice_aware_multidomain", "SLICE_POLICY thresholds per slice", "trisla09_slice_aware_helpers.py", "150/150 slice_md=ACCEPT (no upgrade)", "ADJUNCT_NO_EFFECT"],
        ["SEM inference", "latency/reliability/devices heuristics", "canonical_sla + intent.py", "Multi-slice API supported", "IMPLEMENTED"],
        ["ML-NSMF", "core_cpu in features", "ml_client.py", "Not slice-differentiated in DE score", "PARTIAL"],
    ]
    _write_csv(
        pdir / "SLICE_TYPE_BEHAVIOR_MATRIX.csv",
        ["slice_type", "code_behavior", "template_payload", "phase3_runtime", "classification"],
        behavior_rows,
    )

    constraint_rows = [
        ["latency", "SEM SLARequirements + form_values", "Mapped to intent", "Not separate score term"],
        ["throughput", "SEM / templates", "Campaign URLLC 1000Mbps", "Metadata"],
        ["reliability", "SEM URLLC defaults 0.99999", "In payload", "Metadata"],
        ["PRB", "hard gates + ran_prb_goodness", "Dominates 90/150", "RUNTIME_ACTIVE"],
        ["transport RTT", "transport_rtt_goodness", "60/60 score_mode", "RUNTIME_ACTIVE"],
        ["core CPU", "slice policy thresholds", "Observational in score_mode", "NOT_IN_NUMERATOR"],
    ]
    _write_csv(
        pdir / "SLA_CONSTRAINTS_MATRIX.csv",
        ["constraint", "where_defined", "admission_effect", "runtime_status"],
        constraint_rows,
    )

    md = f"""# Phase 3 — Slice Semantics Audit (URLLC / eMBB / mMTC)

**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}

## Verdict

**`{verdict}`**

(Central question: TriSLA differentiates slices in **runtime admission**, not only metadata.)

---

## 1. Findings

| Layer | Differentiation | Evidence |
|-------|-----------------|----------|
| SEM-CSMF | **Yes** — `SliceType` enum, per-type SLA defaults, templates | `apps/sem-csmf/src/models/intent.py`, tests in `tests/test_canonical_sla.py` |
| DE score_mode weights | **Yes in code** — `default_profile(URLLC|mMTC|eMBB)` | `decision_score_mode.py` lines 49-77 |
| DE runtime (Phase 3) | **URLLC-only** — all 60 score_mode paths `slice_profile.slice=URLLC` | `scientific_multidomain_ieee_campaign.py` PAYLOAD; NASP-hard+ |
| Slice-aware multidomain | **Parallel severity model** — can upgrade decision | Phase 3: all `slice_aware_multidomain.decision=ACCEPT` → **no upgrades** |
| IEEE campaign (separate) | **Balanced n=30 per slice** | `docs/paper/results_and_discussion_ieee.txt` references n=90 dataset — **not** the frozen n=150 publication master |

## 2. Answer to central question

**Partial:** Slice type changes **weight profiles and threshold policies in code**, but the **frozen publication validation campaign** exercised **URLLC payloads only** for score_mode paths. eMBB/mMTC differentiation is **not proven** in the n=150 master dataset.

Hard PRB gates are **slice-agnostic** in the primary path (90/150).

## 3. slice_type as metadata?

For score_mode on NASP-hard+: slice drives **profile weights** but campaign fixed URLLC → **observed behavior is URLLC-specific**, not tri-slice comparative.

## 4. HARD STOP

Await **`PHASE_3_APPROVED`**.
"""
    _write(pdir / "SLICE_SEMANTICS_AUDIT.md", md)
    return verdict


def phase4(out: Path) -> str:
    pdir = out / "phase_4_standards_alignment_audit"
    claims = [
        ["CSMF-like SEM-CSMF", "3GPP CSMF functional", "YES", "docs/AUDIT_INTERFACES_3GPP_MAPPING.md", "Conceptual only"],
        ["NSMF-like ML-NSMF", "3GPP NSMF functional", "PARTIAL", "ml_client + DE", "Risk scoring, not full NSMF"],
        ["NSSMF-like NASP/bc-nssmf", "3GPP NSSMF / NSI", "PARTIAL", "nasp adapter instantiate", "REST not TS 28.541"],
        ["RAN/Transport/Core separation", "Domain model", "YES", "telemetry_snapshot domains", "Observability split"],
        ["free5GC core role", "5GC user plane", "PARTIAL", "Prometheus core_cpu", "Proxy metrics"],
        ["O-RAN observability", "O1-like", "PARTIAL", "Prometheus/RAN metrics", "Not O1 protocol"],
        ["ETSI NFV MANO orchestration", "NFV-MAN style", "PARTIAL", "Helm/K8s + portal", "Not ETSI SOL003 certified"],
        ["URLLC/eMBB/mMTC SST", "Slice service types", "PARTIAL", "SEM + DE profiles", "Runtime proof URLLC-only in n=150"],
        ["SLA-aware admission", "Governance", "YES", "score_mode + hard gates", "Allowed claim with stratification"],
        ["Lifecycle supervision", "SLA lifecycle", "PARTIAL", "sla-agent-layer revalidate/", "Not fully audited here"],
        ["O-RAN A1/E2 native", "Standard interfaces", "NO", "INTERFACE_STANDARDS_MAPPING.md", "Explicit gap"],
        ["3GPP FM/PM native", "Standard interfaces", "NO", "PAPER_ALIGNMENT_NOTE.md", "Use Prometheus proxy"],
    ]
    _write_csv(
        pdir / "STANDARDS_CLAIM_MATRIX.csv",
        ["claim", "standard_ref", "alignment", "evidence_path", "notes"],
        claims,
    )

    allowed = """# Claims Allowed for Paper (evidence-bound)

## Allowed (with caveats)

1. **Prototype exposes REST/Kafka workflows between CSMF-like, NSMF-like, and NSSMF-like functions** — cite interface audit, not protocol conformance.
2. **RAN-dominant, transport-informed SLA admission** under real NASP-hard+ stress (n=150, Phase 4 baseline) — stratify by `decision_source`.
3. **Slice-aware semantic modeling** at intent layer (URLLC/eMBB/mMTC types) — do not claim tri-slice runtime validation on n=150 unless new campaign added.
4. **Hard PRB governance gates** precede continuous scoring — boundary semantics evidence folders.

## Forbidden / high risk

1. "Implements O-RAN O1 / A1 / E2" — `docs/interfaces/PAPER_ALIGNMENT_NOTE.md`
2. "Native 3GPP FM/PM integration"
3. "True balanced multidomain runtime scoring" — SSOT master plan G8 not met (3–4 active terms, RAN dominates)
4. "Core-aware runtime scoring" in score_mode — **not implemented**
5. "Feasibility-aware admission" as runtime-active — **latent only**
6. Normative "compliant with TS 23.x" without bib + conformance proof

## Partial (conceptual alignment only)

- ETSI ZSM management/assurance **analogy**
- O-RAN **O1-like** observability via Prometheus
- GSMA slicing vocabulary **editorial** (`docs/TRISLA_GSMA_ALIGNMENT_MASTER_RUNBOOK.md`)
"""
    _write(pdir / "CLAIMS_ALLOWED_FOR_PAPER.md", allowed)

    md = f"""# Phase 4 — Standards Alignment Audit

**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}

## Verdict

**`STANDARDS_ALIGNMENT_PARTIAL`**

No normative 3GPP/ETSI/O-RAN requirements were invented. Alignment statements tie to **in-repo mapping docs** + **runtime/code evidence**.

---

## 1. Method

- Sources: `docs/AUDIT_INTERFACES_3GPP_MAPPING.md`, `docs/interfaces/INTERFACE_STANDARDS_MAPPING.md`, `docs/interfaces/PAPER_ALIGNMENT_NOTE.md`
- Bib: **none in repo** — normative TS references marked missing in Phase 1

## 2. Summary

| Standard family | Alignment level | Limit |
|-----------------|-----------------|-------|
| 3GPP (functional) | Partial | CSMF/NSMF/NSSMF roles mapped; no standardized NBI |
| ETSI NFV/ZSM | Partial | Orchestration pattern only |
| O-RAN | Partial | Observability analogy; no A1/E2/O1 protocol |
| URLLC/eMBB/mMTC | Partial | Modeled in SEM/DE; frozen runtime proof URLLC-heavy |

## 3. free5GC / NASP

Core metrics (`core_cpu_input`) collected; **not** active in score_mode numerator.

## 4. HARD STOP

Await **`PHASE_4_APPROVED`**.
"""
    _write(pdir / "STANDARDS_ALIGNMENT_AUDIT.md", md)
    return "STANDARDS_ALIGNMENT_PARTIAL"


def phase5(out: Path) -> str:
    pdir = out / "phase_5_gap_matrix"
    items = [
        ("core_runtime_scoring", "IMPLEMENTED_OBSERVATIONAL_ONLY", "core_cpu in metadata; no core_goodness term"),
        ("transport_runtime_scoring", "IMPLEMENTED_RUNTIME_ACTIVE", "transport_rtt_goodness 60/60 score_mode"),
        ("feasibility", "IMPLEMENTED_LATENT", "_extract_feasibility; 0/60 populated"),
        ("resource_headroom", "IMPLEMENTED_LATENT", "g_press; 0/60 populated"),
        ("slice_specific_admission", "IMPLEMENTED_LATENT", "Profiles exist; Phase 3 URLLC-only score_mode"),
        ("urllc_embb_mmtc_differentiation", "SLICE_SEMANTICS_PARTIAL", "SEM yes; runtime proof partial"),
        ("3gpp_alignment", "DOCUMENTED_ONLY", "Functional mapping docs; no conformance"),
        ("etsi_alignment", "DOCUMENTED_ONLY", "ZSM analogy in INTERFACE_STANDARDS_MAPPING"),
        ("oran_alignment", "DOCUMENTED_ONLY", "O1-like stated; protocol gap explicit"),
        ("lifecycle_supervision", "IMPLEMENTED_OBSERVATIONAL_ONLY", "sla-agent revalidate module present"),
        ("governance_persistence", "IMPLEMENTED_RUNTIME_ACTIVE", "bc-nssmf register-sla path (not re-audited E2E)"),
        ("true_multidomain_scoring_G8", "UNSUPPORTED_CLAIM", "SSOT requires ≥4 active domains; 4 terms but 2 latent"),
        ("prb_hard_gate_dominance", "IMPLEMENTED_RUNTIME_ACTIVE", "90/150 decisions"),
    ]
    _write_csv(pdir / "GAP_MATRIX.csv", ["item", "classification", "evidence"], items)

    md = "# Phase 5 — Gap Matrix\n\n## Verdict\n\n**`GAP_MATRIX_COMPLETE`**\n\n"
    md += "| Item | Classification | Evidence |\n|------|----------------|----------|\n"
    for row in items:
        md += f"| {row[0]} | {row[1]} | {row[2]} |\n"
    md += "\n## PAPER_CLAIM_RISK\n\nSee `PAPER_CLAIM_RISK.md`.\n\n## HARD STOP\n\nAwait **`PHASE_5_APPROVED`**.\n"
    _write(pdir / "GAP_MATRIX.md", md)

    risk = """# Paper Claim Risk Register

| Claim | Risk | Mitigation |
|-------|------|------------|
| Multidomain runtime scoring | **HIGH** | Say transport-informed; stratify PRB hard gate vs score_mode |
| Core-aware admission | **HIGH** | Remove or label observational-only |
| Feasibility/headroom aware | **HIGH** | State code exists; runtime inactive |
| Tri-slice experimental equality | **MEDIUM** | Use IEEE n=90 campaign separately; not n=150 master |
| 3GPP/O-RAN compliance | **HIGH** | Conceptual mapping only |
| RAN-dominant admission | **LOW** | Supported Phase 3 r(PRB,score)≈-0.99 in score_mode stratum |
"""
    _write(pdir / "PAPER_CLAIM_RISK.md", risk)
    return "GAP_MATRIX_COMPLETE"


def phase6(out: Path) -> str:
    pdir = out / "phase_6_evolution_plan"
    plan = """# Controlled Evolution Plan (audit-only — DO NOT IMPLEMENT)

**Verdict:** `CONTROLLED_EVOLUTION_PLAN_READY`

Each item requires prior phase approval tokens and separate implementation prompts per SSOT master plan.

---

## Gap 1 — Core goodness in score_mode (Master plan Phase 2)

| Field | Value |
|-------|-------|
| Gap evidence | Phase 2 audit: no `core_goodness` in contributing_factors |
| Files | `apps/decision-engine/src/decision_score_mode.py`, tests, `helm/trisla/values.yaml` |
| Scientific risk | Medium — may dilute RAN dominance; must preserve monotonicity |
| Operational risk | Medium — unit mismatch on CPU (see trisla09 percent sanity) |
| Rollback | DE digest `sha256:64146e3ce1e9a7b52e159b81afa46f11b08e19c1ae96c69f7f122146de3fdf661` |
| Deploy | GHCR digest-only per `DEPLOY_POLICY.md` |
| Validation | NASP-hard+ rerun; corr(core_cpu, score); reconstruction error <1e-6 |
| Claim if validated | "Core-informed (not core-dominant) transport+RAN scoring" |

## Gap 2 — Feasibility activation (Phase 3)

| Field | Value |
|-------|-------|
| Gap | `feasibility` term latent; INPUT_DEGRADED 60/60 |
| Files | SEM context wiring, `decision_score_mode.py`, portal/nasp if needed |
| Validation | Non-null `feasibility_score` from real nest/SLA pipeline |
| Claim | "Feasibility-aware admission" only after populated runtime proof |

## Gap 3 — Resource headroom (Phase 4)

| Field | Value |
|-------|-------|
| Gap | `resource_pressure` always missing |
| Files | DE + telemetry pressure band path |
| Validation | Pressure rises under load regimes |

## Gap 4 — Slice-specific runtime proof

| Field | Value |
|-------|-------|
| Gap | URLLC-only in n=150 master |
| Files | Campaign script payloads (eMBB/mMTC templates), no DE change required for proof-only |
| Validation | Balanced n per slice + stratified stats |

## Gap 5 — Slice-aware severity merge inactive

| Field | Value |
|-------|-------|
| Gap | slice_md always ACCEPT in Phase 3 |
| Files | Review thresholds vs observed telemetry in `trisla09_slice_aware_helpers.py` |
| Risk | May increase REJECT rate — boundary revalidation required |

---

## DO NOT (without explicit approval)

- Change PRB hard thresholds
- Increase w_transport above 0.10
- Use simulator / synthetic telemetry
- Deploy `:latest`
- Merge IEEE n=90 claims into n=150 master without relabeling
"""
    _write(pdir / "CONTROLLED_EVOLUTION_PLAN.md", plan)

    roadmap = """# Phased Implementation Roadmap (proposal)

| Order | SSOT phase | Prerequisite | Deliverable |
|------:|------------|--------------|-------------|
| A | Core goodness | PHASE_2_APPROVED (this audit) + implementation token | g_core term + campaign |
| B | Feasibility | PHASE_3_APPROVED + wiring | live feasibility term |
| C | Resource headroom | PHASE_4_APPROVED + pressure path | live headroom term |
| D | Multidomain validation | Phases A–C | Phase 5–7 SSOT campaigns |
| E | Publication Q1 | Phase 8 | Updated claims matrix |

**Current frozen baseline remains authoritative until a new digest is validated.**
"""
    _write(pdir / "PHASED_IMPLEMENTATION_ROADMAP.md", roadmap)

    dont = """# DO NOT IMPLEMENT YET

1. Core goodness — await `PHASE_1_APPROVED` … `PHASE_5_APPROVED` + explicit implementation prompt
2. Feasibility / headroom activation — same
3. Slice weight retuning — forbidden in audit phase
4. PRB threshold changes — Phase 6 boundary audit in SSOT only after functional phases
5. Any deploy without skopeo-verified GHCR digest
"""
    _write(pdir / "DO_NOT_IMPLEMENT_YET.md", dont)
    return "CONTROLLED_EVOLUTION_PLAN_READY"


def main() -> None:
    ts = _utc_stamp()
    out = REPO / f"evidencias_trisla_core_feasibility_multidomain_audit_{ts}"
    for sub in (
        "phase_1_ssot_and_bib_audit",
        "phase_2_runtime_implementation_audit",
        "phase_3_slice_semantics_audit",
        "phase_4_standards_alignment_audit",
        "phase_5_gap_matrix",
        "phase_6_evolution_plan",
        "analysis",
        "freeze",
        "rollback",
        "logs",
    ):
        (out / sub).mkdir(parents=True, exist_ok=True)

    p3 = _parse_phase3_raw()
    v1 = phase1(out)
    v2 = phase2(out, p3)
    v3 = phase3_audit(out, p3)
    v4 = phase4(out)
    v5 = phase5(out)
    v6 = phase6(out)

    ok, msg = _run_kubectl_freeze(out)
    _write(out / "logs" / "kubectl_freeze.log", f"success={ok}\n{msg}\n")

    manifest = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    _write(out / "analysis" / "MANIFEST.txt", "\n".join(manifest) + "\n")

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(out),
        "verdicts": {
            "phase_1": v1,
            "phase_2": v2,
            "phase_3": v3,
            "phase_4": v4,
            "phase_5": v5,
            "phase_6": v6,
        },
        "kubectl_freeze": ok,
    }
    _write(out / "analysis" / "AUDIT_SUMMARY.json", json.dumps(summary, indent=2))
    print(f"CORE FEASIBILITY MULTIDOMAIN AUDIT COMPLETED: {out}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
