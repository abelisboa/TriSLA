import type { ReactNode } from "react";
import type { GovernanceClarityPayload } from "../../lib/phaseNextConsistency";
import type { SubmitResponse } from "../../lib/submitResponse";
import { governanceClarityFromSubmit } from "../../lib/phaseNextConsistency";
import type { OnChainEvidenceFields } from "../../lib/blockchainEvidenceDisplay";
import {
  CLARITY_LABELS,
  displayClarityBlockchainStatus,
  displayClarityEventType,
  displayClarityGovernanceStatus,
  displayClarityReason,
  GOVERNANCE_LAYER_LEGEND,
  GOVERNANCE_TOOLTIPS,
} from "../../lib/governanceDisplayLabels";
import { OnChainEvidenceDetails } from "./OnChainEvidenceDetails";

type Props = {
  clarity?: GovernanceClarityPayload;
  submitResponse?: SubmitResponse;
  onChainEvidence?: OnChainEvidenceFields;
};

function LabelWithTip({ label, tip, children }: { label: string; tip: string; children: ReactNode }) {
  return (
    <>
      <dt title={tip}>{label}</dt>
      <dd>{children}</dd>
    </>
  );
}

export function GovernanceClarityPanel({ clarity, submitResponse, onChainEvidence }: Props) {
  const gc = clarity ?? (submitResponse ? governanceClarityFromSubmit(submitResponse) : undefined);
  if (!gc) {
    return (
      <section className="trisla-consistency-panel" aria-label="Governance and commit status">
        <h3 className="trisla-consistency-title">{CLARITY_LABELS.sectionTitle}</h3>
        <p className="trisla-muted">Governance clarity data not available from backend.</p>
      </section>
    );
  }

  const gov = gc.governance_event;
  const bc = gc.blockchain_registration;
  const govOk = String(gov?.status ?? "").toLowerCase() === "recorded";
  const bcOk = bc?.executed === true;
  const reasonDisplay = displayClarityReason(bc?.reason);

  return (
    <section className="trisla-consistency-panel" aria-label="Governance and commit status">
      <h3 className="trisla-consistency-title">{CLARITY_LABELS.sectionTitle}</h3>
      <p className="trisla-muted trisla-governance-layer-legend">{GOVERNANCE_LAYER_LEGEND}</p>
      <dl>
        <div className="trisla-status-row">
          <LabelWithTip label={CLARITY_LABELS.admissionDecision} tip={GOVERNANCE_TOOLTIPS.admissionDecision}>
            <span className={govOk ? "trisla-gov-ok" : "trisla-gov-muted"}>
              {govOk ? "✓" : "○"} {displayClarityGovernanceStatus(gov?.status)}
            </span>
            {gov?.event_type ? (
              <span className="trisla-muted"> — {displayClarityEventType(gov.event_type)}</span>
            ) : null}
          </LabelWithTip>
        </div>
        <div className="trisla-status-row">
          <LabelWithTip
            label={bc?.label ?? CLARITY_LABELS.blockchainRegistration}
            tip={GOVERNANCE_TOOLTIPS.onChainCommit}
          >
            <span className={bcOk ? "trisla-gov-ok" : "trisla-gov-warn"}>
              {bcOk ? "✓ Executed" : `✗ ${displayClarityBlockchainStatus(bc?.status, bc?.executed)}`}
            </span>
          </LabelWithTip>
        </div>
        {reasonDisplay ? (
          <div className="trisla-status-row">
            <LabelWithTip label={CLARITY_LABELS.note} tip={GOVERNANCE_TOOLTIPS.onChainNote}>
              {reasonDisplay}
            </LabelWithTip>
          </div>
        ) : null}
      </dl>
      {bcOk && onChainEvidence ? (
        <OnChainEvidenceDetails evidence={onChainEvidence} summaryLabel="Blockchain evidence" />
      ) : null}
    </section>
  );
}
