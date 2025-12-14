/**
 * API Client - TriSLA Portal Light
 * Cliente para comunicação com o backend
 */

import { API_BASE_URL } from './runtimeConfig'

// Usar configuração centralizada Kubernetes-safe
export const BACKEND_URL = API_BASE_URL

export interface APIError {
  message: string
  status?: number
  detail?: string
  module?: string
}

/**
 * Tipo para o cliente API como function object
 * Permite chamar api(endpoint) e também api.getContract(id), etc.
 */
type ApiClient = {
  (endpoint: string, options?: RequestInit): Promise<any>
  getContract: (id: string) => Promise<any>
  getContractViolations: (id: string) => Promise<any>
  getContractRenegotiations: (id: string) => Promise<any>
  getContractPenalties: (id: string) => Promise<any>
  getContracts: () => Promise<any>
  getXAIExplanations: () => Promise<any>
  getModule: (moduleName: string) => Promise<any>
  getModuleMetrics: (moduleName: string) => Promise<any>
  getModuleStatus: (moduleName: string) => Promise<any>
  getHealthGlobal: () => Promise<any>
  getModules: () => Promise<any>
}

/**
 * Função base da API com timeout e tratamento robusto de erros
 */
const baseApi = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<any> => {
  const url = `${BACKEND_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
  
  // Timeout de 25 segundos (AbortController)
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 25000)
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    signal: controller.signal,
    ...options,
  }

  try {
    const response = await fetch(url, defaultOptions)
    clearTimeout(timeoutId)
    
    if (!response.ok) {
      let errorDetail: string = ''
      try {
        const errorData = await response.json()
        errorDetail = errorData.detail || errorData.error || errorData.message || response.statusText
      } catch {
        errorDetail = response.statusText
      }
      
      const error: APIError = {
        message: errorDetail,
        status: response.status,
        detail: errorDetail,
      }
      
      // Se o erro contém informações de módulo, extrair
      if (errorDetail.includes('SEM-CSMF') || errorDetail.includes('ML-NSMF') || 
          errorDetail.includes('Decision Engine') || errorDetail.includes('BC-NSSMF') ||
          errorDetail.includes('SLA-Agent Layer')) {
        error.module = errorDetail.split(':')[0]
      }
      
      throw error
    }

    // Se resposta vazia, retornar objeto vazio
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      return {}
    }

    return await response.json()
  } catch (error: any) {
    clearTimeout(timeoutId)
    
    // Se já é um APIError, relançar
    if (error.status) {
      throw error
    }
    
    // Tratamento de timeout ou erro de rede
    if (error.name === 'AbortError' || error.message?.includes('aborted')) {
      throw {
        message: 'Timeout ao conectar com o backend. Verifique se o túnel SSH está ativo.',
        status: 0,
        detail: 'Request timeout após 25 segundos',
      } as APIError
    }
    
    // Erro de rede ou outro erro
    throw {
      message: error.message || 'Erro ao conectar com o backend. Verifique se o túnel SSH está ativo.',
      status: 0,
      detail: error.message || 'Network error',
    } as APIError
  }
}

/**
 * API Client como function object
 * Pode ser chamado como função: api('/endpoint')
 * Ou como objeto com métodos: api.getContract(id)
 */
const api = baseApi as ApiClient

// Métodos específicos de contratos
api.getContract = (id: string) =>
  baseApi(`/contracts/${id}`)

api.getContractViolations = (id: string) =>
  baseApi(`/contracts/${id}/violations`)

api.getContractRenegotiations = (id: string) =>
  baseApi(`/contracts/${id}/renegotiations`)

api.getContractPenalties = (id: string) =>
  baseApi(`/contracts/${id}/penalties`)

api.getContracts = () =>
  baseApi(`/contracts`)

// Métodos de XAI
api.getXAIExplanations = () =>
  baseApi(`/xai/explanations`)

// Métodos de módulos
api.getModule = (moduleName: string) =>
  baseApi(`/modules/${moduleName}`)

api.getModuleMetrics = (moduleName: string) =>
  baseApi(`/modules/${moduleName}/metrics`)

api.getModuleStatus = (moduleName: string) =>
  baseApi(`/modules/${moduleName}/status`)

api.getModules = () =>
  baseApi(`/modules`)

// Métodos de health
api.getHealthGlobal = () =>
  baseApi(`/health/global`)

export default api
export { api }
