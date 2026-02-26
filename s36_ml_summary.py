import pandas as pd
import os
base = "evidencias_release_v3.9.11/s36"
os.makedirs(f"{base}/14_tables", exist_ok=True)
df = pd.read_csv(f"{base}/06_ml_predictions/ml_predictions_raw.csv")
summary = df.groupby(["decision", "slice_type"]).agg(
    n=("sla_id", "count"),
    risk_mean=("risk_score", "mean"),
    risk_std=("risk_score", "std"),
    conf_mean=("confidence", "mean"),
    rmc_mean=("real_metrics_count", "mean"),
).reset_index()
summary.to_csv(f"{base}/14_tables/ml_summary_by_decision_slice.csv", index=False)
print(summary.head(20))
