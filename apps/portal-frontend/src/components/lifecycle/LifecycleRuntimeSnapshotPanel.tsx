import { displayField } from "../../lib/submitResponse";
import {
  coreRowsForLifecycle,
  isRuntimeSnapshotPopulated,
  parseTelemetrySnapshot,
  ranRowsForLifecycle,
  transportRowsForLifecycle,
  type TelemetrySnapshotV2,
} from "../../lib/lifecycleRuntimeSnapshot";

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
  rows: Array<{ label: string; value: unknown }>;
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
            <dd>{displayField(value)}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export function LifecycleRuntimeSnapshotPanel({ snapshot, loading, error }: Props) {
  const snap: TelemetrySnapshotV2 | undefined = parseTelemetrySnapshot(snapshot);

  return (
    <section className="trisla-status-card" aria-label="Runtime Snapshot">
      <h2>Runtime Snapshot</h2>
      <p className="trisla-muted">Multidomain telemetry from runtime status (contract v2).</p>
      {loading && <p className="trisla-muted">Loading runtime snapshot…</p>}
      {error && <p className="trisla-error">{error}</p>}
      {!loading && !error && !isRuntimeSnapshotPopulated(snap) && (
        <p className="trisla-muted">Runtime snapshot not available for this intent.</p>
      )}
      {!loading && !error && isRuntimeSnapshotPopulated(snap) && snap && (
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
            <div className="trisla-status-row">
              <dt>telemetry_contract_version</dt>
              <dd>{displayField(snap.telemetry_contract_version)}</dd>
            </div>
          </dl>
          <DomainSection title="RAN" rows={ranRowsForLifecycle(snap.ran)} />
          <DomainSection title="Transport" rows={transportRowsForLifecycle(snap.transport)} />
          <DomainSection title="Core" rows={coreRowsForLifecycle(snap.core)} />
        </>
      )}
    </section>
  );
}
