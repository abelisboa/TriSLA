import { asMetadata, type SubmitResponse } from "./submitResponse";

const GOVERNANCE_METADATA_KEYS = [
  "governance_event",
  "governance_event_id",
  "governance_event_state",
  "governance_event_type",
  "governance_registration_status",
  "governance_registration_fallback",
  "governance_registration_fallback_reason",
  "governance_authority_source",
  "governance_authority",
  "portal_governance_role",
  "lifecycle_state",
  "sla_lifecycle",
  "lifecycle_event",
  "lifecycle_event_type",
  "lifecycle_transition_reason",
  "lifecycle_authority_source",
  "lifecycle_initial_state",
  "failure_reason",
  "execution_id",
  "temporal_intent_trace",
] as const;

export function governanceEventFromSubmit(response: SubmitResponse): Record<string, unknown> | undefined {
  const metadata = asMetadata(response);
  const event = metadata?.governance_event;
  return event && typeof event === "object" ? (event as Record<string, unknown>) : undefined;
}

export function registrationStatusFromSubmit(response: SubmitResponse): unknown {
  return asMetadata(response)?.governance_registration_status;
}

export function slaLifecycleFromSubmit(
  response: SubmitResponse,
): Record<string, unknown> | undefined {
  const metadata = asMetadata(response);
  const lifecycle = metadata?.sla_lifecycle;
  return lifecycle && typeof lifecycle === "object"
    ? (lifecycle as Record<string, unknown>)
    : undefined;
}

export function lifecycleStateFromSubmit(response: SubmitResponse): unknown {
  return asMetadata(response)?.lifecycle_state;
}

export function intentIdFromSubmit(response: SubmitResponse): unknown {
  return response.intent_id;
}

export function executionIdFromSubmit(response: SubmitResponse): unknown {
  const metadata = asMetadata(response);
  if (metadata?.execution_id != null) return metadata.execution_id;
  const trace = metadata?.temporal_intent_trace;
  if (trace && typeof trace === "object") {
    return (trace as Record<string, unknown>).execution_id;
  }
  return undefined;
}

export function traceIdFromSubmit(response: SubmitResponse): unknown {
  const metadata = asMetadata(response);
  if (metadata?.trace_id != null) return metadata.trace_id;
  const trace = metadata?.temporal_intent_trace;
  if (trace && typeof trace === "object") {
    const tid = (trace as Record<string, unknown>).trace_id;
    if (tid != null) return tid;
  }
  return undefined;
}

export function buildGovernancePayloadSnapshot(response: SubmitResponse): Record<string, unknown> {
  const metadata = asMetadata(response);
  const governanceMetadata: Record<string, unknown> = {};

  if (metadata) {
    for (const key of GOVERNANCE_METADATA_KEYS) {
      if (metadata[key] !== undefined) {
        governanceMetadata[key] = metadata[key];
      }
    }
  }

  return {
    bc_status: response.bc_status,
    tx_hash: response.tx_hash ?? response.blockchain_tx_hash ?? null,
    block_number: response.block_number ?? null,
    blockchain_status: response.blockchain_status,
    blockchain_tx_hash: response.blockchain_tx_hash ?? null,
    blockchain_transaction_latency_ms: response.blockchain_transaction_latency_ms ?? null,
    intent_id: response.intent_id,
    metadata: governanceMetadata,
  };
}

export type LifecycleTimelineRow = {
  event: string;
  timestamp: unknown;
  status: unknown;
};

export function lifecycleTimelineRows(response: SubmitResponse): LifecycleTimelineRow[] {
  const lifecycle = slaLifecycleFromSubmit(response);
  const lifecycleState = lifecycleStateFromSubmit(response);
  if (!lifecycle) return [];

  return Object.entries(lifecycle).map(([event, timestamp]) => ({
    event,
    timestamp,
    status: lifecycleState,
  }));
}
