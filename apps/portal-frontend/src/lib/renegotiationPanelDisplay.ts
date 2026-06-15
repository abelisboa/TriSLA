import { asMetadata, type SubmitResponse } from "./submitResponse";
import type { SlaRuntimeStatusResponse } from "./runtimeSupervision";

export type RenegotiationFields = {
  requestedType: unknown;
  requestedLatency: unknown;
  suggestedType: unknown;
  suggestedLatency: unknown;
  explanation: unknown;
};

function pickCanonicalSla(
  status?: SlaRuntimeStatusResponse | null,
  submit?: SubmitResponse,
): Record<string, unknown> | undefined {
  const md = submit ? asMetadata(submit) : undefined;
  const fromStatus = status?.operational_summary as Record<string, unknown> | undefined;
  const canonical =
    (md?.canonical_sla as Record<string, unknown> | undefined) ??
    (fromStatus?.canonical_sla as Record<string, unknown> | undefined);
  return canonical && typeof canonical === "object" ? canonical : undefined;
}

export function extractRenegotiationFields(
  statusData?: SlaRuntimeStatusResponse | null,
  submitResponse?: SubmitResponse,
): RenegotiationFields {
  const md = submitResponse ? asMetadata(submitResponse) : undefined;
  const operational = statusData?.operational_summary as Record<string, unknown> | undefined;
  const slaReq =
    operational?.sla_requirements ?? md?.sla_requirements ?? submitResponse?.sla_requirements;
  const canonical = pickCanonicalSla(statusData, submitResponse);
  const explanation =
    statusData?.admission_reasoning ??
    md?.decision_explanation_plain ??
    md?.decision_explanation;

  const requestedLatency =
    slaReq && typeof slaReq === "object"
      ? (slaReq as Record<string, unknown>).latency ??
        (slaReq as Record<string, unknown>).latency_ms
      : undefined;
  const requestedType =
    slaReq && typeof slaReq === "object"
      ? (slaReq as Record<string, unknown>).slice_type ??
        (slaReq as Record<string, unknown>).type
      : operational?.service_type;

  const suggestedLatency =
    canonical?.latency ?? canonical?.latency_ms;
  const suggestedType = canonical?.slice_type ?? canonical?.service_type;

  return {
    requestedType,
    requestedLatency,
    suggestedType,
    suggestedLatency,
    explanation,
  };
}
