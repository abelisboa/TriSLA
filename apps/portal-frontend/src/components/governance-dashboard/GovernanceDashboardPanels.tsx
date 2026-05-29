import { displayField } from "../../lib/submitResponse";
import type { SubmitResponse } from "../../lib/submitResponse";
import {
  buildGovernancePayloadSnapshot,
  governanceEventFromSubmit,
  registrationStatusFromSubmit,
} from "../../lib/governanceEvidence";
import { FieldList } from "../submit-payload/FieldList";

export function GovernanceOverviewPanel({ response }: { response: SubmitResponse }) {
  const metadata = response.metadata as Record<string, unknown> | undefined;
  const governanceEvent = governanceEventFromSubmit(response);
  const governanceEventId =
    metadata?.governance_event_id ??
    (governanceEvent?.governance_event_id as unknown);

  return (
    <section className="trisla-governance-subsection" aria-label="Governance Overview">
      <h3>Governance Overview</h3>
      <FieldList
        fields={[
          { label: "governance_event", value: governanceEvent },
          { label: "governance_event_id", value: governanceEventId },
          {
            label: "registration_status (metadata.governance_registration_status)",
            value: registrationStatusFromSubmit(response),
          },
          { label: "bc_status", value: response.bc_status },
        ]}
      />
      {governanceEvent && (
        <details className="trisla-details">
          <summary>governance_event fields</summary>
          <FieldList
            fields={Object.entries(governanceEvent).map(([label, value]) => ({
              label,
              value,
            }))}
          />
        </details>
      )}
    </section>
  );
}

export function LifecycleTimelinePanel({ response }: { response: SubmitResponse }) {
  const metadata = response.metadata as Record<string, unknown> | undefined;
  const slaLifecycle = metadata?.sla_lifecycle;
  const lifecycleState = metadata?.lifecycle_state;
  const entries =
    slaLifecycle && typeof slaLifecycle === "object"
      ? Object.entries(slaLifecycle as Record<string, unknown>)
      : [];

  return (
    <section className="trisla-governance-subsection" aria-label="Lifecycle Timeline">
      <h3>Lifecycle Timeline</h3>
      <FieldList
        fields={[{ label: "metadata.lifecycle_state", value: lifecycleState }]}
      />
      {entries.length === 0 ? (
        <p className="trisla-muted">metadata.sla_lifecycle: Not available</p>
      ) : (
        <div className="trisla-table-wrap">
          <table className="trisla-simple-table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Timestamp</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {entries.map(([event, timestamp]) => (
                <tr key={event}>
                  <td>{displayField(event)}</td>
                  <td>{displayField(timestamp)}</td>
                  <td>{displayField(lifecycleState)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export function RegistrationEvidencePanel({ response }: { response: SubmitResponse }) {
  const metadata = response.metadata as Record<string, unknown> | undefined;

  return (
    <section className="trisla-governance-subsection" aria-label="Registration Evidence">
      <h3>Registration Evidence</h3>
      <p className="trisla-muted">Governance Registration State — values as returned, no inference.</p>
      <FieldList
        fields={[
          {
            label: "registration_status (metadata.governance_registration_status)",
            value: metadata?.governance_registration_status,
          },
          { label: "bc_status", value: response.bc_status },
          {
            label: "metadata.governance_registration_fallback",
            value: metadata?.governance_registration_fallback,
          },
          {
            label: "metadata.governance_registration_fallback_reason",
            value: metadata?.governance_registration_fallback_reason,
          },
          { label: "blockchain_status", value: response.blockchain_status },
          {
            label: "blockchain_transaction_latency_ms",
            value: response.blockchain_transaction_latency_ms,
          },
          { label: "tx_hash", value: response.tx_hash ?? response.blockchain_tx_hash },
          { label: "block_number", value: response.block_number },
        ]}
      />
    </section>
  );
}

export function AuditabilityMetadataPanel({ response }: { response: SubmitResponse }) {
  const metadata = response.metadata as Record<string, unknown> | undefined;
  const governanceEvent = governanceEventFromSubmit(response);
  const governanceEventId =
    metadata?.governance_event_id ??
    (governanceEvent?.governance_event_id as unknown);
  const executionId =
    metadata?.execution_id ??
    (metadata?.temporal_intent_trace &&
    typeof metadata.temporal_intent_trace === "object"
      ? (metadata.temporal_intent_trace as Record<string, unknown>).execution_id
      : undefined);
  const traceId =
    metadata?.trace_id ??
    (metadata?.temporal_intent_trace &&
    typeof metadata.temporal_intent_trace === "object"
      ? (metadata.temporal_intent_trace as Record<string, unknown>).trace_id
      : undefined);

  return (
    <section className="trisla-governance-subsection" aria-label="Auditability Metadata">
      <h3>Auditability Metadata</h3>
      <p className="trisla-muted">Traceability — only fields present in submit response.</p>
      <FieldList
        fields={[
          { label: "governance_event_id", value: governanceEventId },
          { label: "intent_id", value: response.intent_id },
          { label: "execution_id", value: executionId },
          { label: "trace_id", value: traceId },
        ]}
      />
    </section>
  );
}

export function GovernancePayloadPanel({ response }: { response: SubmitResponse }) {
  const snapshot = buildGovernancePayloadSnapshot(response);

  return (
    <section className="trisla-governance-subsection" aria-label="Governance Payload">
      <details className="trisla-details">
        <summary>Show Governance Payload</summary>
        <pre className="trisla-pre-secondary">{JSON.stringify(snapshot, null, 2)}</pre>
      </details>
    </section>
  );
}
