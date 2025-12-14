/**
 * Configuração de runtime do Portal TriSLA
 * 
 * Fonte única da verdade para URL da API - Kubernetes-safe por padrão
 * 
 * Prioridade:
 * 1. NEXT_PUBLIC_TRISLA_API_BASE_URL (variável de ambiente definida no build)
 * 2. Fallback para Service Kubernetes interno (http://trisla-portal-backend:8001/api/v1)
 * 
 * IMPORTANTE:
 * - Este arquivo NÃO deve ter fallback para localhost
 * - localhost só funciona em desenvolvimento local ou via túnel SSH
 * - Em Kubernetes, o default deve ser o Service interno
 */

/**
 * URL base da API para uso em runtime
 * 
 * Client-side (browser): usa NEXT_PUBLIC_TRISLA_API_BASE_URL se definido,
 *                        caso contrário usa o Service Kubernetes interno
 * 
 * Server-side (SSR): usa INTERNAL_API_URL se definido,
 *                    caso contrário usa o Service Kubernetes interno
 */
export const API_BASE_URL = (() => {
  // Server-side (SSR, API Routes)
  if (typeof window === 'undefined') {
    return process.env.INTERNAL_API_URL ?? 
           process.env.NEXT_PUBLIC_TRISLA_API_BASE_URL ?? 
           'http://trisla-portal-backend:8001/api/v1';
  }
  
  // Client-side (browser)
  return process.env.NEXT_PUBLIC_TRISLA_API_BASE_URL ?? 
         'http://trisla-portal-backend:8001/api/v1';
})();

/**
 * Verificar se estamos em ambiente Kubernetes
 * (útil para logs/debug, mas não usado na lógica principal)
 */
export const isKubernetesEnv = (): boolean => {
  return typeof window === 'undefined' || 
         !process.env.NEXT_PUBLIC_TRISLA_API_BASE_URL?.includes('localhost');
};

