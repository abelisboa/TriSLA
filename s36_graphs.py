import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

base = "evidencias_release_v3.9.11/s36"
figdir = f"{base}/15_graphs/figs"
os.makedirs(figdir, exist_ok=True)

ml = pd.read_csv(f"{base}/06_ml_predictions/ml_predictions_raw.csv")

# G1
dec = ml.groupby(["decision", "slice_type"]).size().reset_index(name="n")
pivot = dec.pivot(index="slice_type", columns="decision", values="n").fillna(0)
ax = pivot.plot(kind="bar")
plt.tight_layout()
plt.savefig(f"{figdir}/fig_decisions_by_slice.png", dpi=200)
plt.savefig(f"{figdir}/fig_decisions_by_slice.pdf")
plt.close()

# G2
ml["risk_score"] = pd.to_numeric(ml["risk_score"], errors="coerce")
plt.figure()
plt.hist(ml["risk_score"].dropna(), bins=20)
plt.tight_layout()
plt.savefig(f"{figdir}/fig_risk_hist.png", dpi=200)
plt.savefig(f"{figdir}/fig_risk_hist.pdf")
plt.close()

# G3
plt.figure()
data = []
labels = []
for s in sorted(ml["slice_type"].dropna().unique()):
    vals = ml.loc[ml["slice_type"] == s, "risk_score"].dropna().values
    if len(vals) > 0:
        data.append(vals)
        labels.append(s)
if data:
    plt.boxplot(data, labels=labels)
plt.tight_layout()
plt.savefig(f"{figdir}/fig_risk_boxplot_by_slice.png", dpi=200)
plt.savefig(f"{figdir}/fig_risk_boxplot_by_slice.pdf")
plt.close()

# G4
kv = pd.read_csv(f"{base}/14_tables/kafka_validation_summary.csv")
plt.figure()
if len(kv) > 0:
    plt.bar(kv["valid"].astype(str), kv["n"])
plt.tight_layout()
plt.savefig(f"{figdir}/fig_kafka_valid_invalid.png", dpi=200)
plt.savefig(f"{figdir}/fig_kafka_valid_invalid.pdf")
plt.close()

print("OK figures generated in:", figdir)
