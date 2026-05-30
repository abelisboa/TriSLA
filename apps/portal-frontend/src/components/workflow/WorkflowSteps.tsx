type Step = {
  id: string;
  label: string;
  description: string;
  active?: boolean;
  complete?: boolean;
};

type Props = {
  title?: string;
  steps: Step[];
};

export function WorkflowSteps({ title = "Service workflow", steps }: Props) {
  return (
    <nav className="trisla-workflow" aria-label={title}>
      <h2 className="trisla-workflow-title">{title}</h2>
      <ol className="trisla-workflow-list">
        {steps.map((step, index) => (
          <li
            key={step.id}
            className={[
              "trisla-workflow-step",
              step.active ? "trisla-workflow-step-active" : "",
              step.complete ? "trisla-workflow-step-complete" : "",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            <span className="trisla-workflow-index">{index + 1}</span>
            <span className="trisla-workflow-label">{step.label}</span>
            <span className="trisla-workflow-desc">{step.description}</span>
          </li>
        ))}
      </ol>
    </nav>
  );
}

export const TEMPLATE_WORKFLOW_STEPS: Step[] = [
  { id: "submit", label: "Submit", description: "Structured template form" },
  { id: "admission", label: "Admission", description: "Decision dashboard" },
  { id: "governance", label: "Governance", description: "Registration and lifecycle" },
  { id: "runtime", label: "Runtime", description: "Operational supervision" },
];

export const PNL_WORKFLOW_STEPS: Step[] = [
  { id: "pnl", label: "PNL", description: "Natural language intent" },
  { id: "interpret", label: "Interpret", description: "Semantic preview" },
  { id: "submit", label: "Submit", description: "Confirm template reference" },
  { id: "admission", label: "Admission", description: "Decision dashboard" },
  { id: "governance", label: "Governance", description: "Registration and lifecycle" },
  { id: "runtime", label: "Runtime", description: "Operational supervision" },
];
