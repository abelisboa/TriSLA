/** POST /api/v1/sla/submit response — aligned to REAL_PAYLOAD_FREEZE captures. */
export type SubmitResponse = Record<string, unknown> & {
  decision?: string;
  status?: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
};

export function asMetadata(
  response: SubmitResponse | null | undefined,
): Record<string, unknown> | undefined {
  const m = response?.metadata;
  return m && typeof m === "object" ? m : undefined;
}

export function displayField(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Not available";
  }
  if (typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

export function hasValue(value: unknown): boolean {
  return value !== null && value !== undefined && value !== "";
}

export function asSlaRequirements(
  response: SubmitResponse | null | undefined,
): Record<string, unknown> | undefined {
  const sla = response?.sla_requirements;
  return sla && typeof sla === "object" ? (sla as Record<string, unknown>) : undefined;
}

/** tenant_id from submit response metadata paths observed in REAL_PAYLOAD_FREEZE. */
export function tenantIdFromResponse(response: SubmitResponse): unknown {
  const metadata = asMetadata(response);
  const governanceEvent = metadata?.governance_event;
  if (governanceEvent && typeof governanceEvent === "object") {
    return (governanceEvent as Record<string, unknown>).tenant_id;
  }
  const orchestrationIntent = metadata?.orchestration_intent;
  if (orchestrationIntent && typeof orchestrationIntent === "object") {
    return (orchestrationIntent as Record<string, unknown>).tenant_id;
  }
  return response.tenant_id;
}
