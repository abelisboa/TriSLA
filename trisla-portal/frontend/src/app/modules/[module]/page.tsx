'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/lib/api'
import { ArrowLeft, Activity } from 'lucide-react'

export default function ModuleDetailPage() {
  const params = useParams()
  const router = useRouter()
  const moduleName = params.module as string
  const [module, setModule] = useState<any>(null)
  const [metrics, setMetrics] = useState<any>(null)
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (moduleName) {
      fetchModuleData()
    }
  }, [moduleName])

  const fetchModuleData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [moduleData, metricsData, statusData] = await Promise.all([
        api.getModule(moduleName),
        api.getModuleMetrics(moduleName),
        api.getModuleStatus(moduleName),
      ])
      setModule(moduleData)
      setMetrics(metricsData)
      setStatus(statusData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Button variant="outline" onClick={() => router.push('/modules')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </Button>
        <Card>
          <CardHeader>
            <CardTitle className="text-destructive">Erro</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => router.push('/modules')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{moduleName}</h1>
          <p className="text-muted-foreground">
            Detalhes do módulo {moduleName}
          </p>
        </div>
      </div>

      {/* Status */}
      {status && (
        <Card>
          <CardHeader>
            <CardTitle>Status</CardTitle>
            <CardDescription>Status dos pods e deployments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {status.pods && status.pods.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Pods</h3>
                  <div className="space-y-2">
                    {status.pods.map((pod: any) => (
                      <div key={pod.name} className="flex items-center justify-between p-2 border rounded">
                        <span>{pod.name}</span>
                        <span className={pod.ready ? 'text-green-600' : 'text-red-600'}>
                          {pod.ready ? 'Ready' : 'Not Ready'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Metrics */}
      {metrics && (
        <Card>
          <CardHeader>
            <CardTitle>Métricas</CardTitle>
            <CardDescription>Métricas principais do módulo</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Object.entries(metrics).map(([key, value]: [string, any]) => (
                <div key={key} className="p-4 border rounded">
                  <div className="text-sm text-muted-foreground">{key}</div>
                  <div className="text-2xl font-bold">{typeof value === 'number' ? value.toFixed(2) : String(value)}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}







