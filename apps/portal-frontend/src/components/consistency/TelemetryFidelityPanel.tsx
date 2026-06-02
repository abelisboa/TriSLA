import {
  fidelityStatusLabel,
  type TelemetryFidelityPayload,
} from "../../lib/phaseNextConsistency";

type Props = {
  fidelity?: TelemetryFidelityPayload;
};

function formatKpiLabel(kpi: string | undefined): string {
  if (!kpi) return "Metric";
  if (kpi === "prb_utilization") return "PRB";
  return kpi.replace(/\./g, " · ");
}

export function TelemetryFidelityPanel({ fidelity }: Props) {
  if (!fidelity?.kpi_rows?.length) {
    return (
      <section className="trisla-consistency-panel" aria-label="Telemetry Consistency">
        <h3 className="trisla-consistency-title">Telemetry Consistency</h3>
        <p className="trisla-muted">telemetry_fidelity not available.</p>
      </section>
    );
  }

  const prbRow = fidelity.kpi_rows.find((r) => r.kpi === "prb_utilization");

  return (
    <section className="trisla-consistency-panel" aria-label="Telemetry Consistency">
      <h3 className="trisla-consistency-title">Telemetry Consistency</h3>
      <p className="trisla-muted">
        Compares admission-time snapshot vs current runtime snapshot (temporal evolution, not a bug).
      </p>

      <div className="trisla-fidelity-grid">
        <article className="trisla-fidelity-card">
          <h4>Admission Snapshot</h4>
          {prbRow ? (
            <p>
              <strong>PRB:</strong> {String(prbRow.admission_value ?? "—")}
              {prbRow.unit ? ` ${prbRow.unit}` : ""}
            </p>
          ) : (
            <p className="trisla-muted">No PRB row in fidelity report.</p>
          )}
        </article>
        <article className="trisla-fidelity-card">
          <h4>Runtime Snapshot</h4>
          {prbRow ? (
            <p>
              <strong>PRB:</strong> {String(prbRow.runtime_value ?? "—")}
              {prbRow.unit ? ` ${prbRow.unit}` : ""}
            </p>
          ) : (
            <p className="trisla-muted">No PRB row in fidelity report.</p>
          )}
        </article>
        <article className="trisla-fidelity-card trisla-fidelity-status">
          <h4>Status</h4>
          <p className="trisla-fidelity-badge">{fidelityStatusLabel(fidelity.consistent)}</p>
          {fidelity.mismatch_count != null && fidelity.mismatch_count > 0 ? (
            <p className="trisla-muted">{fidelity.mismatch_count} KPI mismatch(es)</p>
          ) : null}
        </article>
      </div>

      <details className="trisla-details" style={{ marginTop: "1rem" }}>
        <summary>All KPI fidelity rows</summary>
        <div className="trisla-table-wrap">
          <table className="trisla-simple-table">
            <thead>
              <tr>
                <th>KPI</th>
                <th>Admission</th>
                <th>Runtime</th>
                <th>Match</th>
              </tr>
            </thead>
            <tbody>
              {fidelity.kpi_rows.map((row) => (
                <tr key={row.kpi ?? JSON.stringify(row)}>
                  <td>{formatKpiLabel(row.kpi)}</td>
                  <td>{String(row.admission_value ?? "—")}</td>
                  <td>{String(row.runtime_value ?? "—")}</td>
                  <td>{row.consistent === true ? "Yes" : row.consistent === false ? "No" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  );
}
