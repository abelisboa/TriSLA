import type { SubmitResponse } from "../../lib/submitResponse";

type Props = { response: SubmitResponse; heading?: string };

export function RawPayloadPanel({ response, heading = "6. Raw Payload" }: Props) {
  return (
    <section className="trisla-status-card" aria-label="Raw Payload">
      <h2>{heading}</h2>
      <details className="trisla-details">
        <summary>Show Full Payload</summary>
        <pre className="trisla-pre-secondary">{JSON.stringify(response, null, 2)}</pre>
      </details>
    </section>
  );
}
