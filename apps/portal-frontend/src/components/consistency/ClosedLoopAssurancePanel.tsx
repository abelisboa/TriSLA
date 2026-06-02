import {
  closedLoopFromAssurance,
  detectedLabel,
  remediationAttemptsFromAssurance,
} from "../../lib/phaseNextConsistency";
import type { RuntimeAssurancePayload } from "../../lib/runtimeAssurance";

type Props = {
  assurance?: RuntimeAssurancePayload;
};

const FLOW = ["Observe", "Detect", "Evaluate", "Act", "Revalidate"] as const;

export function ClosedLoopAssurancePanel({ assurance }: Props) {
  const loop = closedLoopFromAssurance(assurance);
  const attempts = remediationAttemptsFromAssurance(assurance);
  const latest = attempts[0];

  if (!loop && attempts.length === 0) {
    return (
      <section className="trisla-consistency-panel" aria-label="Closed Loop Assurance">
        <h3 className="trisla-consistency-title">Closed Loop Assurance</h3>
        <p className="trisla-muted">Closed-loop fields not available.</p>
      </section>
    );
  }

  return (
    <section className="trisla-consistency-panel" aria-label="Closed Loop Assurance">
      <h3 className="trisla-consistency-title">Closed Loop Assurance</h3>
      <ol className="trisla-closed-loop-flow" aria-label="Closed loop flow">
        {FLOW.map((step, i) => {
          const key = step.toLowerCase() as keyof typeof loop;
          const active = loop?.[key] === true;
          return (
            <li key={step} className={active ? "trisla-cl-step-active" : "trisla-cl-step"}>
              {step}
              {i < FLOW.length - 1 ? <span className="trisla-cl-arrow" aria-hidden>↓</span> : null}
            </li>
          );
        })}
      </ol>
      {loop?.mode ? (
        <p className="trisla-muted">
          Mode: <strong>{loop.mode}</strong>
        </p>
      ) : null}

      {latest ? (
        <dl className="trisla-closed-loop-details">
          <div className="trisla-status-row">
            <dt>Detected</dt>
            <dd>{detectedLabel(latest.detected)}</dd>
          </div>
          <div className="trisla-status-row">
            <dt>Action</dt>
            <dd>
              <code className="trisla-inline-code">{latest.action ?? "—"}</code>
            </dd>
          </div>
          <div className="trisla-status-row">
            <dt>Mode</dt>
            <dd>{latest.simulation === true ? "simulation" : "live"}</dd>
          </div>
          <div className="trisla-status-row">
            <dt>Result</dt>
            <dd>{latest.result ?? "—"}</dd>
          </div>
          <div className="trisla-status-row">
            <dt>Revalidation</dt>
            <dd>
              {loop?.revalidate
                ? `completed${
                    latest.revalidation_delta_compliance != null
                      ? ` (Δ compliance ${latest.revalidation_delta_compliance}%)`
                      : ""
                  }`
                : "not run"}
            </dd>
          </div>
        </dl>
      ) : (
        <p className="trisla-muted">No remediation attempt in this evaluation cycle.</p>
      )}
    </section>
  );
}
