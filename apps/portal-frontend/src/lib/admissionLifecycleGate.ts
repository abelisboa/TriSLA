/**
 * Runtime Lifecycle Gating — single UI matrix (dissertation architecture).
 * Decision SSOT: status API fields only — never sessionStorage.
 */

import type { SlaRuntimeStatusResponse } from "./runtimeSupervision";
import type { DecisionEvidenceRow } from "./phaseNextConsistency";

export type AdmissionDecision = "ACCEPT" | "REJECT" | "RENEGOTIATE" | "UNKNOWN";

export type LifecycleSection =
  | "runtimeIdentity"
  | "semanticAdmission"
  | "mlDecision"
  | "blockchain"
  | "runtimeOrchestration"
  | "decisionEvidence"
  | "governance"
  | "whyRejected"
  | "renegotiationProposal"
  | "runtimeSnapshot"
  | "runtimeAssurance"
  | "runtimeCompliance"
  | "driftAnalysis"
  | "closedLoop"
  | "remediation"
  | "revalidation"
  | "viewRuntimeCta"
  | "distributedTrace";

const ACCEPT_SECTIONS: ReadonlySet<LifecycleSection> = new Set([
  "runtimeIdentity",
  "semanticAdmission",
  "mlDecision",
  "blockchain",
  "runtimeOrchestration",
  "decisionEvidence",
  "governance",
  "runtimeSnapshot",
  "runtimeAssurance",
  "runtimeCompliance",
  "driftAnalysis",
  "closedLoop",
  "remediation",
  "revalidation",
  "viewRuntimeCta",
  "distributedTrace",
]);

const REJECT_SECTIONS: ReadonlySet<LifecycleSection> = new Set([
  "runtimeIdentity",
  "semanticAdmission",
  "mlDecision",
  "decisionEvidence",
  "governance",
  "whyRejected",
  "distributedTrace",
]);

const RENEGOTIATE_SECTIONS: ReadonlySet<LifecycleSection> = new Set([
  "runtimeIdentity",
  "semanticAdmission",
  "mlDecision",
  "decisionEvidence",
  "governance",
  "renegotiationProposal",
  "distributedTrace",
]);

export function normalizeAdmissionDecision(value: unknown): AdmissionDecision {
  const key = String(value ?? "").trim().toUpperCase();
  if (key === "ACCEPT" || key === "REJECT" || key === "RENEGOTIATE") return key;
  if (key === "AC") return "ACCEPT";
  if (key === "REJ") return "REJECT";
  if (key === "RENEG") return "RENEGOTIATE";
  return "UNKNOWN";
}

/** Official decision from GET /sla/status only. */
export function admissionDecisionFromStatus(
  status?: SlaRuntimeStatusResponse | null,
): AdmissionDecision {
  if (!status) return "UNKNOWN";
  const direct = normalizeAdmissionDecision(status.admission_decision);
  if (direct !== "UNKNOWN") return direct;
  const fromSummary = normalizeAdmissionDecision(status.operational_summary?.admission_decision);
  if (fromSummary !== "UNKNOWN") return fromSummary;
  if (status.runtime_lifecycle_enabled === true) return "ACCEPT";
  return "UNKNOWN";
}

export function isRuntimeLifecycleEnabled(status?: SlaRuntimeStatusResponse | null): boolean {
  if (status?.runtime_lifecycle_enabled === true) return true;
  if (status?.runtime_lifecycle_enabled === false) return false;
  return admissionDecisionFromStatus(status) === "ACCEPT";
}

export function sectionsForDecision(decision: AdmissionDecision): ReadonlySet<LifecycleSection> {
  if (decision === "ACCEPT") return ACCEPT_SECTIONS;
  if (decision === "REJECT") return REJECT_SECTIONS;
  if (decision === "RENEGOTIATE") return RENEGOTIATE_SECTIONS;
  return REJECT_SECTIONS;
}

export function showLifecycleSection(
  section: LifecycleSection,
  decision: AdmissionDecision,
): boolean {
  return sectionsForDecision(decision).has(section);
}

export function admissionBannerMessage(decision: AdmissionDecision): string | null {
  if (decision === "REJECT") {
    return "Runtime supervision is not applicable — this SLA was rejected at admission (T₀ evidence only).";
  }
  if (decision === "RENEGOTIATE") {
    return "Runtime cycle begins only after a renegotiated SLA is accepted.";
  }
  return null;
}

export function parseStatusDecisionEvidence(
  status?: SlaRuntimeStatusResponse | null,
): DecisionEvidenceRow[] {
  const raw = status?.admission_decision_evidence;
  if (!Array.isArray(raw)) return [];
  return raw.filter((x) => x && typeof x === "object") as DecisionEvidenceRow[];
}

export function operationalStatusLabel(decision: AdmissionDecision): string {
  if (decision === "ACCEPT") return "ACTIVE";
  if (decision === "RENEGOTIATE") return "PENDING_RENEGOTIATION";
  if (decision === "REJECT") return "TERMINATED";
  return "UNKNOWN";
}
