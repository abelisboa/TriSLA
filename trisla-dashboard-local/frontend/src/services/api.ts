import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Prometheus API
export const prometheusApi = {
  health: () => api.get('/api/prometheus/health'),
  
  slices: () => api.get('/api/prometheus/metrics/slices'),
  
  system: () => api.get('/api/prometheus/metrics/system'),
  
  jobs: () => api.get('/api/prometheus/metrics/jobs'),
  
  timeseries: (metric: string = 'http_requests_total', rangeMinutes: number = 60, step: string = '15s') =>
    api.get('/api/prometheus/metrics/timeseries', {
      params: { metric, range_minutes: rangeMinutes, step },
    }),
  
  query: (query: string) =>
    api.post('/api/prometheus/query', null, {
      params: { query },
    }),
}
