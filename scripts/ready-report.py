#!/usr/bin/env python3
"""
TriSLA - READY REPORT GENERATOR

Gera um snapshot de prontidão do TriSLA usando o módulo heartbeat.py:

Saídas:
- docs/READY_STATUS_TRI-SLA_v1.md
- docs/READY_STATUS_TRI-SLA_v1.json
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import sys

# Importar o heartbeat do mesmo diretório
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))

import heartbeat  # noqa: E402


def ensure_dirs():
    (REPO_ROOT / "docs").mkdir(exist_ok=True)
    (REPO_ROOT / "logs").mkdir(exist_ok=True)


def render_markdown(result: dict) -> str:
    ts = result["timestamp"]
    overall = result["overall_status"]
    checks = result["checks"]

    lines = []
    lines.append(f"# TriSLA — READY STATUS REPORT")
    lines.append("")
    lines.append(f"- Gerado em: `{ts}` (UTC)")
    lines.append(f"- Status geral: **{overall}**")
    lines.append("")
    lines.append("## Tabela de módulos")
    lines.append("")
    lines.append("| Módulo           | Tipo   | Alvo                         | Status | Detalhe |")
    lines.append("|------------------|--------|------------------------------|--------|---------|")
    for c in checks:
        lines.append(
            f"| {c['name']:<17} | {c['type']:<6} | {c['target']:<28} | {c['status']:<6} | {c['detail']} |"
        )

    lines.append("")
    lines.append("## Observações automáticas")
    lines.append("")

    if overall == "HEALTHY":
        lines.append(
            "- Todos os módulos principais responderam com sucesso. Ambiente considerado **PRONTO** para testes e operações planejadas."
        )
    elif overall == "DEGRADED":
        lines.append(
            "- Pelo menos um módulo está saudável e pelo menos um módulo falhou. Ambiente em modo **DEGRADADO**. Recomenda-se análise antes de operações críticas."
        )
    else:
        lines.append(
            "- Todos os módulos avaliados reportaram falhas. Ambiente em estado **NÃO PRONTO**. Não é recomendado seguir com operações críticas."
        )

    lines.append("")
    lines.append("> Relatório gerado automaticamente pelo `scripts/ready-report.py` (TriSLA DevOps).")
    return "\n".join(lines)


def main():
    ensure_dirs()
    result = heartbeat.run_all_checks()

    ts = datetime.now(timezone.utc).isoformat()
    json_path = REPO_ROOT / "docs" / "READY_STATUS_TRI-SLA_v1.json"
    md_path = REPO_ROOT / "docs" / "READY_STATUS_TRI-SLA_v1.md"

    # JSON
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Markdown
    md_content = render_markdown(result)
    with md_path.open("w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[TriSLA READY REPORT] {ts} — Status geral: {result['overall_status']}")
    print(f"[TriSLA READY REPORT] Arquivo Markdown: {md_path}")
    print(f"[TriSLA READY REPORT] Arquivo JSON:     {json_path}")


if __name__ == "__main__":
    main()

