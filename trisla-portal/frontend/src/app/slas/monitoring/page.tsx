'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { Activity, BarChart3, ExternalLink, RefreshCw } from 'lucide-react'

export default function MonitoringPage() {
  const [activeSLAs, setActiveSLAs] = useState<number>(0)
  const [systemStatus, setSystemStatus] = useState<'healthy' | 'degraded' | 'unhealthy'>('healthy')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const mountedRef = useRef(true)

  // Função estável com useCallback para evitar loops infinitos
  const fetchMonitoringData = useCallback(async () => {
    // Verificar se componente ainda está montado antes de atualizar state
    if (!mountedRef.current) return
    
    try {
      setLoading(true)
      setError(null)
      
      // Tentar buscar health global para verificar status do sistema
      try {
        const health = await api.getHealthGlobal()
        if (!mountedRef.current) return
        
        if (health.status === 'healthy') {
          setSystemStatus('healthy')
        } else if (health.status === 'degraded') {
          setSystemStatus('degraded')
        } else {
          setSystemStatus('unhealthy')
        }
      } catch (err) {
        if (!mountedRef.current) return
        setSystemStatus('degraded')
      }

      // Contar SLAs ativos (simplificado - em produção, teria endpoint específico)
      // Por enquanto, assumimos que não temos endpoint de listagem, então mostramos 0
      if (mountedRef.current) {
        setActiveSLAs(0)
        setLastUpdate(new Date())
      }
    } catch (err: any) {
      if (!mountedRef.current) return
      setError(err.message || 'Erro ao buscar dados de monitoramento')
      setSystemStatus('degraded')
    } finally {
      if (mountedRef.current) {
        setLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    mountedRef.current = true
    fetchMonitoringData()
    const interval = setInterval(fetchMonitoringData, 30000) // Atualizar a cada 30s
    return () => {
      mountedRef.current = false
      clearInterval(interval)
    }
  }, [fetchMonitoringData])

  const getStatusColor = () => {
    switch (systemStatus) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'unhealthy':
        return 'bg-red-100 text-red-800 border-red-200'
    }
  }

  const getStatusText = () => {
    switch (systemStatus) {
      case 'healthy':
        return 'Sistema Operacional'
      case 'degraded':
        return 'Sistema Degradado'
      case 'unhealthy':
        return 'Sistema Indisponível'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-8 w-8" />
          Monitoramento - Portal TriSLA
        </h1>
        <p className="text-muted-foreground mt-2">
          Visão geral do sistema e SLAs ativos. Para métricas detalhadas, use os dashboards avançados.
        </p>
      </div>

      {error && (
        <Card>
          <CardContent className="pt-6">
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
              <div className="font-medium">Erro:</div>
              <div>{error}</div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>SLAs Ativos</CardTitle>
            <CardDescription>
              Número de SLAs atualmente ativos no sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{activeSLAs}</div>
            <div className="text-sm text-muted-foreground mt-2">
              SLAs em execução
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Geral do Sistema</CardTitle>
            <CardDescription>
              Estado atual da infraestrutura TriSLA
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className={`p-4 rounded border ${getStatusColor()}`}>
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                <div className="text-lg font-semibold">{getStatusText()}</div>
              </div>
            </div>
            <div className="text-xs text-muted-foreground mt-2">
              Última atualização: {lastUpdate.toLocaleString('pt-BR')}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Métricas Detalhadas</CardTitle>
          <CardDescription>
            Acesse os dashboards avançados para visualizar métricas detalhadas por SLA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-2">
                Para métricas detalhadas de um SLA específico, use:
              </p>
              <code className="block p-2 bg-muted rounded text-sm">
                GET /api/v1/slas/metrics/&#123;sla_id&#125;
              </code>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => window.open('http://localhost:3001', '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Abrir Dashboards Avançados (Grafana)
              </Button>
              <Button
                variant="outline"
                onClick={fetchMonitoringData}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Atualizar
              </Button>
            </div>
            
            <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
              <div className="font-medium mb-1">Nota:</div>
              <div>
                O portal não duplica funcionalidades do Grafana. Use os dashboards avançados para análises detalhadas.
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

