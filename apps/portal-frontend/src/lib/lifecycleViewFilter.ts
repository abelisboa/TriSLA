/**
 * View-layer filtering for /sla-lifecycle — does not modify admissionLifecycleGate.ts.
 * Separates Admission Analysis vs Runtime Lifecycle navigation surfaces (Sprint 10F).
 */

import {
  showLifecycleSection,
  type AdmissionDecision,
  type LifecycleSection,
} from "./admissionLifecycleGate";

export type LifecycleView = "admission" | "runtime";

const ADMISSION_VIEW_SECTIONS: ReadonlySet<LifecycleSection> = new Set([
  "runtimeIdentity",
  "semanticAdmission",
  "serviceProfile",
  "mlDecision",
  "blockchain",
  "runtimeOrchestration",
  "decisionEvidence",
  "governance",
  "blockchain",
  "whyRejected",
  "renegotiationProposal",
  "distributedTrace",
]);

const RUNTIME_VIEW_SECTIONS: ReadonlySet<LifecycleSection> = new Set([
  "runtimeIdentity",
  "runtimeOrchestration",
  "runtimeSnapshot",
  "runtimeAssurance",
  "runtimeCompliance",
  "driftAnalysis",
  "closedLoop",
  "remediation",
  "revalidation",
  "viewRuntimeCta",
]);

/** ACCEPT governance consolidated into Runtime Assurance (runtime view only). */
export function showLifecycleSectionInView(
  section: LifecycleSection,
  decision: AdmissionDecision,
  view: LifecycleView,
): boolean {
  if (!showLifecycleSection(section, decision)) return false;

  if (view === "admission") {
    if (decision === "ACCEPT" && section === "governance") return false;
    return ADMISSION_VIEW_SECTIONS.has(section);
  }

  return RUNTIME_VIEW_SECTIONS.has(section);
}

/** Sidebar Runtime Lifecycle link — visible only for ACCEPT (or before decision is known). */
export function isRuntimeLifecycleNavVisible(decision: AdmissionDecision | null): boolean {
  if (decision === null) return true;
  return decision === "ACCEPT";
}

export function lifecycleViewFromParam(value: string | null): LifecycleView {
  return value === "runtime" ? "runtime" : "admission";
}
