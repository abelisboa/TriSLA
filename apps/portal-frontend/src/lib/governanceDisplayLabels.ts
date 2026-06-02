/**
 * Sprint 10G.2 — Governance UX labels & tooltips only.
 * Does not alter API fields, gating, or backend semantics.
 *
 * Layers: A = Decision | C = Local registration | D = On-chain commit | E = Service health
 */

export const GOVERNANCE_LAYER_LEGEND =
  "Four layers: admission decision (A), local BC-NSSMF record (C), on-chain commit (D), BC-NSSMF service health (E).";

export const GOVERNANCE_TOOLTIPS = {
  admissionDecision: "Admission decision recorded by the TriSLA governance flow (not an on-chain event).",
  onChainCommit: "Whether a Besu/blockchain transaction was confirmed for this SLA (tx_hash + COMMITTED).",
  onChainNote: "Explains why on-chain commit did or did not occur for this admission decision.",
  localGovernance: "Governance lineage stored by BC-NSSMF; may exist without an on-chain transaction (SSOT FASE 4).",
  bcServiceHealth: "HTTP health of the BC-NSSMF module (NASP probe); not per-SLA commit state.",
  onChainCommitCard: "Per-SLA blockchain commit from NASP pipeline (tx_hash, block number).",
} as const;

/** Clarity panel — display labels (dt). */
export const CLARITY_LABELS = {
  sectionTitle: "Governance & commit status",
  admissionDecision: "Admission decision record",
  onChainCommit: "On-chain commit status",
  blockchainRegistration: "Blockchain Registration",
  note: "Note",
} as const;

/** Map backend clarity strings to operator-facing text (display only). */
export function displayClarityGovernanceStatus(status: unknown): string {
  const s = String(status ?? "").trim();
  if (!s) return "Not available";
  if (s.toLowerCase() === "recorded") return "Logged";
  return s;
}

export function displayClarityEventType(eventType: unknown): string {
  const t = String(eventType ?? "").trim();
  if (t === "Decision Recorded") return "Admission outcome logged";
  return t || "Not available";
}

export function displayClarityBlockchainStatus(status: unknown, executed?: boolean): string {
  if (executed === true) return "Committed on-chain";
  const s = String(status ?? "").trim();
  if (!s) return "Not available";
  const lower = s.toLowerCase();
  if (lower === "pending or failed") return "Not committed on-chain";
  if (lower === "executed") return "Committed on-chain";
  if (lower === "not executed") return "Not applicable for this decision";
  return s;
}

export function displayClarityReason(reason: unknown): string {
  const r = String(reason ?? "").trim();
  if (!r) return "";
  if (r === "ACCEPT without on-chain commit") {
    return "SLA accepted; no Besu transaction confirmed (degraded governance mode).";
  }
  if (r.startsWith("Decision ")) {
    return `${r} — on-chain commit not required.`;
  }
  return r;
}

/** On-chain commit status from bc_status / pipeline codes (layer D). */
export function displayOnChainCommitStatus(status: unknown): string {
  if (status === null || status === undefined || status === "") return "Not available";
  const key = String(status).trim().toUpperCase();
  const map: Record<string, string> = {
    COMMITTED: "Committed on-chain",
    CONFIRMED: "Committed on-chain",
    BLOCKCHAIN_COMMITTED: "Committed on-chain",
    NOT_COMMITTED: "Not committed on-chain",
    BLOCKCHAIN_FAILED: "Commit failed",
    SKIPPED: "Skipped",
    SKIPPED_ORCH_FAILED: "Skipped (orchestration)",
    DEGRADED: "Not committed on-chain",
    ERROR: "Unavailable",
    FAILED: "Commit failed",
    OK: "Committed on-chain",
  };
  return map[key] ?? String(status).replace(/_/g, " ");
}

/** Local governance registration (layer C). */
export function displayLocalGovernanceRegistration(status: unknown): string {
  if (status === null || status === undefined || status === "") return "Not available";
  const key = String(status).trim().toUpperCase();
  const map: Record<string, string> = {
    REGISTERED: "Lineage ID assigned",
    REGISTERED_LEGACY: "Lineage ID assigned (legacy)",
    REGISTERED_WITH_FALLBACK: "Lineage ID assigned (with fallback)",
    DEGRADED_FALLBACK: "Fallback record (no on-chain tx)",
    SKIPPED_NO_ACCEPT: "Skipped (non-ACCEPT decision)",
    SKIPPED_NO_EVENT: "Skipped (no governance event)",
  };
  return map[key] ?? String(status).replace(/_/g, " ");
}
