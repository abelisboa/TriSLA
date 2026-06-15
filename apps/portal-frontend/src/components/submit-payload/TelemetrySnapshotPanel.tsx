import { asMetadata, displayField, type SubmitResponse } from "../../lib/submitResponse";
import { operatorFieldLabel } from "../../lib/operatorLabels";
import {
  filterObservedDomainObject,
  observedCoreRows,
  observedRanRows,
  observedTransportRows,
  OBSERVED_CORE_FIELDS,
  OBSERVED_RAN_FIELDS,
  OBSERVED_TRANSPORT_FIELDS,
  type ObservedTelemetryRow,
} from "../../lib/observedTelemetry";
import { FieldList } from "./FieldList";

type Props = { response: SubmitResponse; heading?: string };

function ObservedDomainBlock({
  title,
  rows,
}: {
  title: string;
  rows: ObservedTelemetryRow[];
}) {
  if (rows.length === 0) {
    return (
      <div className="trisla-status-row">
        <dt>{title}</dt>
        <dd>Not available</dd>
      </div>
    );
  }
  return (
    <div className="trisla-telemetry-domain">
      <h3>{title}</h3>
      <FieldList fields={rows.map((row) => ({ label: row.label, value: row.value }))} />
    </div>
  );
}

export function TelemetrySnapshotPanel({ response, heading = "4. Multidomain Telemetry" }: Props) {
  const metadata = asMetadata(response);
  const snapshot = metadata?.telemetry_snapshot;
  const snap =
    snapshot && typeof snapshot === "object"
      ? (snapshot as Record<string, unknown>)
      : undefined;

  return (
    <section className="trisla-status-card" aria-label="Multidomain Telemetry">
      <h2>{heading}</h2>
      <p className="trisla-muted">
        Observed runtime metrics only — no compliance scores or SLA evaluation.
      </p>
      <FieldList
        fields={[
          { label: operatorFieldLabel("metadata.telemetry_complete"), value: metadata?.telemetry_complete },
          { label: operatorFieldLabel("metadata.telemetry_gaps"), value: metadata?.telemetry_gaps },
        ]}
      />
      {!snap ? (
        <p className="trisla-muted">Telemetry snapshot not available</p>
      ) : (
        <>
          <FieldList
            fields={[
              { label: "execution_id", value: snap.execution_id },
              { label: "timestamp", value: snap.timestamp },
            ]}
          />
          <ObservedDomainBlock title="RAN" rows={observedRanRows(snap.ran)} />
          <ObservedDomainBlock title="Transport" rows={observedTransportRows(snap.transport)} />
          <ObservedDomainBlock title="Core" rows={observedCoreRows(snap.core)} />
          <details className="trisla-details">
            <summary>Technical details — observed telemetry snapshot</summary>
            <pre className="trisla-pre-secondary">
              {displayField({
                execution_id: snap.execution_id,
                timestamp: snap.timestamp,
                telemetry_contract_version: snap.telemetry_contract_version,
                ran: filterObservedDomainObject(
                  snap.ran as Record<string, unknown> | undefined,
                  OBSERVED_RAN_FIELDS,
                ),
                transport: filterObservedDomainObject(
                  snap.transport as Record<string, unknown> | undefined,
                  OBSERVED_TRANSPORT_FIELDS,
                ),
                core: filterObservedDomainObject(
                  snap.core as Record<string, unknown> | undefined,
                  OBSERVED_CORE_FIELDS,
                ),
              })}
            </pre>
          </details>
        </>
      )}
    </section>
  );
}
