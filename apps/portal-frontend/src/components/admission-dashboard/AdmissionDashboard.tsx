import Link from "next/link";
import type { SubmitResponse } from "../../lib/submitResponse";
import { normalizeAdmissionDecision, showLifecycleSection } from "../../lib/admissionLifecycleGate";
import { DashboardSection } from "../workflow/DashboardSection";
import { DashboardSectionNav } from "../workflow/DashboardSectionNav";
import { GovernancePanel } from "../submit-payload/GovernancePanel";
import { OperationalExplanationPanel } from "../submit-payload/OperationalExplanationPanel";
import { RawPayloadPanel } from "../submit-payload/RawPayloadPanel";
import { TelemetrySnapshotPanel } from "../submit-payload/TelemetrySnapshotPanel";
import { AdmissionOverviewPanel } from "./AdmissionOverviewPanel";
import { ServiceProfilePanel } from "./ServiceProfilePanel";
import { AdmissionOnlyBanner } from "../gating/AdmissionOnlyBanner";
import { WhyRejectedPanel } from "../gating/WhyRejectedPanel";
import { RenegotiationProposalPanel } from "../gating/RenegotiationProposalPanel";
import { decisionEvidenceFromSubmit } from "../../lib/phaseNextConsistency";

type Props = { response: SubmitResponse };

export function AdmissionDashboard({ response }: Props) {
  const decision = normalizeAdmissionDecision(response.decision);
  const runtimeEnabled = decision === "ACCEPT";
  const intentId = String(response.intent_id ?? "");
  const show = (section: Parameters<typeof showLifecycleSection>[0]) =>
    showLifecycleSection(section, decision);

  return (
    <div className="trisla-admission-dashboard">
      <header className="trisla-admission-dashboard-header">
        <h2 className="trisla-admission-dashboard-title">Admission Result</h2>
        <p className="trisla-muted">
          {runtimeEnabled
            ? "Admission complete — open Admission Analysis or Runtime Lifecycle for full detail."
            : "Admission outcome — runtime supervision is not active for this decision."}
        </p>
      </header>

      {!runtimeEnabled ? <AdmissionOnlyBanner decision={decision} /> : null}

      <DashboardSectionNav decision={decision} />

      <div className="trisla-admission-top-grid">
        <DashboardSection id="section-decision" level={1}>
          <AdmissionOverviewPanel response={response} />
        </DashboardSection>
        <DashboardSection id="section-service-profile" level={2}>
          <ServiceProfilePanel response={response} />
        </DashboardSection>
      </div>

      {show("runtimeSnapshot") ? (
        <DashboardSection id="section-telemetry" level={3}>
          <TelemetrySnapshotPanel response={response} heading="3. Multidomain Telemetry" />
        </DashboardSection>
      ) : null}

      {runtimeEnabled ? (
        <DashboardSection id="section-operational" level={4}>
          <OperationalExplanationPanel response={response} heading="4. Operational Explanation" />
        </DashboardSection>
      ) : null}

      {show("whyRejected") ? (
        <DashboardSection id="section-why-rejected" level={4}>
          <WhyRejectedPanel
            decision={decision}
            evidence={decisionEvidenceFromSubmit(response)}
            reasoning={String(response.reason ?? response.justification ?? "")}
          />
        </DashboardSection>
      ) : null}

      {show("renegotiationProposal") ? (
        <DashboardSection id="section-renegotiation" level={4}>
          <RenegotiationProposalPanel submitResponse={response} />
        </DashboardSection>
      ) : null}

      {show("governance") && !runtimeEnabled ? (
        <DashboardSection id="section-governance" level={5}>
          <GovernancePanel response={response} heading="5. Governance" />
        </DashboardSection>
      ) : null}

      <DashboardSection id="section-raw-payload" level={7}>
        <RawPayloadPanel response={response} heading="7. Technical Details" />
      </DashboardSection>

      <section className="trisla-status-card" aria-label="Next steps">
        <h2>Next steps</h2>
        {show("viewRuntimeCta") && intentId ? (
          <>
            <p className="trisla-muted">
              Governance and runtime assurance are consolidated under Runtime Lifecycle.
            </p>
            <div className="trisla-cta-row">
              <Link
                href={`/sla-lifecycle?view=admission&intent_id=${encodeURIComponent(intentId)}`}
                className="trisla-cta-button"
              >
                Admission Analysis
              </Link>
              <Link
                href={`/sla-lifecycle?view=runtime&intent_id=${encodeURIComponent(intentId)}`}
                className="trisla-cta-button"
              >
                Runtime Lifecycle
              </Link>
              <Link href="/monitoring" className="trisla-cta-button">
                Domain Analytics
              </Link>
            </div>
          </>
        ) : intentId ? (
          <div className="trisla-cta-row">
            <Link
              href={`/sla-lifecycle?view=admission&intent_id=${encodeURIComponent(intentId)}`}
              className="trisla-cta-button"
            >
              Admission Analysis
            </Link>
          </div>
        ) : (
          <p className="trisla-muted">
            Runtime lifecycle is unavailable for {decision} decisions. Review admission evidence above.
          </p>
        )}
      </section>
    </div>
  );
}
