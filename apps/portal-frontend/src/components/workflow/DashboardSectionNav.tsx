import type { AdmissionDecision } from "../../lib/admissionLifecycleGate";

const ALL_SECTIONS = [
  { id: "section-decision", label: "Decision", level: 1 },
  { id: "section-service-profile", label: "Service Profile", level: 2 },
  { id: "section-telemetry", label: "Telemetry", level: 3 },
  { id: "section-operational", label: "Explanation", level: 4 },
  { id: "section-why-rejected", label: "Rejection", level: 4 },
  { id: "section-renegotiation", label: "Renegotiation", level: 4 },
  { id: "section-governance", label: "Governance", level: 5 },
  { id: "section-runtime", label: "Runtime", level: 6 },
  { id: "section-raw-payload", label: "Technical Details", level: 7 },
] as const;

function visibleSectionIds(decision: AdmissionDecision): string[] {
  const base = ["section-decision", "section-service-profile"];
  if (decision === "ACCEPT") {
    return [...base, "section-telemetry", "section-operational", "section-raw-payload"];
  }
  if (decision === "REJECT") {
    return [...base, "section-why-rejected", "section-governance", "section-raw-payload"];
  }
  if (decision === "RENEGOTIATE") {
    return [...base, "section-renegotiation", "section-governance", "section-raw-payload"];
  }
  return [...base, "section-governance", "section-raw-payload"];
}

type Props = { decision: AdmissionDecision };

export function DashboardSectionNav({ decision }: Props) {
  const allowed = new Set(visibleSectionIds(decision));
  const visible = ALL_SECTIONS.filter((s) => allowed.has(s.id));

  if (visible.length === 0) return null;

  return (
    <nav className="trisla-section-nav" aria-label="Lifecycle navigation">
      <p className="trisla-section-nav-label">Lifecycle navigation</p>
      <ul className="trisla-section-nav-list">
        {visible.map((section) => (
          <li key={section.id}>
            <a href={`#${section.id}`} className="trisla-section-nav-link">
              <span className="trisla-level-badge">L{section.level}</span>
              {section.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
