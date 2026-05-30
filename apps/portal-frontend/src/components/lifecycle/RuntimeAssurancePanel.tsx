"use client";

import { assuranceStateClass, assuranceStateLabel, type RuntimeAssurancePayload } from "../../lib/runtimeAssurance";
import { formatValue } from "../../lib/format";

type Props = {
  assurance?: RuntimeAssurancePayload;
};

export function RuntimeAssurancePanel({ assurance }: Props) {
  const state = assurance?.state ?? assurance?.assurance_state;
  const label = assuranceStateLabel(assurance);

  return (
    <section className="trisla-status-card trisla-runtime-assurance" aria-label="Runtime Assurance">
      <h2>Runtime Assurance</h2>
      <p className="trisla-muted">Closed-loop observation — detect, evaluate, recommend. No automatic remediation.</p>
      {!assurance || !state ? (
        <p className="trisla-muted">Not available</p>
      ) : (
        <dl>
          <div className="trisla-status-row">
            <dt>Current State</dt>
            <dd>
              <span className={assuranceStateClass(state)}>{label}</span>
            </dd>
          </div>
          <div className="trisla-status-row">
            <dt>Drift detected</dt>
            <dd>{assurance.drift_detected === true ? "Yes" : assurance.drift_detected === false ? "No" : "Not available"}</dd>
          </div>
          <div className="trisla-status-row">
            <dt>Recommendation</dt>
            <dd>{assurance.recommendation ?? "Not available"}</dd>
          </div>
          <div className="trisla-status-row">
            <dt>Last evaluation</dt>
            <dd>{assurance.last_evaluation ? formatValue(assurance.last_evaluation) : "Not available"}</dd>
          </div>
          {assurance.bottleneck_domain ? (
            <div className="trisla-status-row">
              <dt>Focus domain</dt>
              <dd>{formatValue(assurance.bottleneck_domain)}</dd>
            </div>
          ) : null}
        </dl>
      )}
    </section>
  );
}
