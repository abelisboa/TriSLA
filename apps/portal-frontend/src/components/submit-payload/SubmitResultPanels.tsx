import Link from "next/link";
import type { SubmitResponse } from "../../lib/submitResponse";
import { normalizeAdmissionDecision, showLifecycleSection } from "../../lib/admissionLifecycleGate";
import { AdmissionDashboard } from "../admission-dashboard/AdmissionDashboard";
import { AdmissionDecisionPanel } from "./AdmissionDecisionPanel";
import { FeasibilityPanel } from "./FeasibilityPanel";
import { GovernancePanel } from "./GovernancePanel";
import { OperationalExplanationPanel } from "./OperationalExplanationPanel";
import { RawPayloadPanel } from "./RawPayloadPanel";
import { TelemetrySnapshotPanel } from "./TelemetrySnapshotPanel";

type Props = { response: SubmitResponse };

/** F4 admission layout; F2 panel modules remain available for import. */
export function SubmitResultPanels({ response }: Props) {
  return <AdmissionDashboard response={response} />;
}

/** Legacy F2 sequential layout — preserved for non-regression. */
export function SubmitResultPanelsF2({ response }: Props) {
  const decision = normalizeAdmissionDecision(response.decision);
  const showRuntimeCta = showLifecycleSection("viewRuntimeCta", decision);
  return (
    <>
      <AdmissionDecisionPanel response={response} />
      <FeasibilityPanel response={response} />
      <OperationalExplanationPanel response={response} />
      <TelemetrySnapshotPanel response={response} />
      <GovernancePanel response={response} />
      <RawPayloadPanel response={response} />
      <section className="trisla-status-card" aria-label="Next steps">
        <h2>Next steps</h2>
        <p className="trisla-muted">
          {showRuntimeCta
            ? "View runtime orchestration and observability after admission."
            : "Admission-only view — runtime lifecycle is unavailable for this decision."}
        </p>
        <div className="trisla-cta-row">
          {showRuntimeCta ? (
            <Link href="/sla-lifecycle" className="trisla-cta-button">
              View Runtime
            </Link>
          ) : null}
          <Link href="/monitoring" className="trisla-cta-button">
            View Monitoring
          </Link>
        </div>
      </section>
    </>
  );
}
