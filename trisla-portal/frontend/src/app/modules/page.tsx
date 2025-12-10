'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/lib/api'
import { Module } from '@/types'
import { ArrowLeft, Activity, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'

export default function ModulesPage() {
  const router = useRouter()
  const [modules, setModules] = useState<Module[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchModules()
  }, [])

  const fetchModules = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getModules()
      setModules(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'UP':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case 'DOWN':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'DEGRADED':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      default:
        return <Activity className="h-5 w-5 text-gray-500" />
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6, 7].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <Card className="w-full max-w-md">
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
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Módulos</h1>
        <p className="text-muted-foreground">
          Visão detalhada dos módulos do TriSLA
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {modules.map((module) => (
          <Card 
            key={module.name}
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => router.push(`/modules/${module.name}`)}
          >
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{module.name}</CardTitle>
                {getStatusIcon(module.status)}
              </div>
              <CardDescription>Status: {module.status}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {module.latency !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Latência:</span>
                    <span>{module.latency.toFixed(2)}ms</span>
                  </div>
                )}
                {module.error_rate !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Taxa de Erro:</span>
                    <span>{(module.error_rate * 100).toFixed(2)}%</span>
                  </div>
                )}
                {module.pods && module.pods.length > 0 && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Pods:</span>
                    <span>
                      {module.pods.filter(p => p.ready).length}/{module.pods.length} prontos
                    </span>
                  </div>
                )}
              </div>
              <Button 
                variant="outline" 
                className="w-full mt-4"
                onClick={(e) => {
                  e.stopPropagation()
                  router.push(`/modules/${module.name}`)
                }}
              >
                Ver Detalhes
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}


