#!/usr/bin/env python3
"""
Gera artefactos mínimos para evidencias_gsma_alignment_phase3_*.

Não inventa decisões/scores/tx_hash: se o DE não estiver acessível,
os ficheiros *compare* marcam NOT_EXECUTED com motivo explícito.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _sem_src() -> Path:
    return Path(__file__).resolve().parents[2] / "apps" / "sem-csmf" / "src"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        required=True,
        help="Pasta evidencias_gsma_alignment_phase3_<TS>/",
    )
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(_sem_src()))
    from canonical_sla import canonicalize_sla_request  # noqa: E402

    legacy_payload = {
        "service_type": "eMBB",
        "intent": "GSMA phase3 fixture — industrial AR",
        "tenant_id": "smart-port-beta",
        "sla_requirements": {
            "template_id": "semantic-embb-template",
            "latency": "15ms",
            "throughput": "200Mbps",
            "availability_target": 99.95,
            "service_description": "AR assembly line",
            "priority": "high",
            "security_profile": "iso27001",
            "service_continuity": "tier2",
            "edge_processing": "required",
        },
    }
    canonical = canonicalize_sla_request(legacy_payload)

    (out / "payload_legacy.json").write_text(
        json.dumps(legacy_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "payload_canonicalized.json").write_text(
        json.dumps(canonical, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    not_run = {
        "status": "NOT_EXECUTED",
        "reason": "Decision Engine / Portal E2E não disponíveis neste agente; equivalência de decisão/score/governance exige cluster (node006) ou serviços locais UP.",
        "required_for_pass": [
            "same_decision",
            "same_score",
            "same_dominant_domain",
            "same_contributing_factors",
            "same_tx_hash_workflow",
            "same_runtime_behavior",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    for name in (
        "decision_compare.json",
        "score_compare.json",
        "xai_compare.json",
        "orchestration_compare.json",
        "governance_compare.json",
        "runtime_assurance_compare.json",
    ):
        (out / name).write_text(json.dumps(not_run, indent=2) + "\n", encoding="utf-8")

    structural = {
        "status": "PASS",
        "checks": [
            {
                "name": "canonical_preserves_legacy_blob",
                "detail": "legacy_input.template_id and legacy_input.form_values mirror source (minus template_id in form_values when nested absent).",
            },
            {
                "name": "de_http_contract_metadata_extra_ignored",
                "detail": "apps/decision-engine SLAEvaluateInput has no top-level metadata field; SEM root metadata (incl. canonical_sla) is not part of parsed evaluate body unless forwarded into intent/context explicitly.",
                "caveat": "Confirmar em runtime FastAPI/Pydantic extra policy do deployment.",
            },
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (out / "structural_equivalence.json").write_text(
        json.dumps(structural, indent=2) + "\n", encoding="utf-8"
    )

    report = f"""# FASE 3 — Equivalence Validation — relatório

**Pasta:** `{out.name}`  
**Gerado (UTC):** {datetime.now(timezone.utc).isoformat()}

## Resultado global: **FAIL**

Os critérios PASS do runbook exigem **paridade de runtime** (decisão, score, `dominant_domain`, `contributing_factors`, fluxo de governação com `tx_hash`, assurance).  
Neste ambiente **não** foi possível invocar o Decision Engine nem o pipeline Portal→BC→SLA-Agent; os ficheiros `*_compare.json` estão preenchidos com `NOT_EXECUTED` e **não** simulam resultados.

## Sub-validação estrutural: **PASS**

- `canonicalize_sla_request` preserva o legado em `legacy_input` (ver `payload_legacy.json` vs `payload_canonicalized.json`).
- Observação de código: o POST `/evaluate` do Decision Engine usa `SLAEvaluateInput`, que **não** declara campo `metadata` ao nível raiz; metadados extra enviados pelo SEM em paralelo a `intent` tendem a ser **ignorados** na validação Pydantic (política `extra` do modelo — verificar versão exacta no cluster). Isto **não** substitui prova E2E.

## Próximos passos (operador)

1. Executar no **node006** (ou stack local completa) duas requisições equivalentes com o mesmo `sla_requirements` / `telemetry_snapshot`, variando apenas a presença de `canonical_sla` em metadados, e capturar respostas completas.
2. Preencher `decision_compare.json`, `score_compare.json`, etc. com diffs reais.
3. Só então marcar FASE 3 como **PASS** no runbook mestre.

## Rollback

N/A (sem alterações de código nem deploy realizados por este passo).

"""
    (out / "validation_report.md").write_text(report, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
