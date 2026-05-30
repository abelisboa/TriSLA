import { asMetadata, type SubmitResponse } from "../../lib/submitResponse";
import {
  formatBlockchainStatusLabel,
  formatRegistrationStatusLabel,
  operatorFieldLabel,
} from "../../lib/operatorLabels";
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
        Governance registration, lifecycle traceability, and audit metadata from the SLA submission.
      </p>

      <FieldList
        fields={[
          {
            label: operatorFieldLabel("bc_status"),
            value: formatBlockchainStatusLabel(response.bc_status),
          },
          {
            label: operatorFieldLabel("registration_status"),
            value: formatRegistrationStatusLabel(metadata?.governance_registration_status),
          },
        ]}
      />

      <details className="trisla-details trisla-details-secondary">
        <summary>Technical Details</summary>
        <FieldList
          fields={[
            { label: operatorFieldLabel("bc_status"), value: response.bc_status },
            { label: operatorFieldLabel("tx_hash"), value: txHash },
            { label: operatorFieldLabel("block_number"), value: response.block_number },
            { label: operatorFieldLabel("blockchain_status"), value: response.blockchain_status },
            { label: operatorFieldLabel("blockchain_tx_hash"), value: response.blockchain_tx_hash },
            { label: operatorFieldLabel("metadata.governance_event"), value: metadata?.governance_event },
            { label: operatorFieldLabel("metadata.governance_event_id"), value: metadata?.governance_event_id },
            {
              label: operatorFieldLabel("metadata.governance_registration_status"),
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
