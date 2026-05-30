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
    return value ? "true" : "false";
  }
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
    return "Reachable modules (from diagnostics)";
  }
  return `Partial — ${reachableModules.length}/${moduleKeys.length} modules reachable`;
}

export function formatNaspModuleLabel(key: string): string {
  return key;
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
    const detail =
      record.detail ??
      (record.status_code != null ? `HTTP ${record.status_code}` : "ok");
    return `reachable — ${String(detail)}`;
  }
  if (record.reachable === false) {
    return "unreachable";
  }
  if (record.status_code != null) {
    return `HTTP ${record.status_code}`;
  }
  return "reported";
}
