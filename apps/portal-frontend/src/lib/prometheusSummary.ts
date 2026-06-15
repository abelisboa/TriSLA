import { formatOperatorMetric } from "./operatorFormat";
import {
  fallback,
  formatBytesToMB,
  prometheusFirstValue,
} from "./format";

/** Flat v2 summary from GET /api/v1/prometheus/summary (runtime baseline). */
export type PrometheusSummaryV2 = {
  ran_load?: number | null;
  transport_latency?: number | null;
  throughput_mbps?: number | null;
  sessions?: number | null;
  cpu?: number | null;
  ran_prb_utilization?: number | null;
  formula?: string | null;
  metadata?: {
    telemetry_version?: string;
    telemetry_units?: Record<string, string>;
  };
};

/** Legacy PromQL envelope (optional fallback when backend returns old shape). */
export type PrometheusSummaryLegacy = {
  up?: {
    status?: string;
    data?: { result?: Array<{ value?: [number, string] }> };
  };
  cpu?: {
    status?: string;
    data?: { result?: Array<{ value?: [number, string] }> };
  };
  memory?: {
    status?: string;
    data?: { result?: Array<{ value?: [number, string] }> };
  };
};

export type PrometheusSummaryPayload = PrometheusSummaryV2 & PrometheusSummaryLegacy;

const V2_KEYS = [
  "ran_load",
  "transport_latency",
  "throughput_mbps",
  "sessions",
  "ran_prb_utilization",
] as const;

export function formatMetricValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "Not available";
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? String(value) : "Not available";
  }
  if (typeof value === "string" && value.trim() === "") {
    return "Not available";
  }
  return String(value);
}

export function isV2FlatSummary(
  payload: PrometheusSummaryPayload | null | undefined,
): boolean {
  if (!payload) return false;
  const hasV2Field = V2_KEYS.some((key) => key in payload);
  const hasLegacyEnvelope =
    payload.up?.status != null ||
    payload.cpu?.data?.result != null ||
    payload.memory?.data?.result != null;
  return hasV2Field && !hasLegacyEnvelope;
}

export type V2SummaryDisplayRow = {
  label: string;
  value: string;
  title?: string;
};

export const OBSERVED_THROUGHPUT_TOOLTIP =
  "RAN dataplane throughput proxy (N6 peer ingress)";

export function v2SummaryDisplayRows(
  payload: PrometheusSummaryV2,
): V2SummaryDisplayRow[] {
  return [
    { label: "RAN Load", value: formatOperatorMetric("RAN Load", payload.ran_load) },
    {
      label: "Transport Latency",
      value: formatOperatorMetric("Transport Latency", payload.transport_latency),
    },
    {
      label: "Observed Throughput",
      value: formatOperatorMetric("Throughput", payload.throughput_mbps),
      title: OBSERVED_THROUGHPUT_TOOLTIP,
    },
    { label: "Active Sessions", value: formatOperatorMetric("Active Sessions", payload.sessions) },
    { label: "CPU", value: formatOperatorMetric("CPU Utilization", payload.cpu) },
    {
      label: "RAN PRB Utilization",
      value: formatOperatorMetric("PRB Utilization", payload.ran_prb_utilization),
    },
  ];
}

export type LegacySummaryDisplayRow = { label: string; value: string; title?: string };

export function legacySummaryDisplayRows(
  payload: PrometheusSummaryLegacy,
): LegacySummaryDisplayRow[] {
  const upCount = payload.up?.data?.result?.length ?? null;
  const prometheusUp =
    payload.up?.status != null
      ? `${String(fallback(payload.up.status))}${upCount != null ? ` (${upCount} series)` : ""}`
      : "Not available";
  const cpuVal = prometheusFirstValue(payload.cpu?.data?.result);
  const memoryVal = prometheusFirstValue(payload.memory?.data?.result);

  return [
    { label: "Prometheus Up", value: prometheusUp },
    {
      label: "CPU",
      value: cpuVal !== null ? formatOperatorMetric("CPU Utilization", cpuVal) : "Not available",
    },
    {
      label: "Memory",
      value:
        memoryVal !== null
          ? formatOperatorMetric("Memory Utilization", memoryVal)
          : "Not available",
    },
  ];
}

export function isEmptyMetricsObject(
  value: Record<string, unknown> | null | undefined,
): boolean {
  if (!value) return true;
  return Object.keys(value).length === 0;
}

export function formatDomainMetricsState(
  payload: Record<string, unknown> | null | undefined,
  status: "idle" | "loading" | "ready" | "error",
  errorMessage?: string,
): string {
  if (status === "loading") return "Loading…";
  if (status === "error") {
    return errorMessage ?? "error retrieving source data";
  }
  if (status !== "ready") return "Not available";
  if (!payload || isEmptyMetricsObject(payload)) {
    return "No metrics in response";
  }
  return JSON.stringify(payload, null, 2);
}
