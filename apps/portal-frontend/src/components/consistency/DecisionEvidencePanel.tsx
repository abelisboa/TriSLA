import {
  type DecisionEvidenceRow,
  formatDelta,
} from "../../lib/phaseNextConsistency";

type Props = {
  evidence: DecisionEvidenceRow[];
  heading?: string;
  compact?: boolean;
};

export function DecisionEvidencePanel({
  evidence,
  heading = "Decision Evidence",
  compact = false,
}: Props) {
  if (evidence.length === 0) {
    return (
      <section className="trisla-consistency-panel" aria-label={heading}>
        <h3 className="trisla-consistency-title">{heading}</h3>
        <p className="trisla-muted">No quantitative decision evidence returned by the backend.</p>
      </section>
    );
  }

  return (
    <section className="trisla-consistency-panel" aria-label={heading}>
      <h3 className="trisla-consistency-title">{heading}</h3>
      {!compact ? (
        <p className="trisla-muted">
          Admission decision rules only — observed, threshold, delta, and rule from Decision Engine.
          Runtime compliance scores are under Compliance Evaluation.
        </p>
      ) : null}
      {compact ? (
        evidence.map((row, idx) => (
          <article key={`card-${idx}`} className="trisla-why-card" style={{ marginTop: "0.75rem" }}>
            <p className="trisla-why-metric">
              <span>Observed:</span> {row.observed}
              {row.unit ? ` ${row.unit}` : ""}
            </p>
            <p className="trisla-why-metric">
              <span>Threshold:</span> {row.threshold}
              {row.unit ? ` ${row.unit}` : ""}
            </p>
            <p className="trisla-why-metric">
              <span>Delta:</span> {formatDelta(row.delta ?? null)}
            </p>
            <p className="trisla-why-metric">
              <span>Rule:</span> {row.rule ?? "—"}
            </p>
          </article>
        ))
      ) : (
        <div className="trisla-table-wrap">
          <table className="trisla-simple-table trisla-evidence-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Observed</th>
                <th>Threshold</th>
                <th>Delta</th>
                <th>Rule</th>
              </tr>
            </thead>
            <tbody>
              {evidence.map((row, idx) => (
                <tr key={`${row.metric ?? "m"}-${row.rule ?? ""}-${idx}`}>
                  <td>{row.metric ?? "—"}</td>
                  <td>
                    {row.observed}
                    {row.unit ? ` ${row.unit}` : ""}
                  </td>
                  <td>
                    {row.threshold}
                    {row.unit ? ` ${row.unit}` : ""}
                  </td>
                  <td>{formatDelta(row.delta ?? null)}</td>
                  <td>
                    <code className="trisla-inline-code">{row.rule ?? "—"}</code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
