import type { SubmitResponse } from "./submitResponse";
import { asMetadata } from "./submitResponse";
import { resolveOperationalConfidence } from "./confidenceDisplay";
import {
  decisionEvidenceFromSubmit,
  type DecisionEvidenceRow,
} from "./phaseNextConsistency";

const CACHE_KEY = "trisla_admission_operational_v1";

export type AdmissionOperationalSnapshot = {
  intent_id: string;
  decision?: string;
  bc_status?: string;
  tx_hash?: string;
  block_number?: unknown;
  nest_id?: string;
  ml_confidence?: number | null;
  decision_score?: unknown;
  governance_event_id?: string;
  semantic_validation?: string;
  gst_generated?: string;
  nest_generated?: string;
  semantic_fill?: string;
  trace_id?: string;
  decision_evidence?: DecisionEvidenceRow[];
  admission_compliance_percent?: number;
  admission_telemetry_snapshot?: Record<string, unknown>;
  operational_status?: string;
  distributed_traceability?: {
    trace_id?: string;
    span_id?: string;
    parent_span_id?: string | null;
    correlation_chain?: Array<Record<string, unknown>>;
    end_to_end?: boolean;
  };
  cached_at: string;
};

function readStore(): Record<string, AdmissionOperationalSnapshot> {
  if (typeof window === "undefined") return {};
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, AdmissionOperationalSnapshot>;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function writeStore(store: Record<string, AdmissionOperationalSnapshot>): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(CACHE_KEY, JSON.stringify(store));
}

function asOptionalString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value : undefined;
}

function payloadLabel(metadata: Record<string, unknown> | undefined, key: string): string | undefined {
  if (!metadata) return undefined;
  const direct = asOptionalString(metadata[key]);
  if (direct) return direct;
  const summary = metadata.operational_summary;
  if (summary && typeof summary === "object") {
    return asOptionalString((summary as Record<string, unknown>)[key]);
  }
  return undefined;
}

export function buildAdmissionOperationalSnapshot(
  response: SubmitResponse,
): AdmissionOperationalSnapshot | null {
  const intentId = response.intent_id;
  if (!intentId || typeof intentId !== "string") return null;
  const metadata = asMetadata(response);
  const nestId = response.nest_id ?? metadata?.nest_id;
  const distributedTrace =
    metadata?.distributed_traceability && typeof metadata.distributed_traceability === "object"
      ? (metadata.distributed_traceability as AdmissionOperationalSnapshot["distributed_traceability"])
      : undefined;
  return {
    intent_id: intentId,
    decision: response.decision,
    bc_status: asOptionalString(response.bc_status),
    tx_hash: asOptionalString(response.tx_hash ?? response.blockchain_tx_hash),
    block_number: response.block_number,
    nest_id: typeof nestId === "string" ? nestId : undefined,
    ml_confidence: resolveOperationalConfidence(response),
    decision_score: metadata?.decision_score,
    governance_event_id: asOptionalString(
      metadata?.governance_event_id ??
        (metadata?.governance_event as { governance_event_id?: unknown } | undefined)
          ?.governance_event_id,
    ),
    semantic_validation: payloadLabel(metadata, "semantic_validation"),
    gst_generated: payloadLabel(metadata, "gst_generated"),
    nest_generated: payloadLabel(metadata, "nest_generated"),
    semantic_fill: payloadLabel(metadata, "semantic_fill"),
    trace_id: asOptionalString(metadata?.trace_id ?? distributedTrace?.trace_id),
    decision_evidence: decisionEvidenceFromSubmit(response),
    admission_compliance_percent:
      typeof metadata?.admission_compliance_percent === "number"
        ? metadata.admission_compliance_percent
        : typeof metadata?.admission_compliance === "number"
          ? metadata.admission_compliance <= 1
            ? metadata.admission_compliance * 100
            : metadata.admission_compliance
          : undefined,
    admission_telemetry_snapshot:
      metadata?.telemetry_snapshot && typeof metadata.telemetry_snapshot === "object"
        ? (metadata.telemetry_snapshot as Record<string, unknown>)
        : undefined,
    operational_status: asOptionalString(
      (metadata?.runtime_assurance as { operational_status?: string } | undefined)?.operational_status,
    ),
    distributed_traceability: distributedTrace,
    cached_at: new Date().toISOString(),
  };
}

export function cacheAdmissionOperationalSnapshot(response: SubmitResponse): void {
  const snapshot = buildAdmissionOperationalSnapshot(response);
  if (!snapshot) return;
  const store = readStore();
  store[snapshot.intent_id] = snapshot;
  writeStore(store);
}

export function getAdmissionOperationalSnapshot(
  intentId: string | undefined,
): AdmissionOperationalSnapshot | undefined {
  if (!intentId?.trim()) return undefined;
  return readStore()[intentId.trim()];
}
