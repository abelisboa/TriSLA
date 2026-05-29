import {
  asSlaRequirements,
  tenantIdFromResponse,
  type SubmitResponse,
} from "../../lib/submitResponse";
import { FieldList } from "../submit-payload/FieldList";

type Props = { response: SubmitResponse };

export function ServiceProfilePanel({ response }: Props) {
  const sla = asSlaRequirements(response);

  return (
    <section className="trisla-status-card trisla-admission-section" aria-label="Service Profile">
      <h2>2. Service Profile</h2>
      <FieldList
        fields={[
          { label: "tenant_id", value: tenantIdFromResponse(response) },
          {
            label: "slice_type",
            value: sla?.slice_type ?? response.service_type,
          },
          { label: "template_id", value: sla?.template_id },
          { label: "latency", value: sla?.latency },
          { label: "throughput", value: sla?.throughput },
          { label: "reliability", value: sla?.reliability },
        ]}
      />
    </section>
  );
}
