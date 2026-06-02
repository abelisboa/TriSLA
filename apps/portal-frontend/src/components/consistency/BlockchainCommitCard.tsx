"use client";

import {
  BESU_NETWORK_LABEL,
  formatBlockNumberDisplay,
  formatShortTxHash,
  hasOnChainEvidence,
  isBcStatusCommitted,
  type OnChainEvidenceFields,
} from "../../lib/blockchainEvidenceDisplay";
import { GOVERNANCE_TOOLTIPS } from "../../lib/governanceDisplayLabels";
import { formatBlockchainStatusLabel } from "../../lib/operatorLabels";
import { OnChainEvidenceDetails } from "./OnChainEvidenceDetails";

type Props = {
  bcStatus?: string | null;
  txHash?: string | null;
  blockNumber?: number | string | null;
};

export function BlockchainCommitCard({ bcStatus, txHash, blockNumber }: Props) {
  const evidence: OnChainEvidenceFields = {
    bc_status: bcStatus,
    tx_hash: txHash,
    block_number: blockNumber,
    network: BESU_NETWORK_LABEL,
  };
  const committed = isBcStatusCommitted(bcStatus);
  const shortHash = formatShortTxHash(txHash);
  const blockDisplay = formatBlockNumberDisplay(blockNumber);

  return (
    <>
      <dl>
        <div className="trisla-status-row">
          <dt title={GOVERNANCE_TOOLTIPS.onChainCommit}>On-chain commit</dt>
          <dd>
            {committed ? (
              <span className="trisla-gov-ok">✓ Committed</span>
            ) : (
              formatBlockchainStatusLabel(bcStatus)
            )}
          </dd>
        </div>
        <div className="trisla-status-row">
          <dt>Transaction</dt>
          <dd>
            {txHash ? (
              <>
                Registered
                {shortHash ? (
                  <span className="trisla-muted" title={String(txHash)}>
                    {" "}
                    · <code className="trisla-hash-inline">{shortHash}</code>
                  </span>
                ) : null}
              </>
            ) : (
              "Not available"
            )}
          </dd>
        </div>
        <div className="trisla-status-row">
          <dt>Block</dt>
          <dd>
            {blockNumber != null && blockNumber !== "" ? (
              <>
                Confirmed
                {blockDisplay ? <span className="trisla-muted"> · {blockDisplay}</span> : null}
              </>
            ) : (
              "Not available"
            )}
          </dd>
        </div>
      </dl>
      {hasOnChainEvidence(evidence) ? <OnChainEvidenceDetails evidence={evidence} /> : null}
    </>
  );
}
