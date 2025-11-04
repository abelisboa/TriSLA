import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { prometheusApi } from '../services/api'
import { Package } from 'lucide-react'
import { extractPrometheusValue, safeMapMetrics } from '../utils/dataHelpers'

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
        <div className="bg-white rounded-xl shadow-lg p-12 text-center border border-gray-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Carregando dados...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card Total de Slices */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 card-hover">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total de Slices</p>
                <p className="text-4xl font-bold text-gray-900 mt-3">
                  {slices?.total?.[0] ? extractPrometheusValue(slices.total[0]) : '0'}
                </p>
              </div>
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-3 rounded-xl shadow-md">
                <Package className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>

          {/* Slices por Tipo */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 card-hover">
            <h3 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">Slices por Tipo</h3>
            <div className="space-y-3">
              {safeMapMetrics(slices?.by_type, (item: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 transition-colors">
                  <span className="text-sm font-medium text-gray-700">{item.metric?.slice_type || 'Unknown'}</span>
                  <span className="text-sm font-bold text-gray-900 bg-blue-100 px-3 py-1 rounded-full">{extractPrometheusValue(item)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Slices Criados */}
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 card-hover">
            <h3 className="text-lg font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">Total Criados</h3>
            <p className="text-5xl font-bold text-gray-900 text-center py-4">
              {slices?.created_total?.[0] ? extractPrometheusValue(slices.created_total[0]) : '0'}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
