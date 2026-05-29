import type { InterpretResponse } from "../../lib/pnlSubmit";
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
          { label: "input_text (request)", value: inputText },
          { label: "intent_id", value: interpret.intent_id },
          { label: "nest_id", value: interpret.nest_id },
          { label: "service_type", value: interpret.service_type },
          { label: "slice_type", value: interpret.slice_type },
          { label: "tenant_id", value: interpret.tenant_id },
          { label: "status", value: interpret.status },
          { label: "message", value: interpret.message },
          { label: "sla_id", value: interpret.sla_id },
          { label: "created_at", value: interpret.created_at },
          { label: "template_id", value: interpret.template_id },
        ]}
      />
      <FieldList
        fields={[
          { label: "sla_requirements", value: sla },
          { label: "technical_parameters", value: tech },
        ]}
      />
      <details className="trisla-details">
        <summary>Interpret response (full JSON)</summary>
        <pre className="trisla-pre-secondary">{JSON.stringify(interpret, null, 2)}</pre>
      </details>
    </section>
  );
}
