import { asMetadata, type SubmitResponse } from "../../lib/submitResponse";
import { FieldList } from "./FieldList";

type Props = { response: SubmitResponse };

export function FeasibilityPanel({ response }: Props) {
  const metadata = asMetadata(response);
  const confidence =
    response.confidence !== undefined && response.confidence !== null
      ? response.confidence
      : metadata?.confidence_score;

  return (
    <section className="trisla-status-card" aria-label="Feasibility Assessment">
      <h2>2. Feasibility Assessment</h2>
      <FieldList
        fields={[
          { label: "metadata.decision_score", value: metadata?.decision_score },
          { label: "confidence", value: confidence },
          { label: "metadata.decision_mode", value: metadata?.decision_mode },
          { label: "metadata.policy_result", value: metadata?.policy_result },
          { label: "metadata.decision_band", value: metadata?.decision_band },
          { label: "metadata.final_decision", value: metadata?.final_decision },
          { label: "metadata.threshold_decision", value: metadata?.threshold_decision },
        ]}
      />
    </section>
  );
}
