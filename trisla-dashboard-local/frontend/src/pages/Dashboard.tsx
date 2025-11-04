import { useQuery } from '@tanstack/react-query'
import { prometheusApi } from '../services/api'
import MetricCard from '../components/MetricCard'
import { Activity, Package, TrendingUp, AlertCircle } from 'lucide-react'

export default function Dashboard() {
  const { data: health } = useQuery({
    queryKey: ['prometheus', 'health'],
    queryFn: () => prometheusApi.health().then(res => res.data),
  })

  const { data: slices } = useQuery({
    queryKey: ['prometheus', 'slices'],
    queryFn: () => prometheusApi.slices().then(res => res.data),
  })

  const { data: system } = useQuery({
    queryKey: ['prometheus', 'system'],
    queryFn: () => prometheusApi.system().then(res => res.data),
  })

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Dashboard TriSLA</h2>
        <p className="mt-2 text-gray-600">Visão geral do sistema TriSLA</p>
      </div>

      {/* Status do Prometheus */}
      <div className="mb-6">
        {health?.status === 'ok' ? (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center">
            <Activity className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-green-800 font-medium">
              Prometheus acessível e funcionando
            </span>
          </div>
        ) : (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <span className="text-red-800 font-medium">
              Prometheus não acessível. Verifique o túnel SSH.
            </span>
          </div>
        )}
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Slices Ativos"
          value={slices?.total?.[0]?.value?.[1] || '0'}
          icon={Package}
          color="blue"
        />
        <MetricCard
          title="Componentes UP"
          value={system?.components_up?.length || '0'}
          icon={Activity}
          color="green"
        />
        <MetricCard
          title="CPU Médio"
          value={system?.cpu_usage?.[0]?.value?.[1] ? `${parseFloat(system.cpu_usage[0].value[1]).toFixed(1)}%` : 'N/A'}
          icon={TrendingUp}
          color="yellow"
        />
        <MetricCard
          title="Memória (MB)"
          value={system?.memory_usage?.[0]?.value?.[1] ? `${parseFloat(system.memory_usage[0].value[1]).toFixed(0)}` : 'N/A'}
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Informações Adicionais */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Informações do Sistema
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Status Prometheus</p>
            <p className="text-lg font-medium text-gray-900">
              {health?.status === 'ok' ? '🟢 Online' : '🔴 Offline'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">URL Prometheus</p>
            <p className="text-lg font-medium text-gray-900">
              {health?.url || 'N/A'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
