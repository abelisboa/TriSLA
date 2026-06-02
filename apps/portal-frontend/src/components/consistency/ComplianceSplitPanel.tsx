import { formatComplianceDisplay } from "../../lib/phaseNextConsistency";
import type { RuntimeAssurancePayload } from "../../lib/runtimeAssurance";

type Props = {
  assurance?: RuntimeAssurancePayload;
  admissionCompliancePercent?: number;
};

export function ComplianceSplitPanel({ assurance, admissionCompliancePercent }: Props) {
  const admission =
    assurance?.admission_compliance_percent ?? admissionCompliancePercent ?? assurance?.admission_compliance;
  const runtime =
    assurance?.runtime_compliance_percent ?? assurance?.runtime_compliance ?? assurance?.sla_compliance;

  return (
    <section className="trisla-consistency-panel" aria-label="Compliance">
      <h3 className="trisla-consistency-title">Compliance</h3>
      <div className="trisla-compliance-split" role="list">
        <article className="trisla-summary-card" role="listitem">
          <span className="trisla-summary-label">Admission Compliance</span>
          <span className="trisla-summary-value">
            {formatComplianceDisplay(
              typeof admission === "number" ? admission : undefined,
              { alreadyPercent: assurance?.admission_compliance_percent != null },
            )}
          </span>
          <span className="trisla-muted trisla-summary-source">Origin: Decision Engine</span>
        </article>
        <article className="trisla-summary-card" role="listitem">
          <span className="trisla-summary-label">Runtime Compliance</span>
          <span className="trisla-summary-value">
            {formatComplianceDisplay(
              typeof runtime === "number" ? runtime : undefined,
              { alreadyPercent: assurance?.runtime_compliance_percent != null },
            )}
          </span>
          <span className="trisla-muted trisla-summary-source">Origin: Runtime Assurance</span>
        </article>
      </div>
    </section>
  );
}
