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

export function DemoFlowSteps({ title = "Demo flow", steps }: Props) {
  return (
    <nav className="trisla-demo-flow" aria-label={title}>
      <h2 className="trisla-demo-flow-title">{title}</h2>
      <ol className="trisla-demo-flow-list">
        {steps.map((step, index) => (
          <li
            key={step.id}
            className={[
              "trisla-demo-flow-step",
              step.active ? "trisla-demo-flow-step-active" : "",
              step.complete ? "trisla-demo-flow-step-complete" : "",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            <span className="trisla-demo-flow-index">{index + 1}</span>
            <span className="trisla-demo-flow-label">{step.label}</span>
            <span className="trisla-demo-flow-desc">{step.description}</span>
          </li>
        ))}
      </ol>
    </nav>
  );
}

export const TEMPLATE_DEMO_STEPS: Step[] = [
  { id: "submit", label: "Submit", description: "Structured template form" },
  { id: "admission", label: "Admission", description: "Decision dashboard" },
  { id: "governance", label: "Governance", description: "Evidence & lifecycle" },
  { id: "runtime", label: "Runtime", description: "Manual revalidation" },
];

export const PNL_DEMO_STEPS: Step[] = [
  { id: "pnl", label: "PNL", description: "Natural language intent" },
  { id: "interpret", label: "Interpret", description: "Semantic preview" },
  { id: "submit", label: "Submit", description: "Confirm template_id" },
  { id: "admission", label: "Admission", description: "Decision dashboard" },
  { id: "governance", label: "Governance", description: "Evidence & lifecycle" },
  { id: "runtime", label: "Runtime", description: "Manual revalidation" },
];
