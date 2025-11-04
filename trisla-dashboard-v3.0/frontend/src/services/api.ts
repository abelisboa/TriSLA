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
  
  system: (sliceName?: string) => api.get('/api/prometheus/metrics/system', {
    params: { slice_name: sliceName },
  }),
  
  sliceMetrics: (sliceName: string, metricType: string = 'all') => 
    api.get(`/api/prometheus/metrics/slice/${sliceName}`, {
      params: { metric_type: metricType },
    }),
  
  timeseries: (metric: string = 'cpu', sliceName?: string, rangeMinutes: number = 5, step: number = 5) =>
    api.get('/api/prometheus/metrics/timeseries', {
      params: { metric, slice_name: sliceName, range_minutes: rangeMinutes, step },
    }),
  
  query: (query: string) =>
    api.post('/api/prometheus/query', { query }),
}

// SEM-NSMF API
export const semNsmfApi = {
  health: () => api.get('/api/sem-nsmf/health'),
}

// Slices API
export const slicesApi = {
  list: () => api.get('/api/slices/list'),
  
  get: (sliceId: number) => api.get(`/api/slices/${sliceId}`),
  
  createFromNPL: (prompt: string) => 
    api.post('/api/slices/nlp/create', { prompt }),
  
  createFromGST: (gstTemplate: any) => 
    api.post('/api/slices/gst/submit', gstTemplate),
  
  deploy: (sliceId: number, nest: any) => 
    api.post('/api/slices/deploy', { slice_id: sliceId, nest }),
  
  delete: (sliceId: number) => 
    api.delete(`/api/slices/${sliceId}`),
}

// Templates API
export const templatesApi = {
  list: (type?: string) => api.get('/api/templates/list', {
    params: { template_type: type },
  }),
  
  get: (templateId: number) => 
    api.get(`/api/templates/${templateId}`),
  
  create: (template: any) => 
    api.post('/api/templates/create', template),
  
  update: (templateId: number, template: any) => 
    api.put(`/api/templates/${templateId}`, template),
  
  delete: (templateId: number) => 
    api.delete(`/api/templates/${templateId}`),
}



