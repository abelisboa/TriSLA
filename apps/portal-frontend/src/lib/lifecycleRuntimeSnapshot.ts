/** Contract v2 telemetry snapshot helpers for Lifecycle Runtime Snapshot UI. */

export type TelemetryDomain = Record<string, unknown>;

export type TelemetrySnapshotV2 = {
  execution_id?: string;
  timestamp?: string;
  telemetry_contract_version?: string;
  ran?: TelemetryDomain;
  transport?: TelemetryDomain;
  core?: TelemetryDomain;
};

export type LifecycleDomainRow = { label: string; value: unknown };

function pick(obj: TelemetryDomain | undefined, keys: string[]): unknown {
  if (!obj || typeof obj !== "object") return undefined;
  for (const key of keys) {
    const v = obj[key];
    if (v !== null && v !== undefined && v !== "") return v;
  }
  return undefined;
}

export function parseTelemetrySnapshot(raw: unknown): TelemetrySnapshotV2 | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  return raw as TelemetrySnapshotV2;
}

export function ranRowsForLifecycle(ran: TelemetryDomain | undefined): LifecycleDomainRow[] {
  if (!ran) return [];
  const rows: LifecycleDomainRow[] = [];
  const prb = pick(ran, ["prb_utilization"]);
  const load = pick(ran, ["latency_ms", "latency", "radio_load"]);
  if (prb !== undefined) rows.push({ label: "PRB Utilization", value: prb });
  if (load !== undefined) rows.push({ label: "Radio Load", value: load });
  return rows;
}

export function transportRowsForLifecycle(
  transport: TelemetryDomain | undefined,
): LifecycleDomainRow[] {
  if (!transport) return [];
  const rows: LifecycleDomainRow[] = [];
  const latency = pick(transport, ["latency_ms", "rtt_ms", "rtt", "latency"]);
  const jitter = pick(transport, ["jitter_ms", "jitter"]);
  const throughput = pick(transport, ["throughput_mbps", "throughput"]);
  if (latency !== undefined) rows.push({ label: "Latency", value: latency });
  if (jitter !== undefined) rows.push({ label: "Jitter", value: jitter });
  if (throughput !== undefined) rows.push({ label: "Throughput", value: throughput });
  return rows;
}

export function coreRowsForLifecycle(core: TelemetryDomain | undefined): LifecycleDomainRow[] {
  if (!core) return [];
  const rows: LifecycleDomainRow[] = [];
  const cpu = pick(core, ["cpu_utilization", "cpu"]);
  const memory = pick(core, ["memory_bytes", "memory", "memory_utilization"]);
  const sessions = pick(core, ["sessions", "active_sessions"]);
  if (cpu !== undefined) rows.push({ label: "CPU", value: cpu });
  if (memory !== undefined) rows.push({ label: "Memory", value: memory });
  if (sessions !== undefined) rows.push({ label: "Sessions", value: sessions });
  return rows;
}

export function isRuntimeSnapshotPopulated(snapshot: TelemetrySnapshotV2 | undefined): boolean {
  if (!snapshot) return false;
  return (
    ranRowsForLifecycle(snapshot.ran).length > 0 ||
    transportRowsForLifecycle(snapshot.transport).length > 0 ||
    coreRowsForLifecycle(snapshot.core).length > 0
  );
}

export function snapshotHasNullDomainWhenDataExists(
  snapshot: TelemetrySnapshotV2 | undefined,
): boolean {
  if (!isRuntimeSnapshotPopulated(snapshot)) return false;
  const domains = [snapshot?.ran, snapshot?.transport, snapshot?.core];
  return domains.some((d) => d && typeof d === "object" && Object.keys(d).length > 0);
}
