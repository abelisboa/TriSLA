/**
 * Configuração centralizada da API do Portal TriSLA
 * 
 * DEPRECATED: Use runtimeConfig.ts para nova lógica Kubernetes-safe
 * 
 * Este arquivo mantém compatibilidade, mas redireciona para runtimeConfig.ts
 */

import { API_BASE_URL as RUNTIME_API_BASE_URL } from './runtimeConfig';

/**
 * URL base da API - usa runtimeConfig.ts (Kubernetes-safe)
 * 
 * @deprecated Use import { API_BASE_URL } from './runtimeConfig' diretamente
 */
export const API_BASE_URL = RUNTIME_API_BASE_URL;

/**
 * Helper para obter URL da API no server-side (SSR, API Routes)
 * @deprecated Use runtimeConfig.ts
 */
export const getServerApiUrl = (): string => {
  return RUNTIME_API_BASE_URL;
};

/**
 * Helper para obter URL da API no client-side (browser)
 * @deprecated Use runtimeConfig.ts
 */
export const getBrowserApiUrl = (): string => {
  return RUNTIME_API_BASE_URL;
};

export const API_ENDPOINTS = {
  health: '/health',
  sla: {
    interpret: '/api/v1/sla/interpret',
    submit: '/api/v1/sla/submit',
    status: (id: string) => `/api/v1/sla/status/${id}`,
    metrics: (id: string) => `/api/v1/sla/metrics/${id}`,
  },
} as const;

