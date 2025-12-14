import { API_BASE } from "./config";

export interface APIError {
  message: string
  status?: number
  detail?: string
  module?: string
}

/**
 * Cliente de API padronizado - usa apenas /api/v1 (same-origin)
 */
export async function apiFetch(
  path: string,
  options?: RequestInit
): Promise<any> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
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
      
      const error: APIError = {
        message: errorDetail,
        status: res.status,
        detail: errorDetail,
      };
      
      throw error;
    }

    const contentType = res.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      return {};
    }

    return res.json();
  } catch (error: any) {
    clearTimeout(timeout);
    
    if (error.status) {
      throw error;
    }
    
    if (error.name === 'AbortError' || error.message?.includes('aborted')) {
      throw {
        message: 'Timeout ao conectar com o backend',
        status: 0,
        detail: 'Request timeout após 30 segundos',
      } as APIError;
    }
    
    throw {
      message: error.message || 'Erro ao conectar com o backend',
      status: 0,
      detail: error.message || 'Network error',
    } as APIError;
  } finally {
    clearTimeout(timeout);
  }
}

// Compatibilidade: manter api() e métodos para código existente
export async function api(endpoint: string, options: RequestInit = {}): Promise<any> {
  return apiFetch(endpoint, options);
}

// Métodos de compatibilidade
type ApiClient = typeof api & {
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

const apiObj = api as ApiClient;
apiObj.getContract = (id: string) => apiFetch(`/contracts/${id}`)
apiObj.getContractViolations = (id: string) => apiFetch(`/contracts/${id}/violations`)
apiObj.getContractRenegotiations = (id: string) => apiFetch(`/contracts/${id}/renegotiations`)
apiObj.getContractPenalties = (id: string) => apiFetch(`/contracts/${id}/penalties`)
apiObj.getContracts = () => apiFetch(`/contracts`)
apiObj.getXAIExplanations = () => apiFetch(`/xai/explanations`)
apiObj.getModule = (moduleName: string) => apiFetch(`/modules/${moduleName}`)
apiObj.getModuleMetrics = (moduleName: string) => apiFetch(`/modules/${moduleName}/metrics`)
apiObj.getModuleStatus = (moduleName: string) => apiFetch(`/modules/${moduleName}/status`)
apiObj.getModules = () => apiFetch(`/modules`)
apiObj.getHealthGlobal = () => apiFetch(`/health/global`)

export const apiClient = apiObj;
export default apiObj;
