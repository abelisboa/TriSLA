import { asMetadata, type SubmitResponse } from "./submitResponse";

/** GET /api/v1/sla/status/{intent_id} — audited fields only. */
export type SlaRuntimeStatusResponse = {
  sla_id?: string;
  status?: string;
  tenant_id?: string;
  intent_id?: string;
  nest_id?: string | null;
  created_at?: string;
  updated_at?: string | null;
  telemetry_snapshot?: Record<string, unknown>;
  runtime_assurance?: {
    state?: string;
    assurance_state?: string;
    drift_detected?: boolean;
    recommendation?: string;
    last_evaluation?: string;
    bottleneck_domain?: string;
  };
};

/** POST /api/v1/sla/revalidate-telemetry — audited response shape. */
export type RevalidateTelemetryResponse = {
  intent_id?: string;
  execution_id_revalidation?: string;
  telemetry_snapshot_atual?: Record<string, unknown>;
  timestamps_utc?: Record<string, unknown>;
  drift_summary?: {
    compared?: boolean;
    deltas?: Array<{
      path?: string;
      reference?: number;
      current?: number;
      delta?: number;
    }>;
    fields_compared?: number;
    reason?: string;
  };
  revalidation_status?: string;
  temporal_correlation?: Record<string, unknown>;
  metadata?: {
    remediation_evidence?: Record<string, unknown>;
    delegated_to_sla_agent?: boolean;
    delegation_target?: string;
    delegation_fallback_reason?: string;
  };
};

export type RevalidateTelemetryRequest = {
  intent_id: string;
  reference_telemetry_snapshot?: Record<string, unknown>;
  temporal_intent_trace?: Record<string, unknown>;
  correlation_execution_id?: string;
};

export function intentIdFromSubmit(response: SubmitResponse): string | undefined {
  const id = response.intent_id;
  return typeof id === "string" && id.trim() ? id : undefined;
}

export function referenceTelemetryFromSubmit(
  response: SubmitResponse,
): Record<string, unknown> | undefined {
  const metadata = asMetadata(response);
  const snap = metadata?.telemetry_snapshot;
  return snap && typeof snap === "object" ? (snap as Record<string, unknown>) : undefined;
}

export function lifecycleStateFromSubmit(response: SubmitResponse): unknown {
  return asMetadata(response)?.lifecycle_state;
}

export function buildRevalidateRequest(response: SubmitResponse): RevalidateTelemetryRequest | null {
  const intent_id = intentIdFromSubmit(response);
  if (!intent_id) return null;

  const metadata = asMetadata(response);
  const body: RevalidateTelemetryRequest = { intent_id };

  const reference = referenceTelemetryFromSubmit(response);
  if (reference) body.reference_telemetry_snapshot = reference;

  const trace = metadata?.temporal_intent_trace;
  if (trace && typeof trace === "object") {
    body.temporal_intent_trace = trace as Record<string, unknown>;
  }

  const execId = metadata?.execution_id;
  if (typeof execId === "string" && execId.trim()) {
    body.correlation_execution_id = execId;
  }

  return body;
}
