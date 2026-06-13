"use client";

import type { ReactNode } from "react";
import {
  formatMetricValue,
  hasDomainExplainability,
  metricDisplayName,
  parseDomainExplainability,
  statusClass,
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

type Props = {
  assurance?: RuntimeAssurancePayload;
};

function FieldRow({
  label,
  tooltip,
  children,
}: {
  label: string;
  tooltip: string;
  children: ReactNode;
}) {
  return (
    <div className="trisla-status-row">
      <dt>
        <span className="trisla-field-label" title={tooltip}>
          {label}
        </span>
        <span className="trisla-field-info" title={tooltip} aria-hidden="true">
          ⓘ
        </span>
      </dt>
      <dd>{children}</dd>
    </div>
  );
}

function MetricCard({ row }: { row: DomainMetricExplainability }) {
  const name = metricDisplayName(row.metric, row);
  const status = row.status ?? "Unknown";
  const statusTip = STATUS_TOOLTIPS[status] ?? "";

  return (
    <article className="trisla-domain-metric-card">
      <h5>{name}</h5>
      <dl>
        <FieldRow label={UX_LABELS.observed} tooltip={FIELD_TOOLTIPS.observed}>
          {formatMetricValue(row.observed, row.metric)}
        </FieldRow>
        <FieldRow label={UX_LABELS.referenceThreshold} tooltip={FIELD_TOOLTIPS.referenceThreshold}>
          {formatMetricValue(row.threshold, row.metric)}
        </FieldRow>
        <FieldRow label={UX_LABELS.complianceScore} tooltip={FIELD_TOOLTIPS.complianceScore}>
          {row.compliance_score !== undefined && row.compliance_score !== null
            ? formatCompliancePercent(row.compliance_score)
            : "Not available"}
        </FieldRow>
        <FieldRow
          label={UX_LABELS.requiredComplianceBand}
          tooltip={FIELD_TOOLTIPS.requiredComplianceBand}
        >
          {REQUIRED_COMPLIANCE_BAND_PERCENT}%
        </FieldRow>
        <FieldRow label={UX_LABELS.complianceStatus} tooltip={FIELD_TOOLTIPS.complianceStatus}>
          <span className={statusClass(row.status)} title={statusTip}>
            {complianceStatusDisplay(status)}
          </span>
          {statusTip ? <p className="trisla-metric-status-hint">{statusTip}</p> : null}
        </FieldRow>
      </dl>
    </article>
  );
}

function ComplianceStatusHelpBlock() {
  return (
    <details className="trisla-compliance-help" open>
      <summary>{COMPLIANCE_STATUS_HELP.title}</summary>
      <p className="trisla-muted">{COMPLIANCE_STATUS_HELP.intro}</p>
      <ul className="trisla-explain-list">
        {COMPLIANCE_STATUS_HELP.rules.map((rule) => (
          <li key={rule}>{rule}</li>
        ))}
      </ul>
      <div className="trisla-compliance-example">
        <strong>{COMPLIANCE_STATUS_HELP.exampleTitle}</strong>
        <ul className="trisla-explain-list">
          {COMPLIANCE_STATUS_HELP.exampleLines.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </div>
    </details>
  );
}

function DomainBlock({
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
          <span className="trisla-domain-score" title={UX_LABELS.domainAggregateScore}>
            {" "}
            — {UX_LABELS.domainAggregateScore}: {formatCompliancePercent(score)}
          </span>
        ) : null}
      </h4>
      <div className="trisla-domain-metrics-grid">
        {metrics.map((row) => (
          <MetricCard key={`${title}-${row.metric}`} row={row} />
        ))}
      </div>
    </section>
  );
}

export function DomainExplainabilityPanel({ assurance }: Props) {
  const domainExplainability = parseDomainExplainability(assurance?.domain_explainability);
  const scores = assurance?.domain_compliance;

  if (!hasDomainExplainability(domainExplainability)) {
    return null;
  }

  return (
    <section className="trisla-explain-section trisla-domain-explainability" aria-label="Domain Explainability">
      <h3 className="trisla-explainability-title">Domain Explainability</h3>
      <p className="trisla-muted">
        Per-metric KPI breakdown from runtime evaluation. Compliance Status reflects the compliance score
        versus the required band — not a direct observed-vs-threshold breach.
      </p>
      <ComplianceStatusHelpBlock />
      <DomainBlock title="RAN" score={scores?.ran} metrics={domainExplainability?.ran} />
      <DomainBlock title="TRANSPORT" score={scores?.transport} metrics={domainExplainability?.transport} />
      <DomainBlock title="CORE" score={scores?.core} metrics={domainExplainability?.core} />
    </section>
  );
}
