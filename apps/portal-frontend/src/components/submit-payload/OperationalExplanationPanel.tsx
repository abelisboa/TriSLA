import { asMetadata, type SubmitResponse } from "../../lib/submitResponse";
import {
  contributingFactorRows,
  ReasonCodesBlock,
  SimpleTable,
  TextBlock,
  thresholdRows,
} from "./operationalExplanationBlocks";

type Props = { response: SubmitResponse; heading?: string };

const EXPLANATION_SCOPE_NOTE =
  "Operational explanations available from the live admission workflow. Extended ML explainability is not included in this view.";

export function OperationalExplanationPanel({
  response,
  heading = "3. Operational Explanation",
}: Props) {
  const metadata = asMetadata(response);
  const sliceMd = metadata?.slice_aware_multidomain;
  const sliceReasonCodes =
    sliceMd && typeof sliceMd === "object"
      ? (sliceMd as Record<string, unknown>).reason_codes
      : undefined;

  const factors = contributingFactorRows(metadata?.contributing_factors);
  const thresholds = thresholdRows(metadata?.thresholds_used);
  const systemXai = metadata?.system_xai_explanation;

  const decisionConfidence =
    response.confidence !== undefined && response.confidence !== null
      ? response.confidence
      : metadata?.confidence_score;

  return (
    <section className="trisla-status-card" aria-label="Operational Explanation">
      <h2>{heading}</h2>

      <ReasonCodesBlock codes={metadata?.reason_codes} />
      {Array.isArray(sliceReasonCodes) && sliceReasonCodes.length > 0 && (
        <div className="trisla-op-section">
          <h3>Multidomain Reason Codes</h3>
          <ul className="trisla-reason-codes">
            {sliceReasonCodes.map((code, i) => (
              <li key={`md-${String(code)}-${i}`}>
                <code>{String(code)}</code>
              </li>
            ))}
          </ul>
        </div>
      )}

      <TextBlock title="Operational Explanation (plain)" value={metadata?.decision_explanation_plain} />

      {systemXai && typeof systemXai === "object" ? (
        <div className="trisla-op-section">
          <h3>System-aware Explanation</h3>
          <dl>
            {Object.entries(systemXai as Record<string, unknown>).map(([key, value]) => (
              <div key={key} className="trisla-status-row">
                <dt>{key}</dt>
                <dd className={typeof value === "object" && value !== null ? "trisla-pre-wrap" : undefined}>
                  {typeof value === "object" && value !== null
                    ? JSON.stringify(value, null, 2)
                    : String(value ?? "Not available")}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      ) : (
        <TextBlock title="System-aware Explanation" value={systemXai} />
      )}

      <TextBlock title="Reasoning" value={response.reasoning ?? response.reason ?? response.justification} />

      <SimpleTable title="Operational Contributing Factors" headers={factors.headers} rows={factors.rows} />

      <SimpleTable title="Thresholds Used" headers={thresholds.headers} rows={thresholds.rows} />

      <div className="trisla-op-section">
        <h3>Confidence Breakdown</h3>
        <dl>
          <div className="trisla-status-row">
            <dt>Decision Confidence</dt>
            <dd>{decisionConfidence !== undefined && decisionConfidence !== null ? String(decisionConfidence) : "Not available"}</dd>
          </div>
          <div className="trisla-status-row">
            <dt>ML Confidence</dt>
            <dd>
              {metadata?.ml_confidence !== undefined && metadata?.ml_confidence !== null
                ? String(metadata.ml_confidence)
                : "Not available"}
            </dd>
          </div>
        </dl>
      </div>

      <p className="trisla-op-scope-note">{EXPLANATION_SCOPE_NOTE}</p>
    </section>
  );
}
