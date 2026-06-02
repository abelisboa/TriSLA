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
  packet_loss: "Packet Loss",
  bandwidth: "Bandwidth",
  throughput_dl_mbps: "Throughput DL",
  throughput_ul_mbps: "Throughput UL",
  cpu: "CPU",
  memory: "Memory",
  availability: "Availability",
  attach_success_rate: "Attach Success Rate",
  event_throughput: "Event Throughput",
  session_setup_time: "Session Setup Time",
};

export function parseDomainExplainability(raw: unknown): DomainExplainabilityPayload | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  return raw as DomainExplainabilityPayload;
}

export function metricDisplayName(metric: string | undefined): string {
  if (!metric) return "Metric";
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
  const rounded = Number.isInteger(value) ? String(value) : value.toFixed(2);
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
