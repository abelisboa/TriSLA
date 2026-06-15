"use client";

import type { ReactNode } from "react";
import {
  formatMetricValue,
  hasDomainExplainability,
  metricDisplayName,
  parseDomainExplainability,
  statusClass,
  unitForMetric,
  type DomainMetricExplainability,
} from "../../lib/domainExplainability";
import {
  COMPLIANCE_STATUS_HELP,
  FIELD_TOOLTIPS,
  REQUIRED_COMPLIANCE_BAND_PERCENT,
  STATUS_TOOLTIPS,
  UX_LABELS,
  complianceStatusDisplay,
} from "../../lib/domainExplainabilityUx";
import { formatCompliancePercent } from "../../lib/runtimeAssuranceExplainability";
import type { RuntimeAssurancePayload } from "../../lib/runtimeAssurance";
import { ComplianceSplitPanel } from "../consistency/ComplianceSplitPanel";

type Props = {
  assurance?: RuntimeAssurancePayload;
  admissionCompliancePercent?: number;
  heading?: string;
};

function FieldRow({
  label,
  tooltip,
  children,
}: {
  label: string;
  tooltip?: string;
  children: ReactNode;
}) {
  return (
    <div className="trisla-status-row">
      <dt>
        <span className="trisla-field-label" title={tooltip}>
          {label}
        </span>
        {tooltip ? (
          <span className="trisla-field-info" title={tooltip} aria-hidden="true">
            ⓘ
          </span>
        ) : null}
      </dt>
      <dd>{children}</dd>
    </div>
  );
}

function formatComplianceScore(score: number | null | undefined): string {
  if (score === null || score === undefined) return "Not available";
  return formatCompliancePercent(score);
}

function ComplianceKpiCard({ row }: { row: DomainMetricExplainability }) {
  const name = metricDisplayName(row.metric, row);
  const status = row.status ?? "Unknown";
  const statusTip = STATUS_TOOLTIPS[status] ?? "";
  const unit = unitForMetric(row.metric);

  return (
    <article className="trisla-domain-metric-card trisla-compliance-kpi-card">
      <h5>{name}</h5>
      <dl>
        <FieldRow label="Observed Value" tooltip={FIELD_TOOLTIPS.observed}>
          {formatMetricValue(row.observed, row.metric)}
        </FieldRow>
        <FieldRow label="Requirement" tooltip={FIELD_TOOLTIPS.referenceThreshold}>
          {formatMetricValue(row.threshold, row.metric)}
        </FieldRow>
        <FieldRow label="Compliance Score" tooltip={FIELD_TOOLTIPS.complianceScore}>
          {formatComplianceScore(row.compliance_score)}
        </FieldRow>
        <FieldRow label="Compliance Status" tooltip={FIELD_TOOLTIPS.complianceStatus}>
          <span className={statusClass(row.status)} title={statusTip}>
            {complianceStatusDisplay(status)}
          </span>
        </FieldRow>
        <FieldRow label="Source">
          {row.source ?? "Not available"}
        </FieldRow>
        <FieldRow label="Unit">{unit || "Not available"}</FieldRow>
      </dl>
    </article>
  );
}

function DomainComplianceBlock({
  title,
  score,
  metrics,
}: {
  title: string;
  score?: number;
  metrics?: DomainMetricExplainability[];
}) {
  if (!metrics || metrics.length === 0) return null;
  return (
    <section className="trisla-domain-explain-block">
      <h4>
        {title}
        {score !== undefined && score !== null ? (
          <span className="trisla-domain-score" title="Domain aggregate score">
            {" "}
            — Domain aggregate: {formatCompliancePercent(score)}
          </span>
        ) : null}
      </h4>
      <div className="trisla-domain-metrics-grid">
        {metrics.map((row) => (
          <ComplianceKpiCard key={`${title}-${row.metric}`} row={row} />
        ))}
      </div>
    </section>
  );
}

/**
 * RC-P20-03 — compliance evaluation only (SLA-Agent domain_explainability payload).
 * Does not render raw telemetry snapshot fields.
 */
export function ComplianceEvaluationPanel({
  assurance,
  admissionCompliancePercent,
  heading = "Compliance Evaluation",
}: Props) {
  const domainExplainability = parseDomainExplainability(assurance?.domain_explainability);
  const scores = assurance?.domain_compliance;
  const hasKpis = hasDomainExplainability(domainExplainability);
  const hasAggregate =
    assurance?.admission_compliance != null ||
    assurance?.runtime_compliance != null ||
    assurance?.sla_compliance != null ||
    admissionCompliancePercent != null;

  if (!hasKpis && !hasAggregate) {
    return (
      <section className="trisla-status-card trisla-compliance-evaluation" aria-label={heading}>
        <h2>{heading}</h2>
        <p className="trisla-muted">Compliance evaluation not available for this intent.</p>
      </section>
    );
  }

  return (
    <section className="trisla-status-card trisla-compliance-evaluation" aria-label={heading}>
      <h2>{heading}</h2>
      <p className="trisla-muted">
        Runtime compliance scores from SLA-Agent evaluation. Observed values here are evaluation-time
        inputs — see Multidomain Telemetry for raw snapshot metrics.
      </p>

      {hasAggregate ? (
        <ComplianceSplitPanel
          assurance={assurance}
          admissionCompliancePercent={admissionCompliancePercent}
        />
      ) : null}

      {hasKpis ? (
        <>
          <details className="trisla-compliance-help" open>
            <summary>{COMPLIANCE_STATUS_HELP.title}</summary>
            <p className="trisla-muted">{COMPLIANCE_STATUS_HELP.intro}</p>
            <ul className="trisla-explain-list">
              {COMPLIANCE_STATUS_HELP.rules.map((rule) => (
                <li key={rule}>{rule}</li>
              ))}
            </ul>
          </details>

          <DomainComplianceBlock
            title="RAN"
            score={scores?.ran}
            metrics={domainExplainability?.ran}
          />
          <DomainComplianceBlock
            title="TRANSPORT"
            score={scores?.transport}
            metrics={domainExplainability?.transport}
          />
          <DomainComplianceBlock
            title="CORE"
            score={scores?.core}
            metrics={domainExplainability?.core}
          />
          <p className="trisla-muted">
            Required compliance band for metric PASS: {REQUIRED_COMPLIANCE_BAND_PERCENT}%
          </p>
        </>
      ) : null}
    </section>
  );
}
