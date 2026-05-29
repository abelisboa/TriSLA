import Link from "next/link";
import type { SubmitResponse } from "../../lib/submitResponse";
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
          Executive view — all fields from live submit response (REAL_PAYLOAD_FREEZE contract).
        </p>
      </header>

      <div className="trisla-admission-top-grid">
        <AdmissionOverviewPanel response={response} />
        <ServiceProfilePanel response={response} />
      </div>

      <TelemetrySnapshotPanel response={response} heading="3. Multidomain Telemetry" />
      <OperationalExplanationPanel response={response} heading="4. Operational Explanation" />
      <GovernancePanel response={response} heading="5. Governance" />
      <RuntimeSupervisionSection response={response} heading="6. Runtime Supervision" />
      <RawPayloadPanel response={response} heading="7. Raw Payload" />

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
