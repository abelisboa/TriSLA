/**
 * Helpers para validação e extração de dados do Prometheus
 */

export interface PrometheusValue {
  timestamp: number | string
  value: string | number
}

export interface PrometheusMetric {
  metric: Record<string, string>
  value?: PrometheusValue | [number, string]
  values?: PrometheusValue[]
}

/**
 * Extrai valor de uma métrica Prometheus de forma segura
 */
export function extractPrometheusValue(metric: any): string {
  if (!metric || !metric.value) {
    return '0'
  }
  
  // Prometheus retorna [timestamp, value] ou {timestamp, value}
  if (Array.isArray(metric.value)) {
    return metric.value[1] || '0'
  }
  
  if (typeof metric.value === 'object' && 'value' in metric.value) {
    return String(metric.value.value || '0')
  }
  
  return String(metric.value || '0')
}

/**
 * Extrai valor numérico de uma métrica
 */
export function extractPrometheusNumeric(metric: any, decimals: number = 1): string {
  const valueStr = extractPrometheusValue(metric)
  const numValue = parseFloat(valueStr)
  
  if (isNaN(numValue)) {
    return 'N/A'
  }
  
  return numValue.toFixed(decimals)
}

/**
 * Extrai valor numérico como porcentagem
 */
export function extractPrometheusPercent(metric: any, decimals: number = 1): string {
  const valueStr = extractPrometheusValue(metric)
  const numValue = parseFloat(valueStr)
  
  if (isNaN(numValue)) {
    return 'N/A'
  }
  
  return `${numValue.toFixed(decimals)}%`
}

/**
 * Valida e formata data
 */
export function formatTime(time: string | number | Date): string {
  try {
    const date = new Date(time)
    if (isNaN(date.getTime())) {
      return 'Invalid Date'
    }
    return date.toLocaleTimeString()
  } catch {
    return 'Invalid Date'
  }
}

/**
 * Verifica se um array de métricas existe e não está vazio
 */
export function hasMetrics(data: any[] | undefined | null): boolean {
  return Array.isArray(data) && data.length > 0
}

/**
 * Safe map para arrays de métricas
 */
export function safeMapMetrics<T>(
  data: any[] | undefined | null,
  mapper: (item: any, idx: number) => T
): T[] {
  if (!hasMetrics(data)) {
    return []
  }
  return data!.map(mapper)
}





