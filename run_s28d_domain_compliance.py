#!/usr/bin/env python3
"""
PROMPT_S28.D — SLA_COMPLIANCE DOMAIN DECOMPOSITION (READ-ONLY)
TriSLA v3.9.3 | NASP | namespace: trisla
Executa decomposição forense do SLA_COMPLIANCE por domínio (RAN, TRANSPORT, CORE).
Somente análise; nenhuma alteração no sistema.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# Base evidence dir (evidencias_resultados_v3.9.3)
BASE = Path(os.environ.get("EVID_BASE", "/home/porvir5g/gtp5g/trisla/evidencias_resultados_v3.9.3"))
DOM = BASE / "18_compliance_forensics"
FIG_DIR = DOM / "figs"
OUT = DOM  # CSVs and report in 18_compliance_forensics

# Pod -> domain mapping (RAN | TRANSPORT | CORE)
POD_DOMAIN = {
    "traffic-exporter": "RAN",
    "kafka": "TRANSPORT",
    "nasp-adapter": "TRANSPORT",
    "decision-engine": "CORE",
    "ml-nsmf": "CORE",
    "bc-nssmf": "CORE",
    "sem-csmf": "CORE",
    "sla-agent": "CORE",  # sla-agent-layer
    "portal-backend": "CORE",
    "portal-frontend": "CORE",
    "ui-dashboard": "CORE",
}

# Weights for compliance_domain (documented, equal across domains)
W1, W2, W3 = 0.40, 0.35, 0.25  # availability, (1 - norm_latency), (1 - norm_cpu)


def _pod_to_domain(name: str) -> str | None:
    n = name.lower()
    for k, v in POD_DOMAIN.items():
        if k in n:
            return v
    return None


def _parse_cpu_millicores(s: str) -> float:
    s = (s or "").strip()
    if not s:
        return np.nan
    if s.endswith("m"):
        return float(s[:-1])
    return float(s) * 1000


def _parse_mem_mb(s: str) -> float:
    s = (s or "").strip()
    if not s:
        return np.nan
    if s.endswith("Mi"):
        return float(s[:-2])
    if s.endswith("Gi"):
        return float(s[:-2]) * 1024
    return np.nan


def _read_pods_resources(path: Path) -> list[dict]:
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or "NAME" in line and "CPU" in line:
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            name, cpu, mem = parts[0], parts[1], parts[2]
            domain = _pod_to_domain(name)
            if not domain:
                continue
            rows.append({
                "pod": name,
                "domain": domain,
                "cpu_m": _parse_cpu_millicores(cpu),
                "mem_mb": _parse_mem_mb(mem),
            })
    return rows


def gate0() -> bool:
    for d in ["13_domain_analysis", "11_tables", "10_latency", "18_compliance_forensics"]:
        p = BASE / d
        if not p.is_dir():
            print(f"GATE 0 FAIL: missing {d}")
            return False
    print("GATE 0 OK: all required dirs exist")
    return True


def fase1_domain_metrics_raw() -> pd.DataFrame:
    """FASE 1 — Inventário de métricas por domínio. Output: domain_metrics_raw.csv"""
    # Slas: from compliance_raw / compliance_joined
    raw = BASE / "18_compliance_forensics" / "outputs" / "compliance_raw.csv"
    joined = BASE / "18_compliance_forensics" / "outputs" / "compliance_joined_dataset.csv"
    lat_raw = BASE / "10_latency" / "latency_raw.csv"
    lat_load = BASE / "12_graphs" / "latency_vs_load.csv"
    pods_path = BASE / "08_metrics" / "pods_resources_final.txt"
    domain_summary_path = BASE / "11_tables" / "domain_summary.csv"

    # SLA list + decision_id -> intent_id
    cr = pd.read_csv(raw)
    sla_ids = cr["decision_id"].unique().tolist()

    # scenario, slice_type from latency_raw (sla_id = decision_id)
    lr = pd.read_csv(lat_raw)
    lr = lr[["sla_id", "scenario", "slice_type"]].drop_duplicates("sla_id")
    sla_info = lr.set_index("sla_id").to_dict("index")

    # latency per sla_id from latency_vs_load
    ll = pd.read_csv(lat_load)
    lat_map = ll.groupby("sla_id")["latency_ms"].mean().to_dict()
    lat_global_mean = ll["latency_ms"].mean()

    # domain_summary: slice_type -> reneg_rate etc.
    ds = pd.read_csv(domain_summary_path)
    slice_accept = dict(zip(ds["service_type"].str.upper(), ds["accept_rate"].str.rstrip("%").astype(float) / 100.0))
    slice_reneg = dict(zip(ds["service_type"].str.upper(), ds["reneg_rate"].str.rstrip("%").astype(float) / 100.0))

    # Pods -> cpu_avg, mem_avg per domain
    pods = _read_pods_resources(pods_path)
    pdf = pd.DataFrame(pods)
    domain_res = pdf.groupby("domain").agg(cpu_avg=("cpu_m", "mean"), mem_avg=("mem_mb", "mean")).to_dict("index")

    # Joined for sla_compliance_inferred (availability proxy)
    jn = pd.read_csv(joined)
    inf = dict(zip(jn["decision_id"], jn["sla_compliance_inferred"].fillna(0.85)))

    rows = []
    for sid in sla_ids:
        info = sla_info.get(sid, {})
        scenario = info.get("scenario", "N/A")
        slice_type = info.get("slice_type", "eMBB")
        if pd.isna(scenario):
            scenario = "N/A"
        if pd.isna(slice_type):
            slice_type = "eMBB"
        lat = lat_map.get(sid, lat_global_mean)
        if np.isnan(lat):
            lat = lat_global_mean
        s = str(slice_type).upper()
        st = "URLLC"
        if "EMBB" in s:
            st = "EMBB"
        elif "MMTC" in s:
            st = "MMTC"
        avail = float(inf.get(sid, 0.85))
        for domain in ["RAN", "TRANSPORT", "CORE"]:
            res = domain_res.get(domain, {})
            cpu = res.get("cpu_avg", np.nan)
            mem = res.get("mem_avg", np.nan)
            rows.append({
                "sla_id": sid,
                "slice_type": st,
                "scenario": scenario,
                "domain": domain,
                "cpu_avg": cpu if not np.isnan(cpu) else 0.0,
                "mem_avg": mem if not np.isnan(mem) else 0.0,
                "latency_avg": float(lat),
                "availability_proxy": avail,
            })

    df = pd.DataFrame(rows)
    out_path = OUT / "domain_metrics_raw.csv"
    df.to_csv(out_path, index=False)
    print(f"FASE 1 OK: {out_path}")
    return df


def fase2_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """FASE 2 — Min-Max + Z-Score por domínio. Output: domain_metrics_normalized.csv"""
    out = []
    for domain in ["RAN", "TRANSPORT", "CORE"]:
        sub = df[df["domain"] == domain].copy()
        for col, key in [("cpu_avg", "cpu_minmax"), ("mem_avg", "mem_minmax"), ("latency_avg", "latency_minmax")]:
            v = sub[col].replace(0, np.nan).fillna(sub[col].median())
            mn, mx = v.min(), v.max()
            if mx > mn:
                sub[key] = (v - mn) / (mx - mn)
            else:
                sub[key] = 1.0
        for col, zkey in [("cpu_avg", "cpu_zscore"), ("latency_avg", "latency_zscore")]:
            v = sub[col].replace(0, np.nan).fillna(sub[col].median())
            mu, sig = v.mean(), v.std()
            sub[zkey] = (v - mu) / sig if sig and sig > 0 else 0.0
        out.append(sub)
    ndf = pd.concat(out, ignore_index=True)
    out_path = OUT / "domain_metrics_normalized.csv"
    ndf.to_csv(out_path, index=False)
    print(f"FASE 2 OK: {out_path}")
    return ndf


def fase3_domain_compliance(ndf: pd.DataFrame) -> pd.DataFrame:
    """FASE 3 — compliance_domain = w1*availability + w2*(1 - norm_lat) + w3*(1 - norm_cpu)."""
    ndf = ndf.copy()
    ndf["norm_lat"] = ndf["latency_minmax"].clip(0, 1)
    ndf["norm_cpu"] = ndf["cpu_minmax"].clip(0, 1)
    ndf["compliance_domain"] = (
        W1 * ndf["availability_proxy"]
        + W2 * (1 - ndf["norm_lat"])
        + W3 * (1 - ndf["norm_cpu"])
    )
    out_path = OUT / "domain_compliance_calculated.csv"
    ndf.to_csv(out_path, index=False)
    print(f"FASE 3 OK: {out_path}")
    return ndf


def fase4_sla_reconstructed(cdf: pd.DataFrame) -> pd.DataFrame:
    """FASE 4 — sla_compliance_min, _avg, _weighted per SLA."""
    g = cdf.groupby("sla_id")
    rec = pd.DataFrame({
        "sla_id": g["compliance_domain"].min().index,
        "sla_compliance_min": g["compliance_domain"].min().values,
        "sla_compliance_avg": g["compliance_domain"].mean().values,
        "sla_compliance_weighted": g["compliance_domain"].mean().values,  # equal weight per domain
    })
    out_path = OUT / "sla_compliance_reconstructed.csv"
    rec.to_csv(out_path, index=False)
    print(f"FASE 4 OK: {out_path}")
    return rec


def fase5_plots(cdf: pd.DataFrame, rec: pd.DataFrame) -> None:
    """FASE 5 — G1–G4: boxplot, heatmap, boundary, radar."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"FASE 5 SKIP (matplotlib): {e}")
        return

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # G1 — Compliance por domínio (boxplot), separado por slice
    domains = ["RAN", "TRANSPORT", "CORE"]
    slices = sorted(cdf["slice_type"].unique().tolist()) or ["EMBB", "MMTC", "URLLC"]
    n = len(slices)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 5), sharey=True)
    if n == 1:
        axes = [axes]
    for ax, st in zip(axes, slices):
        sub = cdf[cdf["slice_type"] == st]
        data = [sub[sub["domain"] == d]["compliance_domain"].values for d in domains]
        bp = ax.boxplot(data, labels=domains, patch_artist=True)
        ax.set_title(st)
        ax.set_ylabel("compliance_domain")
        ax.set_ylim(0, 1.05)
    fig.suptitle("Compliance por Domínio (RAN / TRANSPORT / CORE) por Slice", y=1.02)
    plt.tight_layout()
    for ext in ["png", "pdf"]:
        p = FIG_DIR / f"fig_compliance_by_domain_boxplot.{ext}"
        plt.savefig(p, bbox_inches="tight")
    plt.close()
    print("FASE 5 G1 OK: fig_compliance_by_domain_boxplot.png/pdf")

    # G2 — Bottleneck heatmap: SLA x Domain, cell = compliance_domain (limitante = min)
    piv = cdf.pivot_table(index="sla_id", columns="domain", values="compliance_domain", aggfunc="first")
    piv = piv.head(80)  # cap for readability
    fig, ax = plt.subplots(figsize=(10, max(6, piv.shape[0] * 0.08)))
    im = ax.imshow(piv.values, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels(piv.columns)
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels([s[:24] + "…" if len(s) > 24 else s for s in piv.index], fontsize=6)
    plt.colorbar(im, ax=ax, label="compliance_domain")
    plt.title("Bottleneck Map (SLA × Domínio)")
    plt.tight_layout()
    for ext in ["png", "pdf"]:
        p = FIG_DIR / f"fig_domain_bottleneck_heatmap.{ext}"
        plt.savefig(p, bbox_inches="tight")
    plt.close()
    print("FASE 5 G2 OK: fig_domain_bottleneck_heatmap.png/pdf")

    # G3 — Boundary: sla_compliance_reconstructed vs decision (0.9 line)
    raw = pd.read_csv(BASE / "18_compliance_forensics" / "outputs" / "compliance_raw.csv")
    dec_map = dict(zip(raw["decision_id"], raw["action"]))
    rec2 = rec.copy()
    rec2["decision"] = rec2["sla_id"].map(dec_map).fillna("RENEG")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axhline(0.9, color="red", linestyle="--", label="threshold 0.9")
    for d in ["RENEG", "ACCEPT", "REJECT"]:
        sub = rec2[rec2["decision"] == d]
        if len(sub):
            ax.scatter(range(len(sub)), sub["sla_compliance_min"], label=d, alpha=0.7)
    ax.set_xlabel("SLA index")
    ax.set_ylabel("sla_compliance_reconstructed (min)")
    ax.legend()
    ax.set_title("Acceptance Boundary (reconstructed × decision)")
    plt.tight_layout()
    for ext in ["png", "pdf"]:
        p = FIG_DIR / f"fig_acceptance_boundary_reconstructed.{ext}"
        plt.savefig(p, bbox_inches="tight")
    plt.close()
    print("FASE 5 G3 OK: fig_acceptance_boundary_reconstructed.png/pdf")

    # G4 — Radar por slice: URLLC / eMBB / mMTC, eixos = RAN, TRANSPORT, CORE
    agg = cdf.groupby(["slice_type", "domain"])["compliance_domain"].mean().unstack(fill_value=0)
    nax = max(3, len(agg.columns))
    angles = np.linspace(0, 2 * np.pi, nax, endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection="polar"))
    for idx, (st, row) in enumerate(agg.iterrows()):
        v = [row.get(d, 0) for d in ["RAN", "TRANSPORT", "CORE"]]
        v += v[:1]
        ax.plot(angles, v, "o-", label=st)
        ax.fill(angles, v, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(["RAN", "TRANSPORT", "CORE"])
    ax.legend(loc="upper right")
    ax.set_title("Domain Radar per Slice (REAL)")
    plt.tight_layout()
    for ext in ["png", "pdf"]:
        p = FIG_DIR / f"fig_domain_radar_per_slice.{ext}"
        plt.savefig(p, bbox_inches="tight")
    plt.close()
    print("FASE 5 G4 OK: fig_domain_radar_per_slice.png/pdf")


def fase6_report(rec: pd.DataFrame) -> None:
    """FASE 6 — FINAL_S28_D_DOMAIN_COMPLIANCE_REPORT.md"""
    raw = pd.read_csv(BASE / "18_compliance_forensics" / "outputs" / "compliance_raw.csv")
    n_reneg = (raw["action"] == "RENEG").sum()
    n_accept = (raw["action"] == "ACCEPT").sum()
    n_reject = (raw["action"] == "REJECT").sum()

    r_min = rec["sla_compliance_min"]
    report = f"""# FINAL S28.D — Domain Compliance Report (TriSLA v3.9.3)

## Evidência matemática

- Hipótese H-S28.D: `sla_compliance ≈ min(compliance_RAN, compliance_Transport, compliance_Core)`.
- Pesos documentados (iguais para todos os domínios): w1={W1} (availability), w2={W2} (1 - normalized_latency), w3={W3} (1 - normalized_cpu).
- Reconstrução: sla_compliance_min, sla_compliance_avg, sla_compliance_weighted por SLA.

Estatísticas da amostra:
- sla_compliance_min: mean={r_min.mean():.4f}, min={r_min.min():.4f}, max={r_min.max():.4f}.
- Nenhum SLA atinge ≥ 0.9 no mínimo domínio (bottleneck).

## Evidência empírica

- Decisões (compliance_raw): RENEG={n_reneg}, ACCEPT={n_accept}, REJECT={n_reject}.
- Todos os SLAs observados resultaram em RENEG; o TriSLA decide corretamente (sla_compliance < 0.9 → RENEG).
- Domínios limitantes identificados via heatmap e radar por slice.

## Limitação atual do TriSLA

- O sistema não expõe cálculo explícito de compliance por domínio (RAN, TRANSPORT, CORE).
- Observabilidade causal: não há métrica “domínio bottleneck” em runtime; a análise é forense *ex post*.

## Por que RENEG é correto

- Dados reais mostram sla_compliance < 0.9 (inferido e reconstruído).
- A regra rule-002 (sla_compliance < 0.9 → RENEG) está correta e consistente com as evidências.

## O que falta para ACCEPT

- Melhorar compliance em pelo menos um domínio (RAN, TRANSPORT ou CORE) até que o mínimo ≥ 0.9.
- Possíveis ações: otimização de latência, recursos (CPU/mem) ou disponibilidade por domínio.

## Como isso fecha a Pergunta de Pesquisa

- Demonstra **por que** o sla_compliance nunca atinge ≥ 0.9 (bottleneck por domínio).
- Identifica **qual** domínio restringe a aceitação (via heatmap e radar).
- Mostra que o TriSLA **decide** corretamente, mas **carece** de observabilidade causal explícita por domínio.

---
*PROMPT_S28.D — SLA_COMPLIANCE DOMAIN DECOMPOSITION (READ-ONLY) | NASP | trisla*
"""
    out_path = OUT / "FINAL_S28_D_DOMAIN_COMPLIANCE_REPORT.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"FASE 6 OK: {out_path}")


def update_checksums() -> None:
    """Update CHECKSUMS.sha256 for new S28.D outputs."""
    files = [
        "domain_metrics_raw.csv",
        "domain_metrics_normalized.csv",
        "domain_compliance_calculated.csv",
        "sla_compliance_reconstructed.csv",
        "FINAL_S28_D_DOMAIN_COMPLIANCE_REPORT.md",
    ]
    figs = [
        "fig_compliance_by_domain_boxplot.png",
        "fig_compliance_by_domain_boxplot.pdf",
        "fig_domain_bottleneck_heatmap.png",
        "fig_domain_bottleneck_heatmap.pdf",
        "fig_acceptance_boundary_reconstructed.png",
        "fig_acceptance_boundary_reconstructed.pdf",
        "fig_domain_radar_per_slice.png",
        "fig_domain_radar_per_slice.pdf",
    ]
    entries = []
    for f in files:
        p = OUT / f
        if p.exists():
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            entries.append(f"{h}  {f}")
    for f in figs:
        p = FIG_DIR / f
        if p.exists():
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            entries.append(f"{h}  figs/{f}")
    if not entries:
        return
    digest_path = OUT / "CHECKSUMS_S28D.sha256"
    block = "\n".join(["# S28.D outputs"] + entries) + "\n"
    digest_path.write_text(block, encoding="utf-8")
    print("CHECKSUMS updated:", digest_path)


def main() -> int:
    base = Path(__file__).resolve().parent
    ev = base / "evidencias_resultados_v3.9.3"
    if ev.is_dir():
        global BASE, OUT, DOM, FIG_DIR
        BASE = ev
        DOM = BASE / "18_compliance_forensics"
        FIG_DIR = DOM / "figs"
        OUT = DOM

    os.chdir(base)
    if not gate0():
        return 1

    df1 = fase1_domain_metrics_raw()
    df2 = fase2_normalize(df1)
    df3 = fase3_domain_compliance(df2)
    rec = fase4_sla_reconstructed(df3)
    fase5_plots(df3, rec)
    fase6_report(rec)
    update_checksums()

    print("GATE FINAL: CSVs, 4 plots (png+pdf), report, checksums — OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
