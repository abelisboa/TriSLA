import React, { useState, useEffect } from 'react'
import MainLayout from '../layout/MainLayout'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'

const API = import.meta.env.VITE_API_URL || 'http://localhost:5000'

interface Metric {
  name: string
  value: number
}

interface SliceMetrics {
  cpu: number | null
  memory: number | null
  latency: number | null
  jitter: number | null
  throughput: number | null
  availability: number | null
}

interface TimeSeriesPoint {
  time: number
  value: number
}

export default function MetricsPage() {
  const [slices, setSlices] = useState<{ name: string, active: boolean }[]>([])
  const [selectedSlice, setSelectedSlice] = useState<string>('')
  const [selectedDomain, setSelectedDomain] = useState<string>('all')
  const [timeRange, setTimeRange] = useState<string>('5m')
  const [metrics, setMetrics] = useState<SliceMetrics | null>(null)
  const [timeseriesData, setTimeseriesData] = useState<TimeSeriesPoint[]>([])
  const [selectedMetric, setSelectedMetric] = useState<string>('cpu')
  const [loading, setLoading] = useState<boolean>(false)

  // Fetch available slices
  useEffect(() => {
    const fetchSlices = async () => {
      try {
        const response = await fetch(`${API}/api/prometheus/metrics/slices`)
        const data = await response.json()
        if (data.status === 'ok' && data.slices) {
          setSlices(data.slices)
          if (data.slices.length > 0 && !selectedSlice) {
            setSelectedSlice(data.slices[0].name)
          }
        }
      } catch (error) {
        console.error('Error fetching slices:', error)
      }
    }

    fetchSlices()
    const interval = setInterval(fetchSlices, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  // Fetch metrics for selected slice
  useEffect(() => {
    if (!selectedSlice) return

    const fetchMetrics = async () => {
      setLoading(true)
      try {
        const response = await fetch(`${API}/api/prometheus/metrics/slice/${selectedSlice}`)
        const data = await response.json()
        if (data.status === 'ok' && data.metrics) {
          setMetrics(data.metrics)
        }
      } catch (error) {
        console.error('Error fetching metrics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [selectedSlice])

  // Fetch timeseries data
  useEffect(() => {
    if (!selectedSlice || !selectedMetric) return

    const fetchTimeseries = async () => {
      try {
        // Convert timeRange to minutes
        let rangeMinutes = 5
        if (timeRange === '1h') rangeMinutes = 60
        if (timeRange === '24h') rangeMinutes = 1440

        const response = await fetch(
          `${API}/api/prometheus/metrics/timeseries?metric=${selectedMetric}&slice_name=${selectedSlice}&range_minutes=${rangeMinutes}`
        )
        const data = await response.json()
        
        if (data && data.data && data.data.result && data.data.result.length > 0) {
          const values = data.data.result[0].values || []
          setTimeseriesData(
            values.map((v: [number, string]) => ({
              time: v[0] * 1000, // Convert to milliseconds for JS Date
              value: parseFloat(v[1])
            }))
          )
        } else {
          setTimeseriesData([])
        }
      } catch (error) {
        console.error('Error fetching timeseries:', error)
        setTimeseriesData([])
      }
    }

    fetchTimeseries()
  }, [selectedSlice, selectedMetric, timeRange])

  // Format metrics for display
  const formatMetricValue = (value: number | null, metric: string): string => {
    if (value === null) return 'N/A'
    
    switch (metric) {
      case 'cpu':
        return `${value.toFixed(2)}%`
      case 'memory':
        return `${value.toFixed(0)} MB`
      case 'latency':
        return `${value.toFixed(2)} ms`
      case 'jitter':
        return `${value.toFixed(2)} ms`
      case 'throughput':
        return `${value.toFixed(2)} Mbps`
      case 'availability':
        return `${(value * 100).toFixed(2)}%`
      default:
        return `${value}`
    }
  }

  // Convert metrics to array for bar chart
  const metricsArray = metrics
    ? Object.entries(metrics)
        .filter(([key]) => key !== 'availability') // Handle availability separately
        .map(([key, value]) => ({
          name: key,
          value: value || 0
        }))
    : []

  return (
    <MainLayout>
      <section id="metrics">
        <h2 className="text-xl font-semibold mb-3">Métricas</h2>
        
        <div className="bg-white rounded-xl shadow-soft p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Slice</label>
              <select 
                className="w-full border rounded-lg p-2"
                value={selectedSlice}
                onChange={(e) => setSelectedSlice(e.target.value)}
              >
                <option value="">Selecione um slice</option>
                {slices.map((slice) => (
                  <option key={slice.name} value={slice.name}>
                    {slice.name} {slice.active ? '(ativo)' : ''}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-gray-600 mb-1">Domínio</label>
              <select 
                className="w-full border rounded-lg p-2"
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
              >
                <option value="all">Todos</option>
                <option value="RAN">RAN</option>
                <option value="Transport">Transport</option>
                <option value="Core">Core</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-gray-600 mb-1">Métrica</label>
              <select 
                className="w-full border rounded-lg p-2"
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
              >
                <option value="cpu">CPU</option>
                <option value="memory">Memória</option>
                <option value="latency">Latência</option>
                <option value="jitter">Jitter</option>
                <option value="throughput">Throughput</option>
                <option value="availability">Disponibilidade</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-gray-600 mb-1">Período</label>
              <select 
                className="w-full border rounded-lg p-2"
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
              >
                <option value="5m">5 minutos</option>
                <option value="1h">1 hora</option>
                <option value="24h">24 horas</option>
              </select>
            </div>
          </div>
          
          {!selectedSlice ? (
            <div className="text-center py-8 text-gray-500">Selecione um slice para visualizar métricas</div>
          ) : loading ? (
            <div className="text-center py-8 text-gray-500">Carregando métricas...</div>
          ) : (
            <div>
              <h3 className="text-lg font-medium mb-4">Métricas para {selectedSlice}</h3>
              
              {/* Gauges for SLO metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Latência</div>
                  <div className="text-2xl font-semibold">
                    {formatMetricValue(metrics?.latency || null, 'latency')}
                  </div>
                  <div className="text-xs text-gray-500">Meta: &lt;= 10ms</div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Throughput</div>
                  <div className="text-2xl font-semibold">
                    {formatMetricValue(metrics?.throughput || null, 'throughput')}
                  </div>
                  <div className="text-xs text-gray-500">Meta: &gt;= 100 Mbps</div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-600 mb-1">Disponibilidade</div>
                  <div className="text-2xl font-semibold">
                    {formatMetricValue(metrics?.availability || null, 'availability')}
                  </div>
                  <div className="text-xs text-gray-500">Meta: &gt;= 99.9%</div>
                </div>
              </div>
              
              {/* Resource metrics bar chart */}
              <div className="mb-6">
                <h4 className="text-md font-medium mb-2">Recursos</h4>
                <div style={{ width: '100%', height: 200 }}>
                  <ResponsiveContainer>
                    <BarChart data={metricsArray}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip formatter={(value, name) => formatMetricValue(value as number, name as string)} />
                      <Bar dataKey="value" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              {/* Time series chart */}
              <div>
                <h4 className="text-md font-medium mb-2">Série Temporal: {selectedMetric}</h4>
                {timeseriesData.length === 0 ? (
                  <div className="text-center py-4 text-gray-500">Sem dados de série temporal disponíveis</div>
                ) : (
                  <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer>
                      <LineChart data={timeseriesData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="time" 
                          tickFormatter={(time) => new Date(time).toLocaleTimeString()} 
                        />
                        <YAxis />
                        <Tooltip 
                          labelFormatter={(time) => new Date(time as number).toLocaleString()}
                          formatter={(value) => formatMetricValue(value as number, selectedMetric)}
                        />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke="#8884d8" 
                          dot={false} 
                          name={selectedMetric} 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </section>
    </MainLayout>
  )
}
