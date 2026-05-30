import Link from "next/link";
import type { SubmitResponse } from "../../lib/submitResponse";
import { DashboardSection } from "../workflow/DashboardSection";
import { DashboardSectionNav } from "../workflow/DashboardSectionNav";
import { GovernancePanel } from "../submit-payload/GovernancePanel";
import { OperationalExplanationPanel } from "../submit-payload/OperationalExplanationPanel";
import { RawPayloadPanel } from "../submit-payload/RawPayloadPanel";
import { TelemetrySnapshotPanel } from "../submit-payload/TelemetrySnapshotPanel";
import { RuntimeSupervisionSection } from "../runtime-supervision/RuntimeSupervisionSection";
import { AdmissionOverviewPanel } from "./AdmissionOverviewPanel";
import { ServiceProfilePanel } from "./ServiceProfilePanel";

type Props = { response: SubmitResponse };

export function AdmissionDashboard({ response }: Props) {
  return (
    <div className="trisla-admission-dashboard">
      <header className="trisla-admission-dashboard-header">
        <h2 className="trisla-admission-dashboard-title">Admission Dashboard</h2>
        <p className="trisla-muted">
          Operational view — decision, telemetry, explanation, governance, and runtime supervision
          from the live SLA submission.
        </p>
      </header>

      <DashboardSectionNav />

      <div className="trisla-admission-top-grid">
        <DashboardSection id="section-decision" level={1}>
          <AdmissionOverviewPanel response={response} />
        </DashboardSection>
        <DashboardSection id="section-service-profile" level={2}>
          <ServiceProfilePanel response={response} />
        </DashboardSection>
      </div>

      <DashboardSection id="section-telemetry" level={3}>
        <TelemetrySnapshotPanel response={response} heading="3. Multidomain Telemetry" />
      </DashboardSection>
      <DashboardSection id="section-operational" level={4}>
        <OperationalExplanationPanel response={response} heading="4. Operational Explanation" />
      </DashboardSection>
      <DashboardSection id="section-governance" level={5}>
        <GovernancePanel response={response} heading="5. Governance" />
      </DashboardSection>
      <DashboardSection id="section-runtime" level={6}>
        <RuntimeSupervisionSection response={response} heading="6. Runtime Supervision" />
      </DashboardSection>
      <DashboardSection id="section-raw-payload" level={7}>
        <RawPayloadPanel response={response} heading="7. Technical Details" />
      </DashboardSection>

      <section className="trisla-status-card" aria-label="Next steps">
        <h2>Next steps</h2>
        <p className="trisla-muted">View runtime orchestration and observability after admission.</p>
        <div className="trisla-cta-row">
          <Link href="/sla-lifecycle" className="trisla-cta-button">
            View Runtime
          </Link>
          <Link href="/monitoring" className="trisla-cta-button">
            View Monitoring
          </Link>
        </div>
      </section>
    </div>
  );
}
