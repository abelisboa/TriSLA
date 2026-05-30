/** Operator-facing labels for real API contract fields (payload keys unchanged). */

export const TENANT_ID_HELP =
  "Unique identifier supplied by the requesting organization.";

export const TEMPLATE_ID_HELP =
  "Template reference identifier for this SLA submission.";

export const AWAITING_DATA = "Loading service data…";

export const SERVICE_UNAVAILABLE = "Service data not available";

export const PLATFORM_SERVICE_LABELS: Record<string, string> = {
  GLOBAL_HEALTH: "Global health service",
  NASP_DIAGNOSTICS: "NASP diagnostics",
  PROMETHEUS_SUMMARY: "Monitoring summary",
  SLA_SUBMIT: "SLA submission",
  SLA_INTERPRET: "SLA interpretation",
};

/** Maps API / metadata keys to operator-readable labels in UI only. */
export function operatorFieldLabel(key: string): string {
  const map: Record<string, string> = {
    tenant_id: "Tenant ID",
    template_id: "Template ID",
    tx_hash: "Transaction hash",
    blockchain_tx_hash: "Blockchain transaction hash",
    bc_status: "Blockchain status",
    block_number: "Block number",
    blockchain_status: "Blockchain status",
    lifecycle_state: "Lifecycle state",
    intent_id: "Intent ID",
    nest_id: "NEST ID",
    service_type: "Service type",
    slice_type: "Slice type",
    sla_id: "SLA ID",
    created_at: "Created at",
    input_text: "Request text",
    "input_text (request)": "Request text",
    "metadata.lifecycle_state (submit)": "Lifecycle state (submit)",
    "metadata.lifecycle_state": "Lifecycle state",
    "metadata.governance_event": "Governance event",
    "metadata.governance_event_id": "Governance event ID",
    "metadata.governance_registration_status": "Registration status",
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
  };
  return map[key] ?? key.replace(/^metadata\./, "").replace(/_/g, " ");
}
