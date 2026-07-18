import React from 'react';

/**
 * TriSLA Observability — Grafana Embed Panel
 * - Objetivo: embutir o dashboard oficial do Grafana sem duplicar dashboards no Portal.
 * - Observação: em produção, recomenda-se configurar o Grafana com allow_embedding,
 *   cookie_samesite e autenticação adequada, ou utilizar backend-proxy.
 */
const GrafanaPanel: React.FC = () => {
  const grafanaUrl = (import.meta as any).env.VITE_GRAFANA_URL || "/grafana/d/trisla-super-dashboard";

  return (
    <div style={{ width: "100%", height: "90vh" }}>
      <iframe
        src={grafanaUrl}
        title="TriSLA Observability Dashboard (Grafana)"
        width="100%"
        height="100%"
        style={{ border: "none" }}
        // sandbox endurece o iframe; pode exigir relaxamento conforme auth do Grafana.
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
      />
    </div>
  );
};

export default GrafanaPanel;
