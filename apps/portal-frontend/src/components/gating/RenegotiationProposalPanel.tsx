import { asMetadata, type SubmitResponse } from "../../lib/submitResponse";
import type { SlaRuntimeStatusResponse } from "../../lib/runtimeSupervision";

type Props = {
  statusData?: SlaRuntimeStatusResponse | null;
  submitResponse?: SubmitResponse;
};

function pickCanonicalSla(status?: SlaRuntimeStatusResponse | null, submit?: SubmitResponse) {
  const md = submit ? asMetadata(submit) : undefined;
  const fromStatus = status?.operational_summary as Record<string, unknown> | undefined;
  return (
    (md?.canonical_sla as Record<string, unknown> | undefined) ??
    (fromStatus?.canonical_sla as Record<string, unknown> | undefined)
  );
}

export function RenegotiationProposalPanel({ statusData, submitResponse }: Props) {
  const md = submitResponse ? asMetadata(submitResponse) : undefined;
  const slaReq =
    (statusData?.operational_summary as Record<string, unknown> | undefined)?.sla_requirements ??
    md?.sla_requirements ??
    submitResponse?.sla_requirements;
  const canonical = pickCanonicalSla(statusData, submitResponse);
  const explanation =
    statusData?.admission_reasoning ??
    md?.decision_explanation_plain ??
    md?.decision_explanation;

  const requestedLatency =
    slaReq && typeof slaReq === "object"
      ? (slaReq as Record<string, unknown>).latency ??
        (slaReq as Record<string, unknown>).latency_ms
      : undefined;
  const requestedType =
    slaReq && typeof slaReq === "object"
      ? (slaReq as Record<string, unknown>).slice_type ??
        (slaReq as Record<string, unknown>).type
      : (statusData?.operational_summary as Record<string, unknown> | undefined)?.service_type;

  const suggestedLatency =
    canonical && typeof canonical === "object"
      ? (canonical as Record<string, unknown>).latency ??
        (canonical as Record<string, unknown>).latency_ms
      : undefined;
  const suggestedType =
    canonical && typeof canonical === "object"
      ? (canonical as Record<string, unknown>).slice_type ??
        (canonical as Record<string, unknown>).service_type
      : undefined;

  return (
    <section className="trisla-consistency-panel" aria-label="Renegotiation Proposal">
      <h3 className="trisla-consistency-title">Renegotiation Proposal</h3>
      <p className="trisla-muted">
        Suggested adjustments based on admission decision — no runtime supervision until ACCEPT.
      </p>
      <div className="trisla-fidelity-grid">
        <article className="trisla-fidelity-card">
          <h4>Requested</h4>
          <p>
            <strong>Profile:</strong> {String(requestedType ?? "—")}
          </p>
          <p>
            <strong>Latency:</strong> {String(requestedLatency ?? "—")}
          </p>
        </article>
        <article className="trisla-fidelity-card">
          <h4>Suggested Alternative</h4>
          <p>
            <strong>Profile:</strong> {String(suggestedType ?? requestedType ?? "eMBB")}
          </p>
          <p>
            <strong>Latency:</strong> {String(suggestedLatency ?? "5 ms")}
          </p>
        </article>
      </div>
      {explanation ? (
        <p className="trisla-muted" style={{ marginTop: "0.75rem" }}>
          {String(explanation)}
        </p>
      ) : (
        <p className="trisla-muted" style={{ marginTop: "0.75rem" }}>
          Required changes: relax URLLC latency target or migrate to eMBB profile per policy thresholds.
        </p>
      )}
    </section>
  );
}
