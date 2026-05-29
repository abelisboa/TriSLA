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

/**
 * Maps interpret → submit form_values using only fields present in REAL_PAYLOAD_FREEZE
 * (payload_pnl.json sla_requirements + slice_type/service_type).
 * Omits null/empty values (backend validator skips them).
 */
export function buildFormValuesFromInterpret(
  interpret: InterpretResponse,
): Record<string, unknown> {
  const formValues: Record<string, unknown> = {};
  const sliceType = interpret.slice_type ?? interpret.service_type;
  if (sliceType !== null && sliceType !== undefined && String(sliceType).trim()) {
    formValues.type = sliceType;
    formValues.slice_type = sliceType;
  }

  const sla = slaRequirements(interpret);
  if (sla) {
    for (const key of ["latency", "throughput", "reliability"] as const) {
      const value = sla[key];
      if (value !== null && value !== undefined && value !== "") {
        formValues[key] = value;
      }
    }
  }

  return formValues;
}

/**
 * Builds POST /api/v1/sla/submit body from interpret + user-confirmed template_id.
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
