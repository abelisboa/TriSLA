/** Platform reachability display helpers (Sprint 5N2). */

export const NASP_MODULE_KEYS = [
  "sem_csmf",
  "ml_nsmf",
  "decision",
  "bc_nssmf",
  "sla_agent",
] as const;

export type ReachabilityAggregate = {
  reachable_modules: number;
  total_modules: number;
  reachability_percent: number;
};

function moduleReachable(mod: unknown): boolean {
  if (!mod || typeof mod !== "object") return false;
  const record = mod as Record<string, unknown>;
  if (record.reachable === true) return true;
  if (record.status_code === 200 || record.status_code === "200") return true;
  return false;
}

export function aggregateFromDiagnostics(
  diagnostics: Record<string, unknown> | null | undefined,
): ReachabilityAggregate | null {
  if (!diagnostics) return null;
  const total = NASP_MODULE_KEYS.length;
  const reachable = NASP_MODULE_KEYS.filter((key) =>
    moduleReachable(diagnostics[key]),
  ).length;
  return {
    reachable_modules: reachable,
    total_modules: total,
    reachability_percent: total ? Math.round((100 * reachable) / total) : 0,
  };
}

export function parseReachabilityAggregate(raw: unknown): ReachabilityAggregate | null {
  if (!raw || typeof raw !== "object") return null;
  const obj = raw as Record<string, unknown>;
  const reachable = obj.reachable_modules;
  const total = obj.total_modules;
  const percent = obj.reachability_percent;
  if (
    typeof reachable !== "number" ||
    typeof total !== "number" ||
    typeof percent !== "number"
  ) {
    return null;
  }
  return {
    reachable_modules: reachable,
    total_modules: total,
    reachability_percent: percent,
  };
}

/** Operator label aligned with Sprint 5N (Operational / Partial / Unavailable). */
export function formatPlatformReachability(
  aggregate: ReachabilityAggregate | null | undefined,
  loadState: "idle" | "loading" | "ready" | "error" = "ready",
): string {
  if (loadState === "loading" || loadState === "idle") return "Loading…";
  if (loadState === "error" || !aggregate) return "Unavailable";
  const { reachable_modules, total_modules, reachability_percent } = aggregate;
  if (total_modules === 0) return "Unavailable";
  if (reachable_modules === total_modules) {
    return `${reachable_modules}/${total_modules} Operational`;
  }
  if (reachable_modules === 0) {
    return `0/${total_modules} Unavailable`;
  }
  return `${reachable_modules}/${total_modules} Operational (${reachability_percent}%)`;
}
