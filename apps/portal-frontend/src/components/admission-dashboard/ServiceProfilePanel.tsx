import { FieldList } from "../submit-payload/FieldList";
import {
  SERVICE_PROFILE_SOURCE,
  asSlaRequirementsRecord,
  serviceProfileContractFields,
} from "../../lib/serviceProfileContract";

type Props = {
  slaRequirements?: unknown;
  serviceType?: unknown;
};

export function ServiceProfilePanel({ slaRequirements, serviceType }: Props) {
  const sla = asSlaRequirementsRecord(slaRequirements);
  const fields = serviceProfileContractFields(sla, serviceType);

  return (
    <section className="trisla-status-card trisla-admission-section" aria-label="SLA Contract">
      <h2>2. Service Profile</h2>
      <p className="trisla-muted">SLA requirements — contract view only (no observed telemetry).</p>
      <FieldList fields={fields} />
      <p className="trisla-muted trisla-summary-source">Source: {SERVICE_PROFILE_SOURCE}</p>
    </section>
  );
}
