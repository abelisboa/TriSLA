"""FASE 5: Boxplot by slice, CDF submit_to_kafka (or submit_to_decision), violin by scenario, timeline."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

base = "evidencias_release_v3.9.11/s36_1_control_latency"
raw = f"{base}/05_latency_tables/control_latency_raw.csv"
figdir = f"{base}/06_graphs"
os.makedirs(figdir, exist_ok=True)
df = pd.read_csv(raw)

# use submit_to_kafka_ms or submit_to_decision_ms
df["latency_ms"] = pd.to_numeric(df["submit_to_kafka_ms"].fillna(df["submit_to_decision_ms"]), errors="coerce")
df = df.dropna(subset=["latency_ms"])

# Boxplot by slice
plt.figure()
data = [df.loc[df["slice_type"] == s, "latency_ms"].values for s in df["slice_type"].unique()]
labels = list(df["slice_type"].unique())
if data and all(len(x) > 0 for x in data):
    plt.boxplot(data, labels=labels)
plt.ylabel("Control latency (ms)")
plt.xlabel("Slice type")
plt.tight_layout()
plt.savefig(f"{figdir}/fig_control_latency_boxplot.png", dpi=200)
plt.savefig(f"{figdir}/fig_control_latency_boxplot.pdf")
plt.close()

# CDF
plt.figure()
x = sorted(df["latency_ms"].values)
y = [(i + 1) / len(x) for i in range(len(x))]
plt.plot(x, y)
plt.xlabel("Control latency (ms)")
plt.ylabel("CDF")
plt.tight_layout()
plt.savefig(f"{figdir}/fig_control_latency_cdf.png", dpi=200)
plt.savefig(f"{figdir}/fig_control_latency_cdf.pdf")
plt.close()

# Violin by scenario
plt.figure()
import numpy as np
scenarios = df["scenario"].unique()
parts = []
for s in scenarios:
    v = df.loc[df["scenario"] == s, "latency_ms"].values
    if len(v) > 0:
        parts.append(v)
if parts:
    vp = plt.violinplot(parts, positions=range(len(parts)), showmeans=True, showmedians=True)
    plt.xticks(range(len(parts)), list(scenarios))
plt.ylabel("Control latency (ms)")
plt.xlabel("Scenario")
plt.tight_layout()
plt.savefig(f"{figdir}/fig_control_latency_violin.png", dpi=200)
plt.savefig(f"{figdir}/fig_control_latency_violin.pdf")
plt.close()

# Timeline: decision_timestamp per SLA (Kafka events not available; use decision_ts)
plt.figure()
df2 = pd.read_csv(raw)
df2["ts"] = pd.to_datetime(df2["decision_timestamp"], utc=True, errors="coerce")
df2 = df2.dropna(subset=["ts"]).sort_values("ts")
if len(df2) > 0:
    y = range(len(df2))
    plt.scatter(df2["ts"], y, s=80)
    plt.yticks(y, [str(r).split("-")[-1][:8] for r in df2["sla_id"]])
    plt.xlabel("Decision timestamp (UTC)")
    plt.ylabel("SLA (sla_id suffix)")
    plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig(f"{figdir}/fig_control_latency_timeline.png", dpi=200)
plt.savefig(f"{figdir}/fig_control_latency_timeline.pdf")
plt.close()

print("OK figures in", figdir)
