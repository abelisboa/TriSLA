import { displayField } from "../../lib/submitResponse";
import type { SubmitResponse } from "../../lib/submitResponse";
import {
  buildGovernancePayloadSnapshot,
  governanceEventFromSubmit,
  registrationStatusFromSubmit,
} from "../../lib/governanceEvidence";
import {
  formatBlockchainStatusLabel,
  formatLifecycleEventLabel,
  formatLifecycleStateLabel,
  formatRegistrationStatusLabel,
  operatorFieldLabel,
} from "../../lib/operatorLabels";
import { formatOperatorMetric } from "../../lib/operatorFormat";
import { GOVERNANCE_TOOLTIPS } from "../../lib/governanceDisplayLabels";
import { FieldList } from "../submit-payload/FieldList";

export function GovernanceOverviewPanel({ response }: { response: SubmitResponse }) {
  const metadata = response.metadata as Record<string, unknown> | undefined;
  const governanceEvent = governanceEventFromSubmit(response);
  const governanceEventId =
    metadata?.governance_event_id ??
    (governanceEvent?.governance_event_id as unknown);
  const registrationStatus = registrationStatusFromSubmit(response);
  const eventRaw =
    governanceEvent?.event ??
    governanceEvent?.governance_event_type ??
    governanceEvent?.lifecycle_event_type;
  const eventLabel =
    eventRaw != null
      ? formatLifecycleEventLabel(String(eventRaw))
      : governanceEvent
        ? "Governance event recorded"
        : "Not available";

  return (
    <section className="trisla-governance-subsection" aria-label="Governance Overview">
      <h3>Governance Overview</h3>
      <FieldList
        fields={[
          {
            label: operatorFieldLabel("governance_event"),
            value: eventLabel,
          },
          {
            label: operatorFieldLabel("governance_event_id"),
            value: governanceEventId,
          },
          {
            label: operatorFieldLabel("registration_status"),
            value: formatRegistrationStatusLabel(registrationStatus),
          },
          {
            label: operatorFieldLabel("bc_status"),
            value: formatBlockchainStatusLabel(response.bc_status),
          },
        ]}
      />
      {governanceEvent && (
        <details className="trisla-details">
          <summary>Technical Details — governance event</summary>
          <FieldList
            fields={Object.entries(governanceEvent).map(([label, value]) => ({
              label: operatorFieldLabel(label),
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
        fields={[
          {
            label: operatorFieldLabel("lifecycle_state"),
            value: formatLifecycleStateLabel(lifecycleState),
          },
        ]}
      />
      {entries.length === 0 ? (
        <p className="trisla-muted">Lifecycle events not yet reported.</p>
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
                  <td>{formatLifecycleEventLabel(event)}</td>
                  <td>{displayField(timestamp)}</td>
                  <td>{formatLifecycleStateLabel(lifecycleState)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <details className="trisla-details">
        <summary>Technical Details — lifecycle identifiers</summary>
        <FieldList
          fields={[
            { label: operatorFieldLabel("metadata.lifecycle_state"), value: lifecycleState },
            ...entries.map(([event, timestamp]) => ({
              label: event,
              value: timestamp,
            })),
          ]}
        />
      </details>
    </section>
  );
}

export function RegistrationEvidencePanel({ response }: { response: SubmitResponse }) {
  const metadata = response.metadata as Record<string, unknown> | undefined;
  const txHash = response.tx_hash ?? response.blockchain_tx_hash;
  const latency = response.blockchain_transaction_latency_ms;

  return (
    <section className="trisla-governance-subsection" aria-label="Local registration and on-chain evidence">
      <h3>Local registration &amp; on-chain evidence</h3>
      <p className="trisla-muted" title={GOVERNANCE_TOOLTIPS.localGovernance}>
        Local BC-NSSMF lineage and per-SLA on-chain commit fields from the submission response.
      </p>
      <FieldList
        fields={[
          {
            label: operatorFieldLabel("registration_status"),
            value: formatRegistrationStatusLabel(metadata?.governance_registration_status),
          },
          {
            label: operatorFieldLabel("bc_status"),
            value: formatBlockchainStatusLabel(response.bc_status),
          },
          {
            label: operatorFieldLabel("blockchain_status"),
            value: formatBlockchainStatusLabel(response.blockchain_status),
          },
          {
            label: "Registry latency",
            value:
              latency != null
                ? formatOperatorMetric("Transport Latency", latency)
                : "Not available",
          },
        ]}
      />
      <details className="trisla-details">
        <summary>Technical Details — blockchain and registration payload</summary>
        <FieldList
          fields={[
            {
              label: operatorFieldLabel("registration_status"),
              value: metadata?.governance_registration_status,
            },
            {
              label: operatorFieldLabel("metadata.governance_registration_fallback"),
              value: metadata?.governance_registration_fallback,
            },
            {
              label: operatorFieldLabel("metadata.governance_registration_fallback_reason"),
              value: metadata?.governance_registration_fallback_reason,
            },
            { label: operatorFieldLabel("tx_hash"), value: txHash },
            { label: operatorFieldLabel("block_number"), value: response.block_number },
            { label: operatorFieldLabel("bc_status"), value: response.bc_status },
            { label: operatorFieldLabel("blockchain_status"), value: response.blockchain_status },
          ]}
        />
      </details>
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
      <p className="trisla-muted">Traceability identifiers from the submission response.</p>
      <FieldList
        fields={[
          { label: operatorFieldLabel("governance_event_id"), value: governanceEventId },
          { label: operatorFieldLabel("intent_id"), value: response.intent_id },
          { label: "Execution ID", value: executionId },
          { label: "Trace ID", value: traceId },
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
        <summary>Technical Details — governance payload (JSON)</summary>
        <pre className="trisla-pre-secondary">{JSON.stringify(snapshot, null, 2)}</pre>
      </details>
    </section>
  );
}
