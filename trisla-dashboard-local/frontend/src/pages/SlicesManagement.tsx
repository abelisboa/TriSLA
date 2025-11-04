import { useQuery } from '@tanstack/react-query'
import { prometheusApi } from '../services/api'
import { Package } from 'lucide-react'

export default function SlicesManagement() {
  const { data: slices, isLoading } = useQuery({
    queryKey: ['prometheus', 'slices'],
    queryFn: () => prometheusApi.slices().then(res => res.data),
  })

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Gestão de Slices</h2>
        <p className="mt-2 text-gray-600">Visualize e gerencie slices TriSLA</p>
      </div>

      {isLoading ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">Carregando dados...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card Total de Slices */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total de Slices</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {slices?.total?.[0]?.value?.[1] || '0'}
                </p>
              </div>
              <Package className="h-8 w-8 text-blue-600" />
            </div>
          </div>

          {/* Slices por Tipo */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Slices por Tipo</h3>
            <div className="space-y-2">
              {slices?.by_type?.map((item: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{item.metric?.slice_type || 'Unknown'}</span>
                  <span className="text-sm font-medium text-gray-900">{item.value[1]}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Slices Criados */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Total Criados</h3>
            <p className="text-3xl font-bold text-gray-900">
              {slices?.created_total?.[0]?.value?.[1] || '0'}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
