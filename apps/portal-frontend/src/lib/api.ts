export type ApiError = {
  status: number;
  message: string;
  url: string;
  bodyText?: string;
};

function apiBase() {
  // Browser: use same-origin Next.js rewrites (/api/v1 -> backend service)
  // Server (standalone): allow direct service URL override when needed
  if (typeof window === 'undefined') {
    return process.env.BACKEND_URL || 'http://trisla-portal-backend:8001/api/v1';
  }
  return '/api/v1';
}

async function readBodyTextSafe(res: Response) {
  try {
    return await res.text();
  } catch {
    return undefined;
  }
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const url = `${apiBase()}${path.startsWith('/') ? '' : '/'}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      'content-type': 'application/json',
      ...(init?.headers || {}),
    },
  });

  if (!res.ok) {
    const bodyText = await readBodyTextSafe(res);
    const err: ApiError = {
      status: res.status,
      message: `HTTP ${res.status} ${res.statusText}`,
      url,
      bodyText,
    };
    throw err;
  }

  return (await res.json()) as T;
}

/** Endpoint paths (no URLs changed). Used by apiRequest for compatibility. */
const API_PATHS: Record<string, string> = {
  GLOBAL_HEALTH: '/health/global',
  PROMETHEUS_SUMMARY: '/prometheus/summary',
  MODULES: '/modules/',
  CORE_METRICS_REALTIME: '/core-metrics/realtime',
  TRANSPORT_METRICS: '/modules/transport/metrics',
  RAN_METRICS: '/modules/ran/metrics',
  NASP_DIAGNOSTICS: '/nasp/diagnostics',
  SLA_INTERPRET: '/sla/interpret',
  SLA_SUBMIT: '/sla/submit',
};

type RequestOptions = { method?: string; body?: unknown };

/** Compatibility layer: same endpoints, no URL change. */
export async function apiRequest<T = unknown>(
  key: keyof typeof API_PATHS,
  options: RequestOptions = {}
): Promise<T> {
  const path = API_PATHS[key as string];
  const method = (options.method || 'GET').toUpperCase();
  const init: RequestInit = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (method !== 'GET' && options.body != null) {
    init.body = JSON.stringify(options.body);
  }
  return apiFetch<T>(path, init);
}

export const portalApi = {
  getHealthGlobal() {
    return apiFetch<any>('/health/global');
  },
  getPrometheusSummary() {
    return apiFetch<any>('/prometheus/summary');
  },
  getModules() {
    return apiFetch<any>('/modules/');
  },
  getCoreMetricsRealtime() {
    return apiFetch<any>('/core-metrics/realtime');
  },
  getTransportMetrics() {
    return apiFetch<any>('/modules/transport/metrics');
  },
  getRanMetrics() {
    return apiFetch<any>('/modules/ran/metrics');
  },
  getNaspDiagnostics() {
    return apiFetch<any>('/nasp/diagnostics');
  },
  interpretSla(payload: Record<string, any>) {
    return apiFetch<any>('/sla/interpret', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  submitSla(payload: Record<string, any>) {
    return apiFetch<any>('/sla/submit', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};

