"use client";

import {
  BESU_NETWORK_LABEL,
  formatBlockNumberDisplay,
  formatShortTxHash,
  hasOnChainEvidence,
  type OnChainEvidenceFields,
} from "../../lib/blockchainEvidenceDisplay";
import { displayOnChainCommitStatus } from "../../lib/governanceDisplayLabels";
import { operatorFieldLabel } from "../../lib/operatorLabels";
import { CopyableHash } from "./CopyableHash";

type Props = {
  evidence: OnChainEvidenceFields;
  summaryLabel?: string;
  className?: string;
};

export function OnChainEvidenceDetails({
  evidence,
  summaryLabel = "On-chain evidence",
  className = "trisla-details trisla-details-secondary",
}: Props) {
  if (!hasOnChainEvidence(evidence)) return null;

  const network = evidence.network ?? BESU_NETWORK_LABEL;
  const blockDisplay = formatBlockNumberDisplay(evidence.block_number);
  const shortHash = formatShortTxHash(evidence.tx_hash);
  const fullHash = evidence.tx_hash ? String(evidence.tx_hash).trim() : "";

  return (
    <details className={className} style={{ marginTop: "0.75rem" }}>
      <summary>{summaryLabel}</summary>
      <dl style={{ marginTop: "0.5rem" }}>
        {evidence.bc_status ? (
          <div className="trisla-status-row">
            <dt>{operatorFieldLabel("bc_status")}</dt>
            <dd>{displayOnChainCommitStatus(evidence.bc_status)}</dd>
          </div>
        ) : null}
        {fullHash ? (
          <div className="trisla-status-row">
            <dt>{operatorFieldLabel("tx_hash")}</dt>
            <dd>
              <span title={fullHash}>{shortHash || fullHash}</span>
              <div style={{ marginTop: "0.25rem" }}>
                <CopyableHash value={fullHash} />
              </div>
            </dd>
          </div>
        ) : null}
        {blockDisplay ? (
          <div className="trisla-status-row">
            <dt>{operatorFieldLabel("block_number")}</dt>
            <dd>{blockDisplay}</dd>
          </div>
        ) : null}
        <div className="trisla-status-row">
          <dt>Network</dt>
          <dd>{network}</dd>
        </div>
      </dl>
    </details>
  );
}
