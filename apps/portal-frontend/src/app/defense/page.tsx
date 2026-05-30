export default function DefensePage() {
  const unavailable = "Not available";

  return (
    <section>
      <h1>Defense</h1>
      <p className="trisla-subtitle">
        Platform defense and protection services — reserved for future operational release.
      </p>
      <div className="trisla-cards-grid">
        <section className="trisla-status-card" aria-label="Admission Protection">
          <h2>Admission Protection</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{unavailable}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Service</dt>
              <dd>Planned platform capability</dd>
            </div>
          </dl>
        </section>

        <section className="trisla-status-card" aria-label="Runtime Integrity">
          <h2>Runtime Integrity</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{unavailable}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Service</dt>
              <dd>Planned platform capability</dd>
            </div>
          </dl>
        </section>

        <section className="trisla-status-card" aria-label="Blockchain Trust Layer">
          <h2>Blockchain Trust Layer</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{unavailable}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Service</dt>
              <dd>Planned platform capability</dd>
            </div>
          </dl>
        </section>

        <section className="trisla-status-card" aria-label="SLA Protection Status">
          <h2>SLA Protection Status</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{unavailable}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Service</dt>
              <dd>Planned platform capability</dd>
            </div>
          </dl>
        </section>
      </div>
    </section>
  );
}
