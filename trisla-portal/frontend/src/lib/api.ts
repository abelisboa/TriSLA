/**
 * API Client - TriSLA Portal Light
 * Cliente para comunicação com o backend usando same-origin (/api/v1)
 * 
 * CORREÇÃO DEFINITIVA: Todas as chamadas usam /api/v1 (same-origin)
 * O Next.js faz proxy interno via rewrites em next.config.js
 */

import { API_BASE } from "./config";

export interface APIError {
  message: string
  status?: number
  detail?: string
  module?: string
}

/**
 * Helper para criar timeout com AbortController
 */
function withTimeout(ms = 30000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), ms);
  return { controller, id };
}

/**
 * GET request com timeout
 */
export async function apiGet<T>(path: string, timeoutMs = 30000): Promise<T> {
  const { controller, id } = withTimeout(timeoutMs);
  try {
    const res = await fetch(`${API_BASE}${path}`, { signal: controller.signal });
    if (!res.ok) {
      let errorDetail: string = '';
      try {
        const errorData = await res.json();
        errorDetail = errorData.detail || errorData.error || errorData.message || res.statusText;
      } catch {
        errorDetail = res.statusText;
      }
      throw new Error(`GET ${path} -> ${res.status}: ${errorDetail}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(id);
  }
}

/**
 * POST request com timeout
 */
export async function apiPost<T>(path: string, body: unknown, timeoutMs = 30000): Promise<T> {
  const { controller, id } = withTimeout(timeoutMs);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!res.ok) {
      let errorDetail: string = '';
      try {
        const errorData = await res.json();
        errorDetail = errorData.detail || errorData.error || errorData.message || res.statusText;
      } catch {
        errorDetail = res.statusText;
      }
      throw new Error(`POST ${path} -> ${res.status}: ${errorDetail}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(id);
  }
}

/**
 * Tipo para o cliente API completo
 */
type ApiClientFunction = ((endpoint: string, options?: RequestInit) => Promise<any>) & {
  getContract: (id: string) => Promise<any>
  getContractViolations: (id: string) => Promise<any>
  getContractRenegotiations: (id: string) => Promise<any>
  getContractPenalties: (id: string) => Promise<any>
  getContracts: () => Promise<any>
  getXAIExplanations: () => Promise<any>
  getModule: (moduleName: string) => Promise<any>
  getModuleMetrics: (moduleName: string) => Promise<any>
  getModuleStatus: (moduleName: string) => Promise<any>
  getModules: () => Promise<any>
  getHealthGlobal: () => Promise<any>
}

/**
 * Compatibilidade: função api() genérica (mantém compatibilidade com código existente)
 */
async function apiFunction(endpoint: string, options: RequestInit = {}): Promise<any> {
  const { controller, id } = withTimeout(30000);
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    signal: controller.signal,
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`, defaultOptions);
    clearTimeout(id);
    
    if (!response.ok) {
      let errorDetail: string = '';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorData.error || errorData.message || response.statusText;
      } catch {
        errorDetail = response.statusText;
      }
      
      const error: APIError = {
        message: errorDetail,
        status: response.status,
        detail: errorDetail,
      };
      
      // Se o erro contém informações de módulo, extrair
      if (errorDetail.includes('SEM-CSMF') || errorDetail.includes('ML-NSMF') || 
          errorDetail.includes('Decision Engine') || errorDetail.includes('BC-NSSMF') ||
          errorDetail.includes('SLA-Agent Layer')) {
        error.module = errorDetail.split(':')[0];
      }
      
      throw error;
    }

    // Se resposta vazia, retornar objeto vazio
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      return {};
    }

    return await response.json();
  } catch (error: any) {
    clearTimeout(id);
    
    // Se já é um APIError, relançar
    if (error.status) {
      throw error;
    }
    
    // Tratamento de timeout ou erro de rede
    if (error.name === 'AbortError' || error.message?.includes('aborted')) {
      throw {
        message: 'Timeout ao conectar com o backend',
        status: 0,
        detail: 'Request timeout após 30 segundos',
      } as APIError;
    }
    
    // Erro de rede ou outro erro
    throw {
      message: error.message || 'Erro ao conectar com o backend',
      status: 0,
      detail: error.message || 'Network error',
    } as APIError;
  }
}

// Criar objeto api com métodos
const api = apiFunction as ApiClientFunction

// Adicionar métodos ao objeto api para compatibilidade
api.getContract = (id: string) => apiGet(`/contracts/${id}`)
api.getContractViolations = (id: string) => apiGet(`/contracts/${id}/violations`)
api.getContractRenegotiations = (id: string) => apiGet(`/contracts/${id}/renegotiations`)
api.getContractPenalties = (id: string) => apiGet(`/contracts/${id}/penalties`)
api.getContracts = () => apiGet(`/contracts`)
api.getXAIExplanations = () => apiGet(`/xai/explanations`)
api.getModule = (moduleName: string) => apiGet(`/modules/${moduleName}`)
api.getModuleMetrics = (moduleName: string) => apiGet(`/modules/${moduleName}/metrics`)
api.getModuleStatus = (moduleName: string) => apiGet(`/modules/${moduleName}/status`)
api.getModules = () => apiGet(`/modules`)
api.getHealthGlobal = () => apiGet(`/health/global`)

// Export para compatibilidade
export const apiClient = api

// Export named e default para compatibilidade
export { api }
export default api
