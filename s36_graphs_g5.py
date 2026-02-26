import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

base = "evidencias_release_v3.9.11/s36"
path = f"{base}/13_latency/latency_attempt.csv"
figdir = f"{base}/15_graphs/figs"
if os.path.exists(path):
    df = pd.read_csv(path)
    if len(df) > 0:
        x = sorted(df["delta_ms"].dropna().values)
        y = [(i + 1) / len(x) for i in range(len(x))]
        plt.figure()
        plt.plot(x, y)
        plt.tight_layout()
        plt.savefig(f"{figdir}/fig_latency_cdf.png", dpi=200)
        plt.savefig(f"{figdir}/fig_latency_cdf.pdf")
        plt.close()
        print("Latency CDF generated.")
    else:
        print("No latency rows; skipping.")
else:
    print("Latency file missing; skipping.")
