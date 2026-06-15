"use client";

import {
  assuranceStateClass,
  assuranceStateLabel,
  type RuntimeAssurancePayload,
} from "../../lib/runtimeAssurance";
import {
  ACTIVE_VS_WARNING_SUMMARY,
  assuranceExplanationForState,
  LIFECYCLE_ACTIVE_EXPLANATION,
} from "../../lib/runtimeAssuranceStateModel";
import { formatLifecycleStateLabel } from "../../lib/operatorLabels";
import {
  governanceClarityFromAssurance,
  operationalStatusFromAssurance,
  telemetryFidelityFromAssurance,
} from "../../lib/phaseNextConsistency";
import { ClosedLoopAssurancePanel } from "../consistency/ClosedLoopAssurancePanel";
import type { OnChainEvidenceFields } from "../../lib/blockchainEvidenceDisplay";
import { GovernanceClarityPanel } from "../consistency/GovernanceClarityPanel";
import { TelemetryFidelityPanel } from "../consistency/TelemetryFidelityPanel";

export type RuntimeAssuranceTraceContext = {
  intent_id?: string;
  nest_id?: string | null;
  trace_id?: string;
  governance_event_id?: string;
};

type Props = {
  assurance?: RuntimeAssurancePayload;
  /** Deprecated — use operational_status from assurance only. */
  lifecycleStatus?: string;
  traceContext?: RuntimeAssuranceTraceContext;
  onChainEvidence?: OnChainEvidenceFields;
};

function ListOrMuted({ items, emptyLabel }: { items: string[]; emptyLabel: string }) {
  if (items.length === 0) {
    return <span className="trisla-muted">{emptyLabel}</span>;
  }
  return (
    <ul className="trisla-explain-list">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

/**
 * RC-P20-03 — closed-loop assurance state only.
 * Compliance scores and per-KPI evaluation live in ComplianceEvaluationPanel.
 * Raw telemetry lives in Multidomain Telemetry panels.
 */
export function RuntimeAssurancePanel({
  assurance,
  lifecycleStatus: _legacyLifecycleStatus,
  traceContext,
  onChainEvidence,
}: Props) {
  const state = assurance?.state ?? assurance?.assurance_state;
  const label = assuranceStateLabel(assurance);
  const operationalStatus = operationalStatusFromAssurance(assurance);
  const operationalLabel = operationalStatus
    ? formatLifecycleStateLabel(operationalStatus)
    : "Not available";
  const showActiveWarningNote =
    operationalStatus === "ACTIVE" && state === "WARNING";

  const violations = assurance?.violations ?? [];
  const warnings = assurance?.warnings ?? [];
  const fidelity = telemetryFidelityFromAssurance(assurance);
  const governanceClarity = governanceClarityFromAssurance(assurance);

  return (
    <section className="trisla-status-card trisla-runtime-assurance" aria-label="Runtime Assurance">
      <h2>Runtime Assurance</h2>
      <p className="trisla-muted">
        Closed-loop assurance state — observe, detect, evaluate, act (simulation), revalidate.
        Per-KPI compliance is under Compliance Evaluation; raw metrics under Multidomain Telemetry.
      </p>
      {!assurance || !state ? (
        <p className="trisla-muted">Not available</p>
      ) : (
        <>
          <dl>
            <div className="trisla-status-row">
              <dt>Operational Status</dt>
              <dd>{operationalLabel}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Current State</dt>
              <dd>
                <span className={assuranceStateClass(String(state))}>{label}</span>
              </dd>
            </div>
            <div className="trisla-status-row">
              <dt>Bottleneck domain</dt>
              <dd>{assurance.bottleneck_domain?.toUpperCase() ?? "Not available"}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Drift detected</dt>
              <dd>
                {assurance.drift_detected === true
                  ? "Yes"
                  : assurance.drift_detected === false
                    ? "No"
                    : "Not available"}
              </dd>
            </div>
            <div className="trisla-status-row">
              <dt>Violations</dt>
              <dd>
                <ListOrMuted items={violations} emptyLabel="None reported" />
              </dd>
            </div>
            <div className="trisla-status-row">
              <dt>Warnings</dt>
              <dd>
                <ListOrMuted items={warnings} emptyLabel="None reported" />
              </dd>
            </div>
            <div className="trisla-status-row">
              <dt>Recommendation</dt>
              <dd>{assurance.recommendation ?? "Not available"}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Last evaluation</dt>
              <dd>{assurance.last_evaluation ?? "Not available"}</dd>
            </div>
            {showActiveWarningNote ? (
              <div className="trisla-status-row">
                <dt>Operational note</dt>
                <dd>
                  {LIFECYCLE_ACTIVE_EXPLANATION} {assuranceExplanationForState(String(state))}
                </dd>
              </div>
            ) : assuranceExplanationForState(String(state)) ? (
              <div className="trisla-status-row">
                <dt>Operational note</dt>
                <dd>{assuranceExplanationForState(String(state))}</dd>
              </div>
            ) : null}
          </dl>

          <GovernanceClarityPanel clarity={governanceClarity} onChainEvidence={onChainEvidence} />

          <TelemetryFidelityPanel fidelity={fidelity} />

          <ClosedLoopAssurancePanel assurance={assurance} />

          {showActiveWarningNote ? (
            <p className="trisla-muted" style={{ marginTop: "0.75rem" }}>
              {ACTIVE_VS_WARNING_SUMMARY}
            </p>
          ) : null}

          {traceContext &&
          (traceContext.intent_id ||
            traceContext.nest_id ||
            traceContext.trace_id ||
            traceContext.governance_event_id) ? (
            <details className="trisla-details trisla-explain-trace" style={{ marginTop: "1rem" }}>
              <summary>Explainability traceability</summary>
              <dl>
                <div className="trisla-status-row">
                  <dt>intent_id</dt>
                  <dd>{traceContext.intent_id ?? "Not available"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>nest_id</dt>
                  <dd>{traceContext.nest_id ?? "Not available"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>trace_id</dt>
                  <dd>{traceContext.trace_id ?? "Not available"}</dd>
                </div>
                <div className="trisla-status-row">
                  <dt>governance_event_id</dt>
                  <dd>{traceContext.governance_event_id ?? "Not available"}</dd>
                </div>
              </dl>
            </details>
          ) : null}
        </>
      )}
    </section>
  );
}
