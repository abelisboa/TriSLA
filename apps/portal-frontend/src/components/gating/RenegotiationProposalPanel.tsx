import { displayField } from "../../lib/submitResponse";
import type { SubmitResponse } from "../../lib/submitResponse";
import type { SlaRuntimeStatusResponse } from "../../lib/runtimeSupervision";
import { extractRenegotiationFields } from "../../lib/renegotiationPanelDisplay";

type Props = {
  statusData?: SlaRuntimeStatusResponse | null;
  submitResponse?: SubmitResponse;
};

export function RenegotiationProposalPanel({ statusData, submitResponse }: Props) {
  const fields = extractRenegotiationFields(statusData, submitResponse);

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
            <strong>Profile:</strong> {displayField(fields.requestedType)}
          </p>
          <p>
            <strong>Latency:</strong> {displayField(fields.requestedLatency)}
          </p>
        </article>
        <article className="trisla-fidelity-card">
          <h4>Suggested Alternative</h4>
          <p>
            <strong>Profile:</strong> {displayField(fields.suggestedType)}
          </p>
          <p>
            <strong>Latency:</strong> {displayField(fields.suggestedLatency)}
          </p>
        </article>
      </div>
      <p className="trisla-muted" style={{ marginTop: "0.75rem" }}>
        {displayField(fields.explanation)}
      </p>
    </section>
  );
}
