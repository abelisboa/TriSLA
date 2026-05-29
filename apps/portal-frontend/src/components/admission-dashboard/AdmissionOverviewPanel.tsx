import { asMetadata, type SubmitResponse } from "../../lib/submitResponse";
import { FieldList } from "../submit-payload/FieldList";

type Props = { response: SubmitResponse };

export function AdmissionOverviewPanel({ response }: Props) {
  const metadata = asMetadata(response);
  const confidence =
    response.confidence !== undefined && response.confidence !== null
      ? response.confidence
      : metadata?.confidence_score;

  return (
    <section className="trisla-status-card trisla-admission-section" aria-label="Admission Overview">
      <h2>1. Admission Overview</h2>
      <FieldList
        fields={[
          { label: "decision", value: response.decision },
          { label: "metadata.decision_score", value: metadata?.decision_score },
          { label: "confidence", value: confidence },
          { label: "metadata.decision_mode", value: metadata?.decision_mode },
          { label: "metadata.policy_result", value: metadata?.policy_result },
        ]}
      />
    </section>
  );
}
