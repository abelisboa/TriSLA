const SECTIONS = [
  { id: "section-decision", label: "Decision", level: 1 },
  { id: "section-service-profile", label: "Service Profile", level: 2 },
  { id: "section-telemetry", label: "Telemetry", level: 3 },
  { id: "section-operational", label: "Explanation", level: 4 },
  { id: "section-governance", label: "Governance", level: 5 },
  { id: "section-runtime", label: "Runtime", level: 6 },
  { id: "section-raw-payload", label: "Technical Details", level: 7 },
] as const;

export function DashboardSectionNav() {
  return (
    <nav className="trisla-section-nav" aria-label="Lifecycle navigation">
      <p className="trisla-section-nav-label">Lifecycle navigation</p>
      <ul className="trisla-section-nav-list">
        {SECTIONS.map((section) => (
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
