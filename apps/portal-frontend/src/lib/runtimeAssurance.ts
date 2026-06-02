/** Runtime assurance display helpers — Sprint 5M4 */

export type RuntimeAssuranceState =
  | "COMPLIANT"
  | "WARNING"
  | "AT_RISK"
  | "VIOLATED"
  | "INCOMPLETE";

export type DriftIndicatorPayload = {
  path?: string;
  reference?: number;
  current?: number;
  delta?: number;
};

export type RuntimeAssurancePayload = {
  state?: RuntimeAssuranceState | string;
  assurance_state?: RuntimeAssuranceState | string;
  operational_status?: string;
  violations?: string[];
  warnings?: string[];
  drift_detected?: boolean;
  drift_indicators?: DriftIndicatorPayload[];
  recommendation?: string;
  last_evaluation?: string;
  slice_type?: string;
  sla_compliance?: number;
  admission_compliance?: number;
  admission_compliance_percent?: number;
  runtime_compliance?: number;
  runtime_compliance_percent?: number;
  bottleneck_domain?: string;
  decision_evidence?: Array<Record<string, unknown>>;
  telemetry_fidelity?: Record<string, unknown>;
  governance_clarity?: Record<string, unknown>;
  closed_loop?: Record<string, unknown>;
  remediation_attempts?: Array<Record<string, unknown>>;
  domain_compliance?: {
    ran?: number;
    transport?: number;
    core?: number;
  };
  domain_explainability?: {
    ran?: Array<Record<string, unknown>>;
    transport?: Array<Record<string, unknown>>;
    core?: Array<Record<string, unknown>>;
  };
};

export function parseRuntimeAssurance(raw: unknown): RuntimeAssurancePayload | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  return raw as RuntimeAssurancePayload;
}

export function assuranceStateLabel(payload: RuntimeAssurancePayload | undefined): string {
  const state = payload?.state ?? payload?.assurance_state;
  if (!state) return "Not available";
  return state.replace(/_/g, " ");
}

export function assuranceStateClass(state: string | undefined): string {
  switch (state) {
    case "COMPLIANT":
      return "trisla-assurance-compliant";
    case "WARNING":
      return "trisla-assurance-warning";
    case "AT_RISK":
      return "trisla-assurance-at-risk";
    case "VIOLATED":
      return "trisla-assurance-violated";
    case "INCOMPLETE":
      return "trisla-assurance-incomplete";
    case "PENDING_RENEGOTIATION":
      return "trisla-assurance-warning";
    case "TERMINATED":
      return "trisla-assurance-violated";
    default:
      return "trisla-assurance-unknown";
  }
}

export function isRuntimeAssurancePopulated(payload: RuntimeAssurancePayload | undefined): boolean {
  if (!payload) return false;
  return Boolean(payload.state ?? payload.assurance_state);
}
