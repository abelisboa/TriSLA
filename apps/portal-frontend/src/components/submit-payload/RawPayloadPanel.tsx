import type { SubmitResponse } from "../../lib/submitResponse";

type Props = { response: SubmitResponse; heading?: string };

export function RawPayloadPanel({ response, heading = "Technical Details" }: Props) {
  return (
    <section className="trisla-status-card" aria-label="Technical Details">
      <h2>{heading}</h2>
      <p className="trisla-muted">Full API response for advanced troubleshooting.</p>
      <details className="trisla-details">
        <summary>View full API response</summary>
        <pre className="trisla-pre-secondary">{JSON.stringify(response, null, 2)}</pre>
      </details>
    </section>
  );
}
