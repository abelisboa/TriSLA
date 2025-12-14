/**
 * Configuração centralizada da API do Portal TriSLA
 * 
 * Fonte única da verdade para URL da API - sem hardcode de IP/NodePort
 * 
 * Prioridade:
 * 1. NEXT_PUBLIC_TRISLA_API_BASE_URL (variável de ambiente)
 * 2. Fallback para localhost:8001/api/v1 (modo demo via túnel SSH)
 * 
 * Server-side (SSR, API Routes, server-side fetch):
 *   - INTERNAL_API_URL: http://trisla-portal-backend:8001/api/v1 (cluster interno)
 *
 * Client-side (browser):
 *   - NEXT_PUBLIC_TRISLA_API_BASE_URL: http://localhost:8001/api/v1 (via túnel SSH)
 */

/**
 * Helper para obter URL da API no server-side (SSR, API Routes)
 * Usa INTERNAL_API_URL para comunicação interna do cluster
 */
export const getServerApiUrl = (): string => {
  return process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_TRISLA_API_BASE_URL || 'http://localhost:8001/api/v1';
};

/**
 * Helper para obter URL da API no client-side (browser)
 * Usa NEXT_PUBLIC_TRISLA_API_BASE_URL (sem fallback para IP interno)
 */
export const getBrowserApiUrl = (): string => {
  return process.env.NEXT_PUBLIC_TRISLA_API_BASE_URL || 'http://localhost:8001/api/v1';
};

/**
 * URL base da API - diferencia automaticamente entre server e client
 */
export const API_BASE_URL =
  typeof window !== 'undefined'
    ? getBrowserApiUrl()
    : getServerApiUrl();

export const API_ENDPOINTS = {
  health: '/health',
  sla: {
    interpret: '/api/v1/sla/interpret',
    submit: '/api/v1/sla/submit',
    status: (id: string) => `/api/v1/sla/status/${id}`,
    metrics: (id: string) => `/api/v1/sla/metrics/${id}`,
  },
} as const;

