import { displayField } from "../../lib/submitResponse";
import { operatorFieldLabel } from "../../lib/operatorLabels";
import type { RevalidateTelemetryResponse, SlaRuntimeStatusResponse } from "../../lib/runtimeSupervision";
import { FieldList } from "../submit-payload/FieldList";

type Props = {
  statusData: SlaRuntimeStatusResponse | null;
  lifecycleState: unknown;
  loading: boolean;
  error: string | undefined;
};

export function RuntimeStatusPanel({ statusData, lifecycleState, loading, error }: Props) {
  return (
    <section className="trisla-runtime-subsection" aria-label="Runtime Status">
      <h3>Runtime Status</h3>
      {loading && <p className="trisla-muted">Loading runtime status…</p>}
      {error && <p className="trisla-error">{error}</p>}
      {!loading && !error && statusData && (
        <FieldList
          fields={[
            { label: operatorFieldLabel("intent_id"), value: statusData.intent_id ?? statusData.sla_id },
            { label: "Status", value: statusData.status },
            { label: operatorFieldLabel("lifecycle_state"), value: lifecycleState },
          ]}
        />
      )}
      {!loading && !error && !statusData && (
        <p className="trisla-muted">Runtime status not loaded.</p>
      )}
      {statusData && (
        <details className="trisla-details">
          <summary>Additional status fields</summary>
          <FieldList
            fields={[
              { label: operatorFieldLabel("sla_id"), value: statusData.sla_id },
              { label: operatorFieldLabel("tenant_id"), value: statusData.tenant_id },
              { label: operatorFieldLabel("nest_id"), value: statusData.nest_id },
              { label: "created_at", value: statusData.created_at },
              { label: "updated_at", value: statusData.updated_at },
            ]}
          />
        </details>
      )}
    </section>
  );
}

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
      <h4>{title}</h4>
      <FieldList
        fields={Object.entries(data).map(([label, value]) => ({ label, value }))}
      />
    </div>
  );
}

export function FreshTelemetryPanel({
  snapshot,
}: {
  snapshot: Record<string, unknown> | undefined;
}) {
  if (!snapshot) {
    return (
      <section className="trisla-runtime-subsection" aria-label="Fresh Telemetry">
        <h3>Fresh Telemetry</h3>
        <p className="trisla-muted">telemetry_snapshot_atual: Not available</p>
      </section>
    );
  }

  return (
    <section className="trisla-runtime-subsection" aria-label="Fresh Telemetry">
      <h3>Fresh Telemetry</h3>
      <FieldList
        fields={[
          { label: "execution_id", value: snapshot.execution_id },
          { label: "timestamp", value: snapshot.timestamp },
          { label: "telemetry_contract_version", value: snapshot.telemetry_contract_version },
        ]}
      />
      <DomainBlock title="RAN" data={snapshot.ran as Record<string, unknown> | undefined} />
      <DomainBlock title="Transport" data={snapshot.transport as Record<string, unknown> | undefined} />
      <DomainBlock title="Core" data={snapshot.core as Record<string, unknown> | undefined} />
    </section>
  );
}

export function DriftAnalysisPanel({
  driftSummary,
}: {
  driftSummary: RevalidateTelemetryResponse["drift_summary"];
}) {
  if (!driftSummary) {
    return (
      <section className="trisla-runtime-subsection" aria-label="Drift Analysis">
        <h3>Drift Analysis</h3>
        <p className="trisla-muted">drift_summary: Not available</p>
      </section>
    );
  }

  const deltas = driftSummary.deltas ?? [];

  return (
    <section className="trisla-runtime-subsection" aria-label="Drift Analysis">
      <h3>Drift Analysis</h3>
      <FieldList
        fields={[
          { label: "drift_summary.compared", value: driftSummary.compared },
          { label: "drift_summary.fields_compared", value: driftSummary.fields_compared },
          { label: "drift_summary.reason", value: driftSummary.reason },
        ]}
      />
      {deltas.length === 0 ? (
        <p className="trisla-muted">No drift deltas returned.</p>
      ) : (
        <div className="trisla-table-wrap">
          <table className="trisla-simple-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Previous</th>
                <th>Current</th>
                <th>Delta</th>
              </tr>
            </thead>
            <tbody>
              {deltas.map((row) => (
                <tr key={row.path ?? JSON.stringify(row)}>
                  <td>{displayField(row.path)}</td>
                  <td>{displayField(row.reference)}</td>
                  <td>{displayField(row.current)}</td>
                  <td>{displayField(row.delta)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export function RemediationEvidencePanel({
  evidence,
}: {
  evidence: Record<string, unknown> | undefined;
}) {
  if (!evidence) {
    return null;
  }

  return (
    <section className="trisla-runtime-subsection" aria-label="Remediation Evidence">
      <h3>Remediation Evidence</h3>
      <FieldList
        fields={Object.entries(evidence).map(([label, value]) => ({ label, value }))}
      />
    </section>
  );
}

export function RuntimePayloadPanel({ payload }: { payload: RevalidateTelemetryResponse }) {
  return (
    <section className="trisla-runtime-subsection" aria-label="Runtime Payload">
      <details className="trisla-details">
        <summary>Show Runtime Payload</summary>
        <pre className="trisla-pre-secondary">{JSON.stringify(payload, null, 2)}</pre>
      </details>
    </section>
  );
}
