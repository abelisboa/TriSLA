/** NASP module probe → operator-facing status (Sprint 5N). */

export type ModuleOperationalState =
  | "Operational"
  | "Warning"
  | "Degraded"
  | "Unavailable"
  | "Loading";

export type ModuleProbe = {
  reachable?: boolean | null;
  status_code?: unknown;
  detail?: unknown;
  module?: string;
};

export function formatModuleOperationalState(
  probe: ModuleProbe | null | undefined,
  loadState: "idle" | "loading" | "ready" | "error" = "ready",
): ModuleOperationalState {
  if (loadState === "loading" || loadState === "idle") return "Loading";
  if (loadState === "error") return "Unavailable";
  if (!probe || typeof probe !== "object") return "Unavailable";
  if (probe.reachable === true) {
    const code = probe.status_code;
    if (code === 200 || code === "200" || probe.detail === "ok") return "Operational";
    if (typeof code === "number" && code >= 500) return "Degraded";
    if (typeof code === "number" && code >= 400) return "Warning";
    return "Operational";
  }
  if (probe.reachable === false) return "Unavailable";
  return "Unavailable";
}

export function moduleOperationalLabel(state: ModuleOperationalState): string {
  return state;
}

export function normalizeModuleProbe(raw: unknown): ModuleProbe {
  if (!raw || typeof raw !== "object") return {};
  const obj = raw as Record<string, unknown>;
  return {
    reachable: typeof obj.reachable === "boolean" ? obj.reachable : null,
    status_code: obj.status_code ?? null,
    detail: obj.detail ?? null,
    module: typeof obj.module === "string" ? obj.module : undefined,
  };
}
