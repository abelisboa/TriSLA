import {
  formatMetricValue,
  type PrometheusSummaryPayload,
} from "./prometheusSummary";
import { formatOperatorMetric } from "./operatorFormat";

export type I1MetricsResponse = {
  interface?: string;
  metrics?: Record<string, unknown> | null;
};

export type DomainMetricRow = { label: string; value: string };

export type DomainCardModel = {
  rows: DomainMetricRow[];
  dataAvailability: string;
};

function isRealMetricValue(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "number") return Number.isFinite(value);
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return false;
    const num = Number(trimmed);
    return Number.isFinite(num);
  }
  return false;
}

function pickFirstReal(...values: unknown[]): unknown | undefined {
  for (const value of values) {
    if (isRealMetricValue(value)) return value;
  }
  return undefined;
}

function row(label: string, value: unknown): DomainMetricRow {
  return { label, value: formatOperatorMetric(label, value) };
}

function availabilityFromRows(rows: DomainMetricRow[]): string {
  const hasValue = rows.some(
    (r) => r.value !== "Not available" && r.value !== "Metrics unavailable",
  );
  return hasValue ? "Available" : "Metrics unavailable";
}

/** RAN: I1 prb → summary ran_prb → summary ran_load */
export function buildRanDomainCard(
  i1: I1MetricsResponse | null | undefined,
  summary: PrometheusSummaryPayload | null | undefined,
): DomainCardModel {
  const i1Metrics = i1?.metrics ?? {};
  const prb = pickFirstReal(
    i1Metrics.prb_utilization,
    summary?.ran_prb_utilization,
    summary?.ran_load,
  );

  const throughput = pickFirstReal(summary?.throughput_mbps);

  const rows: DomainMetricRow[] = [
    row("PRB Utilization", prb),
    row("Dataplane Throughput (N6)", throughput),
  ];

  return {
    rows,
    dataAvailability: availabilityFromRows(rows),
  };
}

/** Transport: I1 latency/jitter → summary transport_latency (no throughput — RAN-owned). */
export function buildTransportDomainCard(
  i1: I1MetricsResponse | null | undefined,
  summary: PrometheusSummaryPayload | null | undefined,
): DomainCardModel {
  const i1Metrics = i1?.metrics ?? {};
  const latency = pickFirstReal(i1Metrics.latency_ms, summary?.transport_latency);
  const jitter = pickFirstReal(i1Metrics.jitter_ms);

  const rows: DomainMetricRow[] = [
    row("Latency (ms)", latency),
    row("Jitter (ms)", jitter),
  ];

  return {
    rows,
    dataAvailability: availabilityFromRows(rows),
  };
}

/** Core: I1 cpu/memory → summary sessions */
export function buildCoreDomainCard(
  i1: I1MetricsResponse | null | undefined,
  summary: PrometheusSummaryPayload | null | undefined,
): DomainCardModel {
  const i1Metrics = i1?.metrics ?? {};
  const cpu = pickFirstReal(i1Metrics.cpu_utilization);
  const memory = pickFirstReal(i1Metrics.memory_utilization);
  const sessions = pickFirstReal(summary?.sessions);

  const rows: DomainMetricRow[] = [
    row("CPU Utilization", cpu),
    row("Memory Utilization", memory),
    row("Active Sessions", sessions),
  ];

  return {
    rows,
    dataAvailability: availabilityFromRows(rows),
  };
}

export function domainCardWhileLoading(): DomainCardModel {
  return { rows: [], dataAvailability: "Loading…" };
}

export function domainCardOnError(message?: string): DomainCardModel {
  return {
    rows: [],
    dataAvailability: message ?? "Not available",
  };
}
