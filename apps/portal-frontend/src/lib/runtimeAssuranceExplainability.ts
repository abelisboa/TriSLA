/**
 * Sprint 6B — expose existing runtime_assurance + telemetry_snapshot fields (no new runtime logic).
 */

import type { RuntimeAssurancePayload } from "./runtimeAssurance";
import {
  coreRowsForLifecycle,
  parseTelemetrySnapshot,
  ranRowsForLifecycle,
  transportRowsForLifecycle,
  type TelemetrySnapshotV2,
} from "./lifecycleRuntimeSnapshot";

export type DriftIndicator = {
  path?: string;
  reference?: number;
  current?: number;
  delta?: number;
};

export type WhyExplanation = {
  title: string;
  summary: string;
  observed?: string;
  target?: string;
  source: string;
};

const CODE_LABELS: Record<string, string> = {
  "service_profile.latency": "Service latency above SLA target",
  "service_profile.throughput": "Service throughput below SLA target",
  "service_profile.reliability": "Service reliability below SLA target",
  "telemetry.drift": "Telemetry drift detected vs prior snapshot",
  "telemetry_snapshot.empty": "Telemetry snapshot empty — cannot evaluate SLOs",
  "telemetry.incomplete": "Telemetry collection incomplete",
};

function labelForCode(code: string): string {
  return CODE_LABELS[code] ?? code.replace(/\./g, " ").replace(/_/g, " ");
}

function formatNum(value: number, unit?: string): string {
  const rounded = Number.isInteger(value) ? String(value) : value.toFixed(2);
  return unit ? `${rounded} ${unit}` : rounded;
}

function unitForPath(path: string): string | undefined {
  const p = path.toLowerCase();
  if (p.includes("latency") || p.includes("rtt") || p.includes("jitter")) return "ms";
  if (p.includes("prb") || p.includes("cpu") || p.includes("utilization")) return "%";
  if (p.includes("throughput")) return "Mbps";
  return undefined;
}

function pathToHeadline(path: string): string {
  const parts = path.split(".");
  const domain = parts[0]?.toUpperCase() ?? "Runtime";
  const metric = parts.slice(1).join(" ").replace(/_/g, " ") || "metric";
  return `${domain} ${metric} changed vs baseline`;
}

export function parseDriftIndicators(raw: unknown): DriftIndicator[] {
  if (!Array.isArray(raw)) return [];
  return raw.filter((x) => x && typeof x === "object") as DriftIndicator[];
}

export function formatCompliancePercent(score: number | undefined): string {
  if (score === undefined || score === null || Number.isNaN(score)) return "Not available";
  return `${Math.round(score * 100)}%`;
}

export function formatDomainCompliance(
  domainCompliance: Record<string, number | undefined> | undefined,
): Array<{ domain: string; score: string }> {
  if (!domainCompliance || typeof domainCompliance !== "object") return [];
  return (["ran", "transport", "core"] as const)
    .filter((d) => domainCompliance[d] !== undefined)
    .map((d) => ({
      domain: d.toUpperCase(),
      score: formatCompliancePercent(domainCompliance[d]),
    }));
}

function primarySnapshotRow(
  domain: string | undefined,
  snap: TelemetrySnapshotV2 | undefined,
): { label: string; value: string } | undefined {
  if (!domain || !snap) return undefined;
  const d = domain.toLowerCase();
  let rows: Array<{ label: string; value: unknown }> = [];
  if (d === "ran") rows = ranRowsForLifecycle(snap.ran);
  else if (d === "transport") rows = transportRowsForLifecycle(snap.transport);
  else if (d === "core") rows = coreRowsForLifecycle(snap.core);
  const first = rows[0];
  if (!first || first.value === undefined) return undefined;
  return { label: first.label, value: String(first.value) };
}

function whyFromDrift(indicators: DriftIndicator[]): WhyExplanation[] {
  return indicators.map((d) => {
    const path = d.path ?? "metric";
    const unit = unitForPath(path);
    return {
      title: pathToHeadline(path),
      summary: pathToHeadline(path),
      observed: d.current !== undefined ? formatNum(d.current, unit) : undefined,
      target: d.reference !== undefined ? formatNum(d.reference, unit) : undefined,
      source: "drift_indicators",
    };
  });
}

function whyFromCodes(
  codes: string[],
  kind: "violation" | "warning",
  snap: TelemetrySnapshotV2 | undefined,
): WhyExplanation[] {
  return codes.map((code) => {
    const metrics = snapshotMetricForCode(code, snap);
    return {
      title: labelForCode(code),
      summary: kind === "violation" ? labelForCode(code) : `${labelForCode(code)} (warning)`,
      observed: metrics.observed,
      target: metrics.target,
      source: kind === "violation" ? "violations + telemetry_snapshot" : "warnings + telemetry_snapshot",
    };
  });
}

