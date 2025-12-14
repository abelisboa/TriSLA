/**
 * Configuração centralizada da API do Portal TriSLA
 * 
 * CORREÇÃO DEFINITIVA: Usa same-origin (/api/v1) e Next.js faz proxy interno
 * 
 * O browser sempre chama /api/v1 no mesmo host do Portal.
 * O Next.js faz rewrite interno para o backend via Service Kubernetes.
 */

/**
 * Base URL da API - sempre same-origin (sem IP hardcoded)
 * O Next.js faz proxy via rewrites em next.config.js
 */
export const API_BASE = "/api/v1";

export const API_ENDPOINTS = {
  health: '/health',
  sla: {
    interpret: '/api/v1/sla/interpret',
    submit: '/api/v1/sla/submit',
    status: (id: string) => `/api/v1/sla/status/${id}`,
    metrics: (id: string) => `/api/v1/sla/metrics/${id}`,
  },
} as const;

