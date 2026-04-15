export const API_ENDPOINTS = {
  GLOBAL_HEALTH: "/api/v1/health",
  PROMETHEUS_SUMMARY: "/api/v1/prometheus/summary",
  MODULES: "/api/v1/modules/",
  CORE_METRICS_REALTIME: "/api/v1/core-metrics/realtime",
  TRANSPORT_METRICS: "/api/v1/modules/transport/metrics",
  RAN_METRICS: "/api/v1/modules/ran/metrics",
  NASP_DIAGNOSTICS: "/api/v1/nasp/diagnostics",
  SLA_INTERPRET: "/api/v1/sla/interpret",
  SLA_SUBMIT: "/api/v1/sla/submit",
} as const;

export type ApiEndpointKey = keyof typeof API_ENDPOINTS;

