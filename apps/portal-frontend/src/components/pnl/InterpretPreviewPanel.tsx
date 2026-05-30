import type { InterpretResponse } from "../../lib/pnlSubmit";
import { operatorFieldLabel } from "../../lib/operatorLabels";
import { FieldList } from "../submit-payload/FieldList";

type Props = {
  interpret: InterpretResponse;
  inputText: string;
};

export function InterpretPreviewPanel({ interpret, inputText }: Props) {
  const sla = interpret.sla_requirements;
  const tech = interpret.technical_parameters;

  return (
    <section className="trisla-status-card" aria-label="Interpret Preview">
      <h2>Interpret Preview</h2>
      <FieldList
        fields={[
          { label: operatorFieldLabel("input_text (request)"), value: inputText },
          { label: operatorFieldLabel("intent_id"), value: interpret.intent_id },
          { label: operatorFieldLabel("nest_id"), value: interpret.nest_id },
          { label: operatorFieldLabel("service_type"), value: interpret.service_type },
          { label: operatorFieldLabel("slice_type"), value: interpret.slice_type },
          { label: operatorFieldLabel("tenant_id"), value: interpret.tenant_id },
          { label: "Status", value: interpret.status },
          { label: "Message", value: interpret.message },
          { label: operatorFieldLabel("sla_id"), value: interpret.sla_id },
          { label: operatorFieldLabel("created_at"), value: interpret.created_at },
          { label: operatorFieldLabel("template_id"), value: interpret.template_id },
        ]}
      />
      <FieldList
        fields={[
          { label: operatorFieldLabel("sla_requirements"), value: sla },
          { label: operatorFieldLabel("technical_parameters"), value: tech },
        ]}
      />
      <details className="trisla-details">
        <summary>Technical details — full API response</summary>
        <pre className="trisla-pre-secondary">{JSON.stringify(interpret, null, 2)}</pre>
      </details>
    </section>
  );
}
