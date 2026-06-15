/**
 * RC-P20-03 — observed runtime metrics only (no compliance fields, no RSRP/RSRQ).
 */

import { formatOperatorMetric } from "./operatorFormat";

export type ObservedFieldDef = {
  keys: string[];
  label: string;
  formatLabel?: string;
};

/** Canonical observed fields per domain (implemented / wired metrics only). */
export const OBSERVED_RAN_FIELDS: ObservedFieldDef[] = [
  { keys: ["prb_utilization"], label: "PRB Utilization", formatLabel: "PRB Utilization" },
  { keys: ["latency_ms", "latency"], label: "Latency", formatLabel: "Latency" },
  { keys: ["reliability_pct", "reliability"], label: "Reliability", formatLabel: "Reliability" },
];

export const OBSERVED_TRANSPORT_FIELDS: ObservedFieldDef[] = [
  { keys: ["rtt_ms", "rtt"], label: "RTT", formatLabel: "Latency" },
  { keys: ["jitter_ms", "jitter"], label: "Jitter", formatLabel: "Jitter" },
  {
    keys: ["bandwidth_mbps", "throughput_mbps", "throughput", "bandwidth"],
    label: "Bandwidth",
    formatLabel: "Throughput",
  },
  { keys: ["packet_loss_pct", "packet_loss"], label: "Packet Loss", formatLabel: "Packet Loss" },
];

export const OBSERVED_CORE_FIELDS: ObservedFieldDef[] = [
  { keys: ["cpu_utilization", "cpu"], label: "CPU", formatLabel: "CPU Utilization" },
  {
    keys: ["memory_bytes", "memory", "memory_utilization"],
    label: "Memory",
    formatLabel: "Memory Utilization",
  },
  { keys: ["availability_pct", "availability"], label: "Availability", formatLabel: "Availability" },
];

const PROXY_METADATA_KEYS = new Set(["reliability_proxy_kind", "availability_proxy_kind"]);

export type ObservedTelemetryRow = { label: string; value: string; raw: unknown };

function pick(obj: Record<string, unknown> | undefined, keys: string[]): unknown {
  if (!obj) return undefined;
  for (const key of keys) {
    const v = obj[key];
    if (v !== null && v !== undefined && v !== "") return v;
  }
  return undefined;
}

export function formatObservedValue(label: string, value: unknown): string {
  if (value === null || value === undefined) return "Not available";
  return formatOperatorMetric(label, value);
}

export function buildObservedRows(
  domain: Record<string, unknown> | undefined,
  fields: ObservedFieldDef[],
): ObservedTelemetryRow[] {
  if (!domain) return [];
  const rows: ObservedTelemetryRow[] = [];
  for (const def of fields) {
    const raw = pick(domain, def.keys);
    if (raw === undefined) continue;
    const fmtLabel = def.formatLabel ?? def.label;
    rows.push({
      label: def.label,
      value: formatObservedValue(fmtLabel, raw),
      raw,
    });
  }
  return rows;
}

export function observedRanRows(ran: unknown): ObservedTelemetryRow[] {
  return buildObservedRows(
    ran && typeof ran === "object" ? (ran as Record<string, unknown>) : undefined,
    OBSERVED_RAN_FIELDS,
  );
}

export function observedTransportRows(transport: unknown): ObservedTelemetryRow[] {
  return buildObservedRows(
    transport && typeof transport === "object" ? (transport as Record<string, unknown>) : undefined,
    OBSERVED_TRANSPORT_FIELDS,
  );
}

export function observedCoreRows(core: unknown): ObservedTelemetryRow[] {
  return buildObservedRows(
    core && typeof core === "object" ? (core as Record<string, unknown>) : undefined,
    OBSERVED_CORE_FIELDS,
  );
}

/** Canonical observed-only object for technical JSON (primary key per metric). */
export function filterObservedDomainObject(
  domain: Record<string, unknown> | undefined,
  fields: ObservedFieldDef[],
): Record<string, unknown> | undefined {
  if (!domain || typeof domain !== "object") return undefined;
  const out: Record<string, unknown> = {};
  for (const def of fields) {
    const raw = pick(domain, def.keys);
    if (raw !== undefined) out[def.keys[0]] = raw;
  }
  for (const key of PROXY_METADATA_KEYS) {
    delete out[key];
  }
  return Object.keys(out).length > 0 ? out : undefined;
}

export function isObservedSnapshotPopulated(snapshot: {
  ran?: unknown;
  transport?: unknown;
  core?: unknown;
}): boolean {
  return (
    observedRanRows(snapshot.ran).length > 0 ||
    observedTransportRows(snapshot.transport).length > 0 ||
    observedCoreRows(snapshot.core).length > 0
  );
}
