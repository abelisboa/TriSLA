import { asMetadata, displayField, type SubmitResponse } from "../../lib/submitResponse";
import { FieldList } from "./FieldList";

type Props = { response: SubmitResponse; heading?: string };

function DomainBlock({ title, data }: { title: string; data: Record<string, unknown> | undefined }) {
  if (!data || typeof data !== "object") {
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
      <FieldList
        fields={Object.entries(data).map(([label, value]) => ({ label, value }))}
      />
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
      <FieldList
        fields={[
          { label: "metadata.telemetry_complete", value: metadata?.telemetry_complete },
          { label: "metadata.telemetry_gaps", value: metadata?.telemetry_gaps },
          { label: "metadata.telemetry_version", value: metadata?.telemetry_version },
        ]}
      />
      {!snap ? (
        <p className="trisla-muted">metadata.telemetry_snapshot: Not available</p>
      ) : (
        <>
          <FieldList
            fields={[
              { label: "execution_id", value: snap.execution_id },
              { label: "timestamp", value: snap.timestamp },
              { label: "telemetry_contract_version", value: snap.telemetry_contract_version },
            ]}
          />
          <DomainBlock title="RAN" data={snap.ran as Record<string, unknown> | undefined} />
          <DomainBlock title="Transport" data={snap.transport as Record<string, unknown> | undefined} />
          <DomainBlock title="Core" data={snap.core as Record<string, unknown> | undefined} />
          <details className="trisla-details">
            <summary>metadata.telemetry_snapshot (full JSON)</summary>
            <pre className="trisla-pre-secondary">{displayField(snap)}</pre>
          </details>
        </>
      )}
    </section>
  );
}
