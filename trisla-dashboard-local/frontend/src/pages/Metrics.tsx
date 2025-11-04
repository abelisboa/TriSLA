import { useQuery } from '@tanstack/react-query'
import { prometheusApi } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Metrics() {
  const { data: timeseriesData } = useQuery({
    queryKey: ['prometheus', 'timeseries', 'http_requests_total'],
    queryFn: () => prometheusApi.timeseries('http_requests_total', 60).then(res => res.data),
  })

  const { data: system } = useQuery({
    queryKey: ['prometheus', 'system'],
    queryFn: () => prometheusApi.system().then(res => res.data),
  })

  // Transformar dados para formato do Recharts
  const chartData = timeseriesData?.data?.map((item: any) => ({
    time: new Date(item.time).toLocaleTimeString(),
    value: parseFloat(item.value) || 0,
  })) || []

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Métricas Detalhadas</h2>
        <p className="mt-2 text-gray-600">Visualização de métricas em tempo real</p>
      </div>

      {/* Gráfico de Requisições HTTP */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Taxa de Requisições HTTP (últimas 60 minutos)
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} name="Requisições/s" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Métricas do Sistema */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Componentes</h3>
          <div className="space-y-2">
            {system?.components_up?.map((item: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{item.metric?.job || 'Unknown'}</span>
                <span className={`text-sm font-medium ${item.value[1] === '1' ? 'text-green-600' : 'text-red-600'}`}>
                  {item.value[1] === '1' ? '🟢 UP' : '🔴 DOWN'}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Uso de CPU</h3>
          <div className="space-y-2">
            {system?.cpu_usage?.slice(0, 5).map((item: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{item.metric?.pod || 'Unknown'}</span>
                <span className="text-sm font-medium text-gray-900">
                  {parseFloat(item.value[1] || '0').toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
