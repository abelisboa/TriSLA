/** Sprint 6C — domain_explainability rendering (additive runtime_assurance field). */

export type DomainMetricExplainability = {
  metric?: string;
  observed?: number | null;
  threshold?: number;
  compliance_score?: number | null;
  status?: "PASS" | "FAIL" | "MISSING" | "N/A" | string;
  policy?: string;
  policy_reason?: string;
  measurement_semantics?: string;
  measurement_note?: string;
  source?: string;
};

export type DomainExplainabilityPayload = {
  ran?: DomainMetricExplainability[];
  transport?: DomainMetricExplainability[];
  core?: DomainMetricExplainability[];
};

const METRIC_LABELS: Record<string, string> = {
  latency_ms: "Latency",
  jitter_ms: "Jitter",
  reliability: "Reliability",
  cpu_utilization: "CPU Utilization",
  prb_utilization: "PRB Utilization",
  packet_loss: "Packet Loss",
  packet_loss_pct: "Packet Loss",
  bandwidth: "Bandwidth",
  bandwidth_mbps: "Bandwidth",
  throughput_dl_mbps: "Throughput DL",
  throughput_ul_mbps: "Throughput UL",
  cpu: "CPU",
  memory: "Memory",
  availability: "Availability",
  availability_pct: "Availability",
  attach_success_rate: "Attach Success Rate",
  event_throughput: "Event Throughput",
  session_setup_time: "Session Setup Time",
};

/** Metrics stored as fractional utilization (0–1) but displayed with % suffix. */
const FRACTIONAL_PERCENT_METRICS = new Set(["cpu", "memory", "cpu_utilization"]);

export function parseDomainExplainability(raw: unknown): DomainExplainabilityPayload | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  return raw as DomainExplainabilityPayload;
}

export function metricDisplayName(
  metric: string | undefined,
  row?: Pick<DomainMetricExplainability, "measurement_note">,
): string {
  if (!metric) return "Metric";
  if (
    metric === "cpu_utilization" &&
    row?.measurement_note?.includes("PRB")
  ) {
    return "PRB Utilization";
  }
  return METRIC_LABELS[metric] ?? metric.replace(/_/g, " ");
}

export function unitForMetric(metric: string | undefined): string {
  if (!metric) return "";
  const m = metric.toLowerCase();
  if (m.includes("latency") || m.includes("jitter") || m.includes("rtt")) return "ms";
  if (m.includes("throughput") && m.includes("mbps")) return "Mbps";
  if (m.includes("bandwidth")) return "Mbps";
  if (m.includes("packet_loss")) return "%";
  if (m.includes("reliability") || m.includes("availability") || m.includes("attach_success")) return "%";
  if (m.includes("cpu") || m.includes("memory") || m.includes("utilization")) return "%";
  if (m.includes("event_throughput")) return "events/s";
  return "";
}

export function formatMetricValue(value: number | null | undefined, metric?: string): string {
  if (value === null || value === undefined) return "Not available";
  const unit = unitForMetric(metric);
  let display = value;
  const m = (metric || "").toLowerCase();
  if (
    unit === "%" &&
    FRACTIONAL_PERCENT_METRICS.has(m) &&
    Math.abs(value) >= 0 &&
    Math.abs(value) < 1.5
  ) {
    display = value * 100;
  }
  const rounded = Number.isInteger(display) ? String(display) : display.toFixed(2);
  return unit ? `${rounded} ${unit}` : rounded;
}

export function statusClass(status: string | undefined): string {
  switch (status) {
    case "PASS":
      return "trisla-metric-pass";
    case "FAIL":
      return "trisla-metric-fail";
    case "MISSING":
      return "trisla-metric-missing";
    case "N/A":
      return "trisla-metric-na";
    default:
      return "trisla-metric-unknown";
  }
}

export function hasDomainExplainability(payload: DomainExplainabilityPayload | undefined): boolean {
  if (!payload) return false;
  return (["ran", "transport", "core"] as const).some(
    (d) => Array.isArray(payload[d]) && (payload[d]?.length ?? 0) > 0,
  );
}
