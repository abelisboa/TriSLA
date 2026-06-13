import {
  API_V1_PATHS,
  BACKEND_ROOT_PATHS,
  type ApiEndpointKey,
} from './endpoints';
import type {
  RevalidateTelemetryRequest,
  RevalidateTelemetryResponse,
  SlaRuntimeStatusResponse,
} from './runtimeSupervision';

export type ApiError = {
  status: number;
  message: string;
  url: string;
  bodyText?: string;
};

const DEFAULT_TIMEOUT_MS = 30_000;

const BACKEND_ROOT_KEYS = new Set<string>(Object.keys(BACKEND_ROOT_PATHS));

/** Optional fetch — non-critical endpoints (e.g. prometheus summary). */
export const OPTIONAL_ENDPOINTS = new Set<ApiEndpointKey>(['PROMETHEUS_SUMMARY']);

function trimSlash(s: string): string {
  return s.replace(/\/$/, '');
}

/** Public backend root for browser direct access (NodePort / SSH tunnel). */
export function publicBackendRoot(): string | null {
  const v = process.env.NEXT_PUBLIC_TRISLA_API_BASE_URL?.trim();
  return v ? trimSlash(v) : null;
}

/** Server-side backend root (K8s service or explicit override). */
export function backendRootUrl(): string {
  const candidates = [
    process.env.TRISLA_API_BASE_URL,
    process.env.BACKEND_URL,
  ];
  for (const raw of candidates) {
    if (!raw?.trim()) continue;
    const v = raw.trim();
    if (v.startsWith('http')) {
      return trimSlash(v.replace(/\/api\/v1\/?$/, ''));
    }
  }
  return 'http://trisla-portal-backend:8001';
}

function resolveApiV1Path(path: string): string {
  const rel = path.startsWith('/') ? path : `/${path}`;
  const publicRoot = typeof window !== 'undefined' ? publicBackendRoot() : null;
  if (publicRoot) return `${publicRoot}/api/v1${rel}`;
  if (typeof window !== 'undefined') return `/api/v1${rel}`;
  return `${backendRootUrl()}/api/v1${rel}`;
}

function resolveRequestUrl(key: ApiEndpointKey): string {
  const publicRoot = typeof window !== 'undefined' ? publicBackendRoot() : null;

  if (BACKEND_ROOT_KEYS.has(key)) {
    const rel = BACKEND_ROOT_PATHS[key as keyof typeof BACKEND_ROOT_PATHS];
    if (publicRoot) return `${publicRoot}${rel}`;
    if (typeof window !== 'undefined') return rel;
    return `${backendRootUrl()}${rel}`;
  }

  const rel = API_V1_PATHS[key as keyof typeof API_V1_PATHS];
  if (publicRoot) return `${publicRoot}/api/v1${rel}`;
  if (typeof window !== 'undefined') return `/api/v1${rel}`;
  return `${backendRootUrl()}/api/v1${rel}`;
}

async function readBodyTextSafe(res: Response): Promise<string | undefined> {
  try {
    return await res.text();
  } catch {
    return undefined;
  }
}

function devLog(message: string, detail?: unknown): void {
  if (process.env.NODE_ENV === 'development') {
    // eslint-disable-next-line no-console
    console.debug(`[trisla-api] ${message}`, detail ?? '');
  }
}

export function isApiError(err: unknown): err is ApiError {
  return (
    typeof err === 'object' &&
    err !== null &&
    'status' in err &&
    'url' in err &&
    typeof (err as ApiError).status === 'number'
  );
}

export function formatApiError(err: unknown): string {
  if (isApiError(err)) {
    if (err.bodyText) {
      try {
        const parsed = JSON.parse(err.bodyText) as { detail?: unknown };
        if (typeof parsed.detail === 'string') return parsed.detail;
        if (parsed.detail != null) return JSON.stringify(parsed.detail);
      } catch {
        return `${err.message} — ${err.bodyText.slice(0, 240)}`;
      }
    }
    return err.message;
  }
  if (err instanceof Error) return err.message;
  return 'error retrieving source data';
}

export async function apiFetch<T>(
  url: string,
  init?: RequestInit,
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    devLog(`${init?.method ?? 'GET'} ${url}`);
    const res = await fetch(url, {
      ...init,
      signal: controller.signal,
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
  } catch (e) {
    if (e instanceof Error && e.name === 'AbortError') {
      throw {
        status: 408,
        message: `Request timeout after ${timeoutMs}ms`,
        url,
      } satisfies ApiError;
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

type RequestOptions = { method?: string; body?: unknown; timeoutMs?: number };

export async function apiRequest<T = unknown>(
  key: ApiEndpointKey,
  options: RequestOptions = {},
): Promise<T> {
  const url = resolveRequestUrl(key);
  const method = (options.method || 'GET').toUpperCase();
  const init: RequestInit = { method };
  if (method !== 'GET' && method !== 'HEAD' && options.body != null) {
    init.body = JSON.stringify(options.body);
  }
  return apiFetch<T>(url, init, options.timeoutMs);
}

/** Non-throwing variant for optional backend features. */
export async function apiRequestOptional<T = unknown>(
  key: ApiEndpointKey,
  options: RequestOptions = {},
): Promise<{ data: T | null; error: ApiError | null }> {
  try {
    const data = await apiRequest<T>(key, options);
    return { data, error: null };
  } catch (e) {
    const error: ApiError = isApiError(e)
      ? e
      : { status: 0, message: formatApiError(e), url: resolveRequestUrl(key) };
    devLog(`optional fail ${key}`, error);
    return { data: null, error };
  }
}

export const portalApi = {
  getHealthGlobal() {
    return apiRequest<Record<string, unknown>>('GLOBAL_HEALTH');
  },
  getPrometheusSummaryOptional() {
    return apiRequestOptional<Record<string, unknown>>('PROMETHEUS_SUMMARY');
  },
  getModules() {
    return apiRequest<unknown>('MODULES');
  },
  getTransportMetrics() {
    return apiRequest<Record<string, unknown>>('TRANSPORT_METRICS');
  },
  getRanMetrics() {
    return apiRequest<Record<string, unknown>>('RAN_METRICS');
  },
  getNaspDiagnostics() {
    return apiRequest<Record<string, unknown>>('NASP_DIAGNOSTICS');
  },
  interpretSla(payload: Record<string, unknown>) {
    return apiRequest<Record<string, unknown>>('SLA_INTERPRET', {
      method: 'POST',
      body: payload,
    });
  },
  submitSla(payload: Record<string, unknown>) {
    return apiRequest<Record<string, unknown>>('SLA_SUBMIT', {
      method: 'POST',
      body: payload,
    });
  },
  getSlaStatus(intentId: string) {
    const encoded = encodeURIComponent(intentId);
    return apiFetch<SlaRuntimeStatusResponse>(
      resolveApiV1Path(`/sla/status/${encoded}`),
    );
  },
  revalidateTelemetry(body: RevalidateTelemetryRequest) {
    return apiRequest<RevalidateTelemetryResponse>('SLA_REVALIDATE', {
      method: 'POST',
      body,
    });
  },
};
