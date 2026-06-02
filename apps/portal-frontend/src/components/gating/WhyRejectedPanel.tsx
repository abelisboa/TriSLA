import type { DecisionEvidenceRow } from "../../lib/phaseNextConsistency";
import { formatDelta } from "../../lib/phaseNextConsistency";
import { DecisionEvidencePanel } from "../consistency/DecisionEvidencePanel";

type Props = {
  decision: string;
  evidence: DecisionEvidenceRow[];
  reasoning?: string | null;
};

export function WhyRejectedPanel({ decision, evidence, reasoning }: Props) {
  return (
    <section className="trisla-consistency-panel" aria-label="Why Rejected">
      <h3 className="trisla-consistency-title">Why Rejected?</h3>
      <p className="trisla-muted">
        Admission-time decision only (T₀). No runtime telemetry is shown for rejected SLAs.
      </p>
      <dl>
        <div className="trisla-status-row">
          <dt>Decision</dt>
          <dd>{decision}</dd>
        </div>
      </dl>
      <DecisionEvidencePanel evidence={evidence} heading="Decision Evidence" />
      {evidence.length > 0 ? (
        <article className="trisla-why-card">
          {evidence.map((row, idx) => (
            <div key={`why-${idx}`}>
              {row.metric ? (
                <p className="trisla-why-metric">
                  <span>Observed {row.metric}:</span> {row.observed}
                  {row.unit ? ` ${row.unit}` : ""}
                </p>
              ) : null}
              {row.threshold !== undefined ? (
                <p className="trisla-why-metric">
                  <span>Threshold:</span> {row.threshold}
                  {row.unit ? ` ${row.unit}` : ""}
                </p>
              ) : null}
              {row.delta !== undefined && row.delta !== null ? (
                <p className="trisla-why-metric">
                  <span>Delta:</span> {formatDelta(row.delta)}
                </p>
              ) : null}
              {row.rule ? (
                <p className="trisla-why-metric">
                  <span>Rule:</span> {row.rule}
                </p>
              ) : null}
            </div>
          ))}
          <p className="trisla-muted" style={{ marginTop: "0.5rem" }}>
            Reason: Admission conditions exceeded the configured threshold.
          </p>
        </article>
      ) : reasoning ? (
        <p className="trisla-muted">{reasoning}</p>
      ) : null}
    </section>
  );
}
