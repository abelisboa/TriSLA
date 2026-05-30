type NaspModule = Record<string, unknown>;

function moduleReachable(mod: unknown): boolean {
  if (!mod || typeof mod !== "object") return false;
  const record = mod as NaspModule;
  if (record.reachable === true) return true;
  if (record.status_code === 200) return true;
  return false;
}

export function healthFieldDisplay(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Not reported by backend";
  }
  if (typeof value === "boolean") {
    return value ? "Operational" : "Unavailable";
  }
  const text = String(value).trim().toLowerCase();
  if (text === "ok" || text === "healthy") return "Operational";
  if (text === "degraded") return "Degraded";
  return String(value);
}

export function inferNaspReachability(
  nasp: Record<string, unknown> | null | undefined,
): string {
  if (!nasp) return "Not reported by backend";

  const moduleKeys = ["sem_csmf", "ml_nsmf", "decision", "bc_nssmf", "sla_agent"];
  const reachableModules = moduleKeys.filter((key) => moduleReachable(nasp[key]));

  if (reachableModules.length === 0) {
    return "Not reported by backend";
  }
  if (reachableModules.length === moduleKeys.length) {
    return "All modules connected";
  }
  return `Partial — ${reachableModules.length}/${moduleKeys.length} modules connected`;
}

export function formatNaspModuleStatus(value: unknown): string {
  if (value === null || value === undefined) {
    return "Not available";
  }
  if (typeof value !== "object") {
    return String(value);
  }

  const record = value as NaspModule;
  if (record.reachable === true) {
    return "Connected";
  }
  if (record.reachable === false) {
    return "Unavailable";
  }
  if (record.status_code != null) {
    const code = Number(record.status_code);
    if (code >= 200 && code < 300) return "Connected";
    return "Unavailable";
  }
  return "Reported";
}

/** Technical probe details for collapsed Technical Details section. */
export function formatNaspModuleTechnical(value: unknown): string {
  if (value === null || value === undefined) {
    return "Not available";
  }
  if (typeof value !== "object") {
    return String(value);
  }
  return JSON.stringify(value, null, 2);
}
