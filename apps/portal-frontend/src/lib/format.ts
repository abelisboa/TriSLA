export function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "unavailable";
  }

  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }

  if (typeof value === "string" || typeof value === "number") {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value.length === 0 ? "[]" : JSON.stringify(value, null, 2);
  }

  if (typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }

  return String(value);
}

/** Fallback controlado para exibição (payload real API-2). */
export function fallback<T>(value: T | null | undefined): T | "N/A" {
  if (value === null || value === undefined) return "N/A";
  return value;
}

/** Extrai o primeiro valor numérico de um result Prometheus (value[1]). */
export function prometheusFirstValue(
  result: Array<{ value?: [number, string] }> | null | undefined,
): string | number | null {
  const v = result?.[0]?.value?.[1];
  if (v === undefined || v === null) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : v;
}

/** Formata bytes em MB para exibição (payload real). */
export function formatBytesToMB(bytes: number | string | null | undefined): string {
  const n = typeof bytes === "string" ? Number(bytes) : bytes;
  if (n == null || !Number.isFinite(n)) return "N/A";
  return `${(n / 1024 / 1024).toFixed(2)} MB`;
}

