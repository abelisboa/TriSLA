import { formatBytesToMB } from "./format";

function finiteNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const n = typeof value === "number" ? value : Number(String(value).trim());
  return Number.isFinite(n) ? n : null;
}

/** Core CPU rate sum (cores/sec) → operator percent display. */
export function formatCoreCpuUtilization(value: unknown): string {
  const n = finiteNumber(value);
  if (n === null) return "Not available";
  const pct = n <= 1 ? n * 100 : n;
  return `${pct.toFixed(2)} %`;
}

/** Core memory working-set bytes → MB. */
export function formatCoreMemoryUtilization(value: unknown): string {
  const n = finiteNumber(value);
  if (n === null) return "Not available";
  if (n > 1_000_000) return formatBytesToMB(n);
  return `${n.toFixed(2)} %`;
}

/** PRB / load ratio → percent. */
export function formatPrbUtilization(value: unknown): string {
  const n = finiteNumber(value);
  if (n === null) return "Not available";
  const pct = n <= 1 ? n * 100 : n;
  return `${pct.toFixed(2)} %`;
}

export function formatLatencyMs(value: unknown): string {
  const n = finiteNumber(value);
  if (n === null) return "Not available";
  return `${n.toFixed(2)} ms`;
}

export function formatThroughputMbps(value: unknown): string {
  const n = finiteNumber(value);
  if (n === null) return "Not available";
  return `${n.toFixed(2)} Mbps`;
}

export function formatSessionCount(value: unknown): string {
  const n = finiteNumber(value);
  if (n === null) return "Not available";
  return String(Math.round(n));
}

export function formatDecisionScore(value: unknown): string {
  const n = finiteNumber(value);
  if (n === null) return "Not available";
  if (n <= 1) return `${(n * 100).toFixed(1)} %`;
  return n.toFixed(2);
}

export function formatOperatorMetric(label: string, value: unknown): string {
  const key = label.toLowerCase();
  if (key.includes("cpu utilization")) return formatCoreCpuUtilization(value);
  if (key.includes("memory utilization")) return formatCoreMemoryUtilization(value);
  if (key.includes("prb")) return formatPrbUtilization(value);
  if (key.includes("latency") || key.includes("jitter")) return formatLatencyMs(value);
  if (key.includes("throughput")) return formatThroughputMbps(value);
  if (key.includes("session")) return formatSessionCount(value);
  if (key.includes("ran load")) return formatPrbUtilization(value);
  if (key.includes("transport latency")) return formatLatencyMs(value);
  const n = finiteNumber(value);
  if (n !== null) {
    if (Math.abs(n) >= 1000) return formatBytesToMB(n);
    if (n < 1 && n > 0) return `${(n * 100).toFixed(2)} %`;
    if (Number.isInteger(n)) return String(n);
    return n.toFixed(2);
  }
  if (value === null || value === undefined || value === "") return "Not available";
  return String(value);
}
