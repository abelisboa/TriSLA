/** Runtime assurance display helpers — Sprint 5M4 */

export type RuntimeAssuranceState =
  | "COMPLIANT"
  | "WARNING"
  | "AT_RISK"
  | "VIOLATED";

export type RuntimeAssurancePayload = {
  state?: RuntimeAssuranceState;
  assurance_state?: RuntimeAssuranceState;
  violations?: string[];
  warnings?: string[];
  drift_detected?: boolean;
  recommendation?: string;
  last_evaluation?: string;
  sla_compliance?: number;
  bottleneck_domain?: string;
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
    default:
      return "trisla-assurance-unknown";
  }
}

export function isRuntimeAssurancePopulated(payload: RuntimeAssurancePayload | undefined): boolean {
  if (!payload) return false;
  return Boolean(payload.state ?? payload.assurance_state);
}
