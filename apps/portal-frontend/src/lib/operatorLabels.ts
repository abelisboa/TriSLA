/** Operator-facing labels for real API contract fields (payload keys unchanged). */

import { displayLocalGovernanceRegistration } from "./governanceDisplayLabels";

export const TENANT_ID_HELP =
  "Unique identifier supplied by the requesting organization.";

export const TEMPLATE_ID_HELP =
  "Template reference identifier for this SLA submission.";

export const AWAITING_DATA = "Loading service data…";

export const SERVICE_UNAVAILABLE = "Service data not available";

export const PLATFORM_SERVICE_LABELS: Record<string, string> = {
  GLOBAL_HEALTH: "Platform Health",
  NASP_DIAGNOSTICS: "NASP Diagnostics",
  PROMETHEUS_SUMMARY: "Monitoring Service",
  SLA_SUBMIT: "Admission Service",
  SLA_INTERPRET: "Interpretation Service",
};

export const NASP_MODULE_LABELS: Record<string, string> = {
  sem_csmf: "Semantic Interpretation",
  ml_nsmf: "ML Analytics",
  decision: "Decision Engine",
  bc_nssmf: "BC-NSSMF (service health)",
  sla_agent: "SLA Agent",
};

const LIFECYCLE_EVENT_LABELS: Record<string, string> = {
  BLOCKCHAIN_COMMITTED: "On-chain commit milestone",
  BLOCKCHAIN_REGISTERED: "Local governance record milestone",
  PIPELINE_INGESTED: "Runtime Monitoring — Active",
  COMPLETED: "Completed",
  REGISTERED: "Registered",
  ACCEPT: "Admission — Accepted",
  INGESTED: "Ingested",
};

const LIFECYCLE_STATE_LABELS: Record<string, string> = {
  ACTIVE: "Active",
  PENDING_RENEGOTIATION: "Pending Renegotiation",
  TERMINATED: "Terminated",
  COMPLETED: "Completed",
  REGISTERED: "Registered",
  ACCEPT: "Accepted",
  ACCEPTED: "Accepted",
  BLOCKCHAIN_REGISTERED: "Local record assigned",
  BLOCKCHAIN_COMMITTED: "On-chain committed",
};

const BLOCKCHAIN_STATUS_LABELS: Record<string, string> = {
  COMMITTED: "Committed on-chain",
  BLOCKCHAIN_REGISTERED: "Local record assigned",
  BLOCKCHAIN_COMMITTED: "Committed on-chain",
  OK: "Committed on-chain",
  FAILED: "Unavailable",
};

/** Maps API / metadata keys to operator-readable labels in UI only. */
export function operatorFieldLabel(key: string): string {
  const map: Record<string, string> = {
    tenant_id: "Tenant ID",
    template_id: "Template ID",
    tx_hash: "Transaction hash",
    blockchain_tx_hash: "Blockchain transaction hash",
    bc_status: "On-chain commit status",
    block_number: "Block number",
    blockchain_status: "On-chain commit status",
    lifecycle_state: "Lifecycle status",
    intent_id: "Intent ID",
    nest_id: "NEST ID",
    service_type: "Service type",
    slice_type: "Slice type",
    sla_id: "SLA ID",
    created_at: "Created at",
    input_text: "Request text",
    "input_text (request)": "Request text",
    "metadata.lifecycle_state (submit)": "Lifecycle status (submit)",
    "metadata.lifecycle_state": "Lifecycle status",
    "metadata.governance_event": "Governance event",
    "metadata.governance_event_id": "Governance event ID",
    "metadata.governance_registration_status": "Local governance registration",
    "metadata.telemetry_complete": "Telemetry complete",
    "metadata.telemetry_gaps": "Telemetry gaps",
    "metadata.telemetry_version": "Telemetry version",
    "metadata.telemetry_snapshot": "Telemetry snapshot",
    "metadata.decision_score": "Decision score",
    "metadata.decision_mode": "Decision mode",
    "metadata.policy_result": "Policy result",
    "metadata.decision_band": "Decision band",
    "metadata.final_decision": "Final decision",
    "metadata.threshold_decision": "Threshold decision",
    sla_requirements: "SLA requirements",
    technical_parameters: "Technical parameters",
    governance_event: "Admission decision record",
    governance_event_id: "Governance event ID",
    registration_status: "Local governance registration",
    "registration_status (metadata.governance_registration_status)":
      "Local governance registration",
  };
  return map[key] ?? key.replace(/^metadata\./, "").replace(/_/g, " ");
}

export function formatLifecycleEventLabel(event: string): string {
  return LIFECYCLE_EVENT_LABELS[event] ?? event.replace(/_/g, " ");
}

export function formatLifecycleStateLabel(state: unknown): string {
  if (state === null || state === undefined || state === "") return "Not available";
  const key = String(state).trim();
  return LIFECYCLE_STATE_LABELS[key] ?? key.replace(/_/g, " ");
}

export function formatBlockchainStatusLabel(status: unknown): string {
  if (status === null || status === undefined || status === "") return "Not available";
  const key = String(status).trim().toUpperCase();
  if (key === "REGISTERED" || key === "DEGRADED_FALLBACK" || key === "REGISTERED_LEGACY") {
    return displayLocalGovernanceRegistration(status);
  }
  return BLOCKCHAIN_STATUS_LABELS[key] ?? String(status).replace(/_/g, " ");
}

export function formatNaspModuleLabel(key: string): string {
  return NASP_MODULE_LABELS[key] ?? key.replace(/_/g, " ");
}

export function formatRegistrationStatusLabel(status: unknown): string {
  return displayLocalGovernanceRegistration(status);
}
