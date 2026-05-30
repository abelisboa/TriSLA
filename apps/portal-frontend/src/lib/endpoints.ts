/** Relative paths under /api/v1 (Portal Backend). */
export const API_V1_PATHS = {
  GLOBAL_HEALTH: "/health/global",
  PROMETHEUS_SUMMARY: "/prometheus/summary",
  RAN_I1_METRICS: "/interfaces/ran-i1/metrics",
  TN_I1_METRICS: "/interfaces/tn-i1/metrics",
  CN_I1_METRICS: "/interfaces/cn-i1/metrics",
  MODULES: "/modules/",
  TRANSPORT_METRICS: "/modules/transport/metrics",
  RAN_METRICS: "/modules/ran/metrics",
  SLA_INTERPRET: "/sla/interpret",
  SLA_SUBMIT: "/sla/submit",
  SLA_REVALIDATE: "/sla/revalidate-telemetry",
} as const;

/** Backend root paths (not under /api/v1). */
export const BACKEND_ROOT_PATHS = {
  NASP_DIAGNOSTICS: "/nasp/diagnostics",
} as const;

export type ApiV1EndpointKey = keyof typeof API_V1_PATHS;
export type BackendRootEndpointKey = keyof typeof BACKEND_ROOT_PATHS;

export type ApiEndpointKey = ApiV1EndpointKey | BackendRootEndpointKey;

/** @deprecated Use API_V1_PATHS / BACKEND_ROOT_PATHS via api client. */
export const API_ENDPOINTS = {
  GLOBAL_HEALTH: "/api/v1/health/global",
  PROMETHEUS_SUMMARY: "/api/v1/prometheus/summary",
  RAN_I1_METRICS: "/api/v1/interfaces/ran-i1/metrics",
  TN_I1_METRICS: "/api/v1/interfaces/tn-i1/metrics",
  CN_I1_METRICS: "/api/v1/interfaces/cn-i1/metrics",
  MODULES: "/api/v1/modules/",
  TRANSPORT_METRICS: "/api/v1/modules/transport/metrics",
  RAN_METRICS: "/api/v1/modules/ran/metrics",
  NASP_DIAGNOSTICS: BACKEND_ROOT_PATHS.NASP_DIAGNOSTICS,
  SLA_INTERPRET: "/api/v1/sla/interpret",
  SLA_SUBMIT: "/api/v1/sla/submit",
} as const;