function snapshotMetricForCode(
  code: string,
  snap: TelemetrySnapshotV2 | undefined,
): { observed?: string; target?: string } {
  if (!snap) return {};
  if (code === "service_profile.latency") {
    const t = snap.transport;
    const v =
      t && typeof t === "object"
        ? (t as Record<string, unknown>).rtt_ms ??
          (t as Record<string, unknown>).latency_ms ??
          (t as Record<string, unknown>).latency
        : undefined;
    if (v !== undefined) return { observed: formatNum(Number(v), "ms") };
  }
  if (code === "service_profile.throughput") {
    const t = snap.transport;
    const v =
      t && typeof t === "object"
        ? (t as Record<string, unknown>).throughput_mbps ?? (t as Record<string, unknown>).throughput
        : undefined;
    if (v !== undefined) return { observed: formatNum(Number(v), "Mbps") };
  }
  const ran = snap.ran;
  const prb =
    ran && typeof ran === "object" ? (ran as Record<string, unknown>).prb_utilization : undefined;
  if (code.includes("reliability") && prb !== undefined) {
    return { observed: formatNum(Number(prb), "%") };
  }
  const core = snap.core;
  const cpu =
    core && typeof core === "object"
      ? ((core as Record<string, unknown>).cpu_utilization ?? (core as Record<string, unknown>).cpu)
      : undefined;
  if (cpu !== undefined && (code.includes("cpu") || code === "telemetry.drift")) {
    return { observed: formatNum(Number(cpu), "%") };
  }
  return {};
}

function whyFromBottleneck(
  assurance: RuntimeAssurancePayload,
  snap: TelemetrySnapshotV2 | undefined,
): WhyExplanation | undefined {
  const domain = assurance.bottleneck_domain;
  if (!domain) return undefined;
  const scores = assurance.domain_compliance as Record<string, number> | undefined;
  const score = scores?.[domain.toLowerCase()];
  const row = primarySnapshotRow(domain, snap);
  const domainLabel = domain.toUpperCase();
  const summary =
    score !== undefined && score < 0.85
      ? `${domainLabel} domain compliance is low (${formatCompliancePercent(score)})`
      : `${domainLabel} is the bottleneck domain for this evaluation`;
  return {
    title: `${domainLabel} domain drives assurance state`,
    summary,
    observed: row ? `${row.label}: ${row.value}` : undefined,
    target: "Domain compliance band ≥ 85% (evaluator aggregate)",
    source: "bottleneck_domain + domain_compliance + telemetry_snapshot",
  };
}

export function whySectionHeading(state: string | undefined): string | undefined {
  switch (state) {
    case "WARNING":
      return "WHY WARNING?";
    case "AT_RISK":
      return "WHY AT RISK?";
    case "VIOLATED":
      return "WHY VIOLATED?";
    case "INCOMPLETE":
      return "WHY INCOMPLETE?";
    default:
      return undefined;
  }
}

/** Build operator-facing WHY lines from existing API fields only. */
export function buildWhyExplanations(
  assurance: RuntimeAssurancePayload | undefined,
  telemetrySnapshot: unknown,
): WhyExplanation[] {
  if (!assurance) return [];
  const snap = parseTelemetrySnapshot(telemetrySnapshot);
  const drift = parseDriftIndicators(assurance.drift_indicators);
  const items: WhyExplanation[] = [];

  items.push(...whyFromDrift(drift));
  items.push(...whyFromCodes(assurance.violations ?? [], "violation", snap));
  items.push(...whyFromCodes(assurance.warnings ?? [], "warning", snap));

  if (items.length === 0) {
    const bottleneck = whyFromBottleneck(assurance, snap);
    if (bottleneck) items.push(bottleneck);
  }

  return items;
}

export function hasExplainabilityContent(assurance: RuntimeAssurancePayload | undefined): boolean {
  if (!assurance) return false;
  return (
    (assurance.violations?.length ?? 0) > 0 ||
    (assurance.warnings?.length ?? 0) > 0 ||
    (parseDriftIndicators(assurance.drift_indicators).length ?? 0) > 0 ||
    assurance.bottleneck_domain !== undefined ||
    assurance.sla_compliance !== undefined ||
    (assurance.domain_compliance && Object.keys(assurance.domain_compliance).length > 0) ||
    Boolean(assurance.recommendation)
  );
}
