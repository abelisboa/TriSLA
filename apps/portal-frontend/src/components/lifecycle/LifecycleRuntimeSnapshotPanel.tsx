import { displayField } from "../../lib/submitResponse";
import {
  isObservedSnapshotPopulated,
  observedCoreRows,
  observedRanRows,
  observedTransportRows,
  type ObservedTelemetryRow,
} from "../../lib/observedTelemetry";
import { parseTelemetrySnapshot, type TelemetrySnapshotV2 } from "../../lib/lifecycleRuntimeSnapshot";

type Props = {
  snapshot: unknown;
  loading?: boolean;
  error?: string;
};

function DomainSection({
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
      <h4>{title}</h4>
      <dl>
        {rows.map(({ label, value }) => (
          <div key={label} className="trisla-status-row">
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export function LifecycleRuntimeSnapshotPanel({ snapshot, loading, error }: Props) {
  const snap: TelemetrySnapshotV2 | undefined = parseTelemetrySnapshot(snapshot);
  const populated = isObservedSnapshotPopulated({
    ran: snap?.ran,
    transport: snap?.transport,
    core: snap?.core,
  });

  return (
    <section className="trisla-status-card" aria-label="Runtime Snapshot">
      <h2>Multidomain Telemetry</h2>
      <p className="trisla-muted">
        Observed runtime metrics only — compliance evaluation is shown separately.
      </p>
      {loading && <p className="trisla-muted">Loading runtime snapshot…</p>}
      {error && <p className="trisla-error">{error}</p>}
      {!loading && !error && !populated && (
        <p className="trisla-muted">Runtime snapshot not available for this intent.</p>
      )}
      {!loading && !error && populated && snap && (
        <>
          <dl>
            <div className="trisla-status-row">
              <dt>execution_id</dt>
              <dd>{displayField(snap.execution_id)}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>timestamp</dt>
              <dd>{displayField(snap.timestamp)}</dd>
            </div>
          </dl>
          <DomainSection title="RAN" rows={observedRanRows(snap.ran)} />
          <DomainSection title="Transport" rows={observedTransportRows(snap.transport)} />
          <DomainSection title="CORE" rows={observedCoreRows(snap.core)} />
        </>
      )}
    </section>
  );
}
