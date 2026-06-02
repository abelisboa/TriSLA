/**
 * Sprint 6E — UX labels and help text only (no runtime logic).
 * Documents the 85% band used by SLA-Agent; does not compute scores.
 */

/** Display-only mirror of SLA-Agent runtime assurance band (Sprint 6D audit). */
export const REQUIRED_COMPLIANCE_BAND_PERCENT = 85;

export const UX_LABELS = {
  observed: "Observed",
  referenceThreshold: "Reference Threshold",
  complianceScore: "Compliance Score",
  requiredComplianceBand: "Required Compliance Band",
  complianceStatus: "Compliance Status",
  domainAggregateScore: "Domain aggregate score",
} as const;

export const STATUS_TOOLTIPS: Record<string, string> = {
  PASS: "Compliance Score meets or exceeds the required compliance band (≥ 85%). This does not by itself mean the service is COMPLIANT overall.",
  FAIL: "Compliance Score is below the required compliance band (< 85%). This does not necessarily mean the metric exceeded its configured reference threshold.",
  MISSING:
    "No telemetry was available for this KPI at evaluation time. The domain score may be reduced when configured KPIs are missing.",
  "N/A":
    "Throughput observed with no active user-plane traffic. Per FLOW_AWARE policy (Sprint 7E), this KPI is not scored as capacity — it does not reduce the transport domain score.",
};

export const FIELD_TOOLTIPS = {
  observed: "Value from the runtime telemetry snapshot at evaluation time.",
  referenceThreshold:
    "Slice-configured reference used to normalize the compliance score. It is not the same as a binary pass/fail line for Compliance Status.",
  complianceScore:
    "Normalized metric score (0–100%) derived from observed value and reference threshold. Determines Compliance Status.",
  requiredComplianceBand:
    "Minimum compliance score required for PASS at metric level. Aligned with runtime assurance COMPLIANT band.",
  complianceStatus:
    "PASS if Compliance Score ≥ required band; FAIL if below; MISSING if no observed telemetry; N/A if flow-aware policy excludes idle throughput.",
} as const;

export const COMPLIANCE_STATUS_HELP = {
  title: "How Compliance Status Is Determined",
  intro:
    "Compliance Status is based on Compliance Score compared against the required Compliance Band — not a direct observed-vs-threshold comparison.",
  rules: [
    "PASS: Compliance Score ≥ 85%",
    "FAIL: Compliance Score < 85%",
    "MISSING: Telemetry unavailable for this KPI",
    "N/A: Not scored (e.g. idle throughput — not treated as zero capacity)",
  ],
  exampleTitle: "Example (latency)",
  exampleLines: [
    "Observed: 5.68 ms",
    "Reference Threshold: 20 ms",
    "Compliance Score: 71%",
    "Required Compliance Band: 85%",
    "Compliance Status: FAIL — score below band, even though observed is below reference threshold",
  ],
} as const;

export function complianceStatusDisplay(status: string | undefined): string {
  if (!status) return "Unknown";
  return status;
}
