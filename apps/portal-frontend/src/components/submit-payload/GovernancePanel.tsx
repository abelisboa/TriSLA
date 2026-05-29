import { asMetadata, type SubmitResponse } from "../../lib/submitResponse";
import { FieldList } from "./FieldList";
import {
  AuditabilityMetadataPanel,
  GovernanceOverviewPanel,
  GovernancePayloadPanel,
  LifecycleTimelinePanel,
  RegistrationEvidencePanel,
} from "../governance-dashboard/GovernanceDashboardPanels";

type Props = { response: SubmitResponse; heading?: string };

export function GovernancePanel({ response, heading = "5. Governance" }: Props) {
  const metadata = asMetadata(response);
  const txHash = response.tx_hash ?? response.blockchain_tx_hash;

  return (
    <section className="trisla-status-card trisla-governance-dashboard" aria-label="Governance">
      <h2>{heading}</h2>
      <p className="trisla-muted">
        Governance Evidence, Lifecycle Traceability, and Auditability Metadata — submit response only.
      </p>

      <details className="trisla-details trisla-details-secondary">
        <summary>Core governance fields (submit response)</summary>
        <FieldList
          fields={[
            { label: "bc_status", value: response.bc_status },
            { label: "tx_hash", value: txHash },
            { label: "block_number", value: response.block_number },
            { label: "blockchain_status", value: response.blockchain_status },
            { label: "blockchain_tx_hash", value: response.blockchain_tx_hash },
            { label: "metadata.governance_event", value: metadata?.governance_event },
            { label: "metadata.governance_event_id", value: metadata?.governance_event_id },
            {
              label: "metadata.governance_registration_status",
              value: metadata?.governance_registration_status,
            },
          ]}
        />
      </details>

      <GovernanceOverviewPanel response={response} />
      <LifecycleTimelinePanel response={response} />
      <RegistrationEvidencePanel response={response} />
      <AuditabilityMetadataPanel response={response} />
      <GovernancePayloadPanel response={response} />
    </section>
  );
}
