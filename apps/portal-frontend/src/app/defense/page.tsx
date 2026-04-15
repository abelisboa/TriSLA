export default function DefensePage() {
  const noEndpoint = "No defense endpoint in current API";
  const notExposed = "Defense panel not exposed by backend";

  return (
    <section>
      <h1>Defense</h1>
      <p className="trisla-subtitle">No defense-specific API in current backend; structure reserved for future use.</p>
      <div className="trisla-cards-grid">
        <section className="trisla-status-card" aria-label="Admission Protection">
          <h2>Admission Protection</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{noEndpoint}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Observed source</dt>
              <dd>{notExposed}</dd>
            </div>
          </dl>
        </section>

        <section className="trisla-status-card" aria-label="Runtime Integrity">
          <h2>Runtime Integrity</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{noEndpoint}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Observed source</dt>
              <dd>{notExposed}</dd>
            </div>
          </dl>
        </section>

        <section className="trisla-status-card" aria-label="Blockchain Trust Layer">
          <h2>Blockchain Trust Layer</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{noEndpoint}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Observed source</dt>
              <dd>{notExposed}</dd>
            </div>
          </dl>
        </section>

        <section className="trisla-status-card" aria-label="SLA Protection Status">
          <h2>SLA Protection Status</h2>
          <dl>
            <div className="trisla-status-row">
              <dt>Status</dt>
              <dd>{noEndpoint}</dd>
            </div>
            <div className="trisla-status-row">
              <dt>Observed source</dt>
              <dd>{notExposed}</dd>
            </div>
          </dl>
        </section>
      </div>
    </section>
  );
}
