/**
 * Phase Next — Consistency fields (read-only binding helpers).
 * No local decision logic; display backend values only.
 */

import type { RuntimeAssurancePayload } from "./runtimeAssurance";
import { asMetadata, type SubmitResponse } from "./submitResponse";

export type DecisionEvidenceRow = {
  metric?: string;
  observed?: number | string;
  threshold?: number | string;
  delta?: number | string | null;
  rule?: string;
  unit?: string;
};

export type GovernanceClarityPayload = {
  governance_event?: {
    label?: string;
    status?: string;
    event_type?: string;
    governance_event_id?: string | null;
  };
  blockchain_registration?: {
    label?: string;
    status?: string;
    executed?: boolean;
    reason?: string;
    bc_status?: string;
  };
};

export type TelemetryFidelityRow = {
  kpi?: string;
  admission_value?: unknown;
  runtime_value?: unknown;
  unit?: string;
  consistent?: boolean;
};

export type TelemetryFidelityPayload = {
  kpi_rows?: TelemetryFidelityRow[];
  mismatch_count?: number;
  consistent?: boolean;
};

export type ClosedLoopPayload = {
  observe?: boolean;
  detect?: boolean;
  evaluate?: boolean;
  act?: boolean;
  revalidate?: boolean;
  mode?: string;
};

export type RemediationAttemptRow = {
  detected?: string;
  action?: string;
  domain?: string;
  result?: string;
  simulation?: boolean;
  revalidation_delta_compliance?: number | null;
  evidence?: Record<string, unknown>;
};

export function parseDecisionEvidence(raw: unknown): DecisionEvidenceRow[] {
  if (!Array.isArray(raw)) return [];
  return raw.filter((x) => x && typeof x === "object") as DecisionEvidenceRow[];
}

export function decisionEvidenceFromSubmit(response: SubmitResponse): DecisionEvidenceRow[] {
  const md = asMetadata(response);
  return parseDecisionEvidence(md?.decision_evidence);
}

export function governanceClarityFromAssurance(
  assurance: RuntimeAssurancePayload | undefined,
): GovernanceClarityPayload | undefined {
  const gc = assurance?.governance_clarity;
  return gc && typeof gc === "object" ? (gc as GovernanceClarityPayload) : undefined;
}

export function governanceClarityFromSubmit(response: SubmitResponse): GovernanceClarityPayload | undefined {
  const md = asMetadata(response);
  const direct = md?.governance_clarity;
  if (direct && typeof direct === "object") return direct as GovernanceClarityPayload;
  const ra = md?.runtime_assurance;
  if (ra && typeof ra === "object") {
    return governanceClarityFromAssurance(ra as RuntimeAssurancePayload);
  }
  return undefined;
}

export function telemetryFidelityFromAssurance(
  assurance: RuntimeAssurancePayload | undefined,
): TelemetryFidelityPayload | undefined {
  const tf = assurance?.telemetry_fidelity;
  return tf && typeof tf === "object" ? (tf as TelemetryFidelityPayload) : undefined;
}

export function closedLoopFromAssurance(
  assurance: RuntimeAssurancePayload | undefined,
): ClosedLoopPayload | undefined {
  const cl = assurance?.closed_loop;
  return cl && typeof cl === "object" ? (cl as ClosedLoopPayload) : undefined;
}

export function remediationAttemptsFromAssurance(
  assurance: RuntimeAssurancePayload | undefined,
): RemediationAttemptRow[] {
  const raw = assurance?.remediation_attempts;
  if (!Array.isArray(raw)) return [];
  return raw.filter((x) => x && typeof x === "object") as RemediationAttemptRow[];
}

/** Backend operational_status only — no frontend inference. */
export function operationalStatusFromAssurance(
  assurance: RuntimeAssurancePayload | undefined,
): string | undefined {
  const op = assurance?.operational_status;
  return typeof op === "string" && op.trim() ? op.trim() : undefined;
}

export function formatComplianceDisplay(
  value: number | undefined,
  opts?: { alreadyPercent?: boolean },
): string {
  if (value === undefined || value === null || Number.isNaN(value)) return "Not available";
  if (opts?.alreadyPercent || value > 1.0) {
    return `${Number(value).toFixed(value % 1 === 0 ? 0 : 2)}%`;
  }
  return `${Math.round(value * 100)}%`;
}

export function formatDelta(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const n = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(n)) return String(value);
  const sign = n > 0 ? "+" : "";
  return `${sign}${n}`;
}

export function fidelityStatusLabel(consistent: boolean | undefined): string {
  if (consistent === true) return "CONSISTENT";
  if (consistent === false) return "UPDATED SNAPSHOT";
  return "Not available";
}

export function detectedLabel(ruleId: string | undefined): string {
  if (!ruleId) return "Not available";
  if (ruleId.includes("prb")) return "PRB saturation";
  if (ruleId.includes("transport")) return "Transport degradation";
  if (ruleId.includes("core")) return "Core resource pressure";
  return ruleId.replace(/-/g, " ");
}
