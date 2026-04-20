#!/usr/bin/env python3
"""PROMPT_230 — campanha complementar de contraste (PRB + submissões reais), sem substituir o dataset Fase 2 base."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SSOT = ROOT / "evidencias_resultados_trisla_baseline_v8"
OUTDIR = SSOT / "dataset" / "fase2_contrast"
ANADIR = SSOT / "analysis" / "fase2_contrast"

sys.path.insert(0, str(ROOT / "scripts" / "e2e"))
from trisla_closure_common import extract_row_from_submit, submit_sla, trace_hits  # noqa: E402

FORMS: dict[str, dict[str, Any]] = {
    "urllc": {"latency": "10ms", "reliability": 0.999, "throughput": "100Mbps"},
    "embb": {"latency": "20ms", "reliability": 0.99, "throughput": "500Mbps"},
    "mmtc": {"latency": "50ms", "reliability": 0.99, "throughput": "50Mbps"},
}

# Perfis mais contrastantes: (tag, template, iperf -u -b, form overrides)
PROFILES: list[dict[str, Any]] = [
    {
        "tag": "contrast_low",
        "template": "urllc",
        "iperf_b": "8M",
        "form": {**FORMS["urllc"], "latency": "2ms", "throughput": "8Mbps"},
    },
    {
        "tag": "contrast_medium",
        "template": "embb",
        "iperf_b": "35M",
        "form": {**FORMS["embb"], "throughput": "35Mbps", "latency": "15ms"},
    },
    {
        "tag": "contrast_high",
        "template": "mmtc",
        "iperf_b": "60M",
        "form": {**FORMS["mmtc"], "throughput": "60Mbps", "latency": "80ms"},
    },
    {
        "tag": "contrast_stress",
        "template": "urllc",
        "iperf_b": "80M",
        "form": {**FORMS["urllc"], "latency": "1ms", "reliability": 0.99999, "throughput": "800Mbps"},
    },
]


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for cand in (p.parents[2], p.parents[1]):
        if (cand / "evidencias_resultados_trisla_baseline_v8").is_dir():
            return cand
    return p.parents[2]


def _start_iperf_udp(bitrate: str, server: str) -> subprocess.Popen:
    return subprocess.Popen(
        [
            "kubectl",
            "-n",
            "ueransim",
            "exec",
            "deploy/ueransim-singlepod",
            "-c",
            "ue",
            "--",
            "iperf3",
            "-B",
            "10.1.0.1",
            "-c",
            server,
            "-u",
            "-b",
            bitrate,
            "-t",
            "45",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    global ROOT, SSOT, OUTDIR, ANADIR
    ROOT = _repo_root()
    SSOT = ROOT / "evidencias_resultados_trisla_baseline_v8"
    OUTDIR = SSOT / "dataset" / "fase2_contrast"
    ANADIR = SSOT / "analysis" / "fase2_contrast"
    OUTDIR.mkdir(parents=True, exist_ok=True)
    ANADIR.mkdir(parents=True, exist_ok=True)

    n = max(1, int(os.environ.get("TRISLA_CONTRAST_ITER_PER_SCENARIO", "30")))
    pause = float(os.environ.get("TRISLA_CONTRAST_SLEEP_S", "1"))
    server = os.environ.get("TRISLA_FASE2_IPERF_SERVER", "192.168.100.51")
    run_tag = str(int(time.time()))
    raw_path = OUTDIR / "dataset_fase2_contrast_raw.csv"
    rows: list[dict[str, Any]] = []

    prom_url = os.environ.get("TRISLA_PROMETHEUS_QUERY_URL", "")
    probe_script = ROOT / "scripts" / "fase2_prb_variability_probe.py"

    for prof in PROFILES:
        tag = prof["tag"]
        template = prof["template"]
        fv = dict(prof["form"])
        print(f"[INFO] Perfil={tag} template={template} iperf={prof['iperf_b']}", flush=True)
        proc = _start_iperf_udp(prof["iperf_b"], server)
        time.sleep(3)
        if prom_url and probe_script.is_file():
            env = {**os.environ, "TRISLA_PROMETHEUS_QUERY_URL": prom_url}
            probe_out = ANADIR / f"prb_probe_{tag}.txt"
            try:
                subprocess.run(
                    [sys.executable, str(probe_script)],
                    env=env,
                    stdout=open(probe_out, "w", encoding="utf-8"),
                    stderr=subprocess.STDOUT,
                    timeout=120,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError) as e:
                probe_out.write_text(f"[WARN] probe falhou: {e}\n", encoding="utf-8")

        for i in range(n):
            tenant = f"prompt230_{tag}_{i}_{run_tag}"
            scen_id = f"P230_{tag}_{i}"
            data, http_st, err = submit_sla(template, tenant, fv)
            intent_id = str(data.get("intent_id") or "")
            hits = trace_hits(intent_id) if intent_id else trace_hits("")
            row = extract_row_from_submit(scen_id, "P230_CONTRAST", data, http_st, err, hits)
            row["fase2_scenario"] = tag
            row["fase2_template"] = template
            rows.append(row)
            ok = err is None and http_st == 200
            print(f"[{'OK' if ok else 'ERRO'}] {tag} {i + 1}/{n} http={http_st}", flush=True)
            time.sleep(pause)

        proc.wait(timeout=120)

    pd.DataFrame(rows).to_csv(raw_path, index=False)
    print(f"[OK] {len(rows)} linhas -> {raw_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
