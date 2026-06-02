import { asMetadata, type SubmitResponse } from "../../lib/submitResponse";
import { resolveOperationalConfidence } from "../../lib/confidenceDisplay";
import { formatDecisionScore } from "../../lib/operatorFormat";
import { operatorFieldLabel } from "../../lib/operatorLabels";
import { FieldList } from "../submit-payload/FieldList";
import { DecisionEvidencePanel } from "../consistency/DecisionEvidencePanel";
import { decisionEvidenceFromSubmit } from "../../lib/phaseNextConsistency";

type Props = { response: SubmitResponse };

export function AdmissionOverviewPanel({ response }: Props) {
  const metadata = asMetadata(response);
  const modelConfidence = resolveOperationalConfidence(response);

  const decision = response.decision ?? "—";
  const decisionScore = metadata?.decision_score;
  const evidence = decisionEvidenceFromSubmit(response);

  return (
    <section className="trisla-status-card trisla-admission-section" aria-label="Admission Overview">
      <h2>1. Decision</h2>
      <p className="trisla-section-lead">Primary admission outcome from the submit response.</p>

      <div className="trisla-summary-cards" role="list" aria-label="Decision summary">
        <article className="trisla-summary-card trisla-summary-card-primary" role="listitem">
          <span className="trisla-summary-label">Decision</span>
          <span className="trisla-summary-value">{String(decision)}</span>
        </article>
        <article className="trisla-summary-card" role="listitem">
          <span className="trisla-summary-label">Decision Score</span>
          <span className="trisla-summary-value">
            {decisionScore != null ? formatDecisionScore(decisionScore) : "—"}
          </span>
        </article>
        <article className="trisla-summary-card" role="listitem">
          <span className="trisla-summary-label">Model Confidence</span>
          <span className="trisla-summary-value">
            {modelConfidence != null ? formatDecisionScore(modelConfidence) : "Not available"}
          </span>
        </article>
      </div>

      <DecisionEvidencePanel evidence={evidence} />

      <details className="trisla-details trisla-details-secondary">
        <summary>Technical Details — decision metadata</summary>
        <FieldList
          fields={[
            { label: operatorFieldLabel("metadata.decision_score"), value: metadata?.decision_score },
            { label: "response.confidence", value: response.confidence },
            { label: operatorFieldLabel("metadata.ml_confidence"), value: metadata?.ml_confidence },
            { label: operatorFieldLabel("metadata.confidence_score"), value: metadata?.confidence_score },
            { label: operatorFieldLabel("metadata.decision_mode"), value: metadata?.decision_mode },
            { label: operatorFieldLabel("metadata.policy_result"), value: metadata?.policy_result },
            { label: operatorFieldLabel("metadata.decision_band"), value: metadata?.decision_band },
            { label: operatorFieldLabel("metadata.final_decision"), value: metadata?.final_decision },
          ]}
        />
      </details>
    </section>
  );
}
