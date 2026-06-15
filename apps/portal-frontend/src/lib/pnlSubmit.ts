/** POST /api/v1/sla/interpret response — aligned to REAL_PAYLOAD_FREEZE payload_pnl.json */
export type InterpretResponse = Record<string, unknown> & {
  intent_id?: string | null;
  nest_id?: string | null;
  service_type?: string | null;
  slice_type?: string | null;
  tenant_id?: string | null;
  status?: string | null;
  message?: string | null;
  sla_requirements?: Record<string, unknown> | null;
  technical_parameters?: Record<string, unknown> | null;
  template_id?: string | null;
};

export type SubmitRequestPayload = {
  template_id: string;
  tenant_id: string;
  form_values: Record<string, unknown>;
};

function slaRequirements(
  interpret: InterpretResponse,
): Record<string, unknown> | undefined {
  const req = interpret.sla_requirements;
  return req && typeof req === "object" ? req : undefined;
}

function isPresent(value: unknown): value is NonNullable<unknown> {
  return value !== null && value !== undefined && value !== "";
}

/**
 * Maps interpret → submit form_values (P2 — PNL = TRANSPORT).
 * Forwards all present sla_requirements keys without conversion or filtering.
 * Omits null/empty values only (backend validator skips them).
 */
export function buildFormValuesFromInterpret(
  interpret: InterpretResponse,
): Record<string, unknown> {
  const formValues: Record<string, unknown> = {};

  const sla = slaRequirements(interpret);
  if (sla) {
    for (const [key, value] of Object.entries(sla)) {
      if (isPresent(value)) {
        formValues[key] = value;
      }
    }
  }

  const sliceType = interpret.slice_type ?? interpret.service_type;
  if (isPresent(sliceType)) {
    if (!isPresent(formValues.slice_type)) {
      formValues.slice_type = sliceType;
    }
    if (!isPresent(formValues.type)) {
      formValues.type = sliceType;
    }
  }

  return formValues;
}

/**
 * Builds POST /api/v1/sla/submit body from interpret + resolved template_id.
 * template_id is required by submit API but not returned by interpret (REAL_PAYLOAD_FREEZE).
 */
export function buildSubmitPayloadFromInterpret(
  interpret: InterpretResponse,
  templateId: string,
): SubmitRequestPayload | null {
  const trimmedTemplate = templateId.trim();
  if (!trimmedTemplate) return null;

  const tenantId = interpret.tenant_id;
  if (!tenantId || !String(tenantId).trim()) return null;

  const formValues = buildFormValuesFromInterpret(interpret);
  if (Object.keys(formValues).length === 0) return null;

  return {
    template_id: trimmedTemplate,
    tenant_id: String(tenantId).trim(),
    form_values: formValues,
  };
}
