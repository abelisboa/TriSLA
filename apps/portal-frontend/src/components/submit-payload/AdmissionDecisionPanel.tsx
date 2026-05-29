import type { SubmitResponse } from "../../lib/submitResponse";
import { FieldList } from "./FieldList";

type Props = { response: SubmitResponse };

export function AdmissionDecisionPanel({ response }: Props) {
  return (
    <section className="trisla-status-card" aria-label="Admission Decision">
      <h2>1. Admission Decision</h2>
      <FieldList fields={[{ label: "decision", value: response.decision }]} />
    </section>
  );
}
