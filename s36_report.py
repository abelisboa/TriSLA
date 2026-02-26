import pandas as pd
import os
import glob

base = "evidencias_release_v3.9.11/s36"
rep = f"{base}/16_integrity/S36_FINAL_REPORT.md"
os.makedirs(os.path.dirname(rep), exist_ok=True)

reg = pd.read_csv(f"{base}/01_sla_submissions/sla_registry.csv")
ml = pd.read_csv(f"{base}/06_ml_predictions/ml_predictions_raw.csv")
ml["risk_score"] = pd.to_numeric(ml["risk_score"], errors="coerce")
ml["real_metrics_count"] = pd.to_numeric(ml["real_metrics_count"], errors="coerce")

kraw = f"{base}/08_kafka/events_raw.log"
kcount = sum(1 for _ in open(kraw, errors="ignore")) if os.path.exists(kraw) else 0
kv = pd.read_csv(f"{base}/08_kafka/events_validation.csv") if os.path.exists(f"{base}/08_kafka/events_validation.csv") else None

figs = sorted(glob.glob(f"{base}/15_graphs/figs/*.png"))

lat = f"{base}/13_latency/latency_attempt.csv"
lat_ok = False
if os.path.exists(lat):
    try:
        lat_df = pd.read_csv(lat)
        lat_ok = len(lat_df) > 0
    except Exception:
        pass

with open(rep, "w") as f:
    f.write("# S36 FINAL REPORT — TriSLA v3.9.11 (READ-ONLY)\n\n")
    f.write("## Volume de SLAs\n")
    f.write(reg.groupby(["scenario", "slice_type"]).size().to_string() + "\n\n")
    f.write("## ML-NSMF\n")
    r = ml["risk_score"]
    rmc = ml["real_metrics_count"]
    f.write(f"- risk_score min/avg/max: {r.min():.6f} / {r.mean():.6f} / {r.max():.6f}\n")
    f.write(f"- real_metrics_count avg: {rmc.mean():.3f}\n\n")
    f.write("## Kafka (trisla-decision-events)\n")
    f.write(f"- linhas consumidas (raw): {kcount}\n")
    if kv is not None:
        f.write(kv.groupby("valid").size().to_string() + "\n\n")
    f.write("## Latência\n")
    f.write("- disponível: " + ("SIM" if lat_ok else "NÃO (sem timestamps correlacionáveis nos logs)") + "\n\n")
    f.write("## Figuras geradas (PNG)\n")
    for p in figs:
        f.write(f"- {os.path.basename(p)}\n")

print("Report:", rep)
