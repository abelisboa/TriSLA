'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiFetch } from '@/lib/api'
import { FileText, Activity, ArrowLeft } from 'lucide-react'

function StatusPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [slaId, setSlaId] = useState('')
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setMounted(true)
    const id = searchParams.get('id') || ''
    setSlaId(id)
    if (id) {
      fetchStatus(id)
    } else {
      setLoading(false)
    }
  }, [searchParams])

  const fetchStatus = async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiFetch(`/sla/status/${id}`)
      setStatus(data)
    } catch (err: any) {
      console.warn('Status não encontrado:', err)
      setError(err?.message || 'Status não encontrado. Verifique o ID do SLA.')
    } finally {
      setLoading(false)
    }
  }

  if (!mounted) {
    return null
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <FileText className="h-8 w-8" />
          Status do SLA
        </h1>
        <p className="text-muted-foreground mt-2">
          Consulta em tempo real ao NASP — sem cache local
        </p>
      </div>

      {!slaId && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">
              Informe o ID do SLA na URL: <code className="bg-muted px-1 rounded">/slas/status?id=&lt;sla_id&gt;</code>
            </p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => router.push('/slas/result')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar ao resultado
            </Button>
          </CardContent>
        </Card>
      )}

      {slaId && loading && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">Carregando status...</p>
          </CardContent>
        </Card>
      )}

      {slaId && error && !loading && (
        <Card>
          <CardContent className="pt-6">
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
              <div className="font-medium">Erro ao buscar status</div>
              <div>{error}</div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button variant="outline" onClick={() => fetchStatus(slaId)}>
                Tentar novamente
              </Button>
              <Button variant="outline" onClick={() => router.push(`/slas/metrics?id=${slaId}`)}>
                <Activity className="h-4 w-4 mr-2" />
                Ver métricas
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {slaId && status && !loading && (
        <Card>
          <CardHeader>
            <CardTitle>Status do SLA</CardTitle>
            <CardDescription>SLA ID: {status.sla_id || slaId}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">SLA ID</div>
                <div className="font-mono text-sm">{status.sla_id || slaId}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Status</div>
                <div className="text-sm font-medium">
                  <span className={`px-2 py-1 rounded text-xs ${
                    status.status === 'active' ? 'bg-green-100 text-green-800' :
                    status.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {status.status || 'N/A'}
                  </span>
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Tenant ID</div>
                <div className="font-mono text-sm">{status.tenant_id || 'N/A'}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Intent ID</div>
                <div className="font-mono text-sm">{status.intent_id || 'N/A'}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">NEST ID</div>
                <div className="font-mono text-sm">{status.nest_id || 'N/A'}</div>
              </div>
              {status.created_at && (
                <div>
                  <div className="text-sm text-muted-foreground">Criado em</div>
                  <div className="text-sm">{new Date(status.created_at).toLocaleString('pt-BR')}</div>
                </div>
              )}
              {status.updated_at && (
                <div>
                  <div className="text-sm text-muted-foreground">Atualizado em</div>
                  <div className="text-sm">{new Date(status.updated_at).toLocaleString('pt-BR')}</div>
                </div>
              )}
            </div>
            <div className="flex gap-2 mt-6">
              <Button
                variant="outline"
                onClick={() => router.push(`/slas/metrics?id=${slaId}`)}
              >
                <Activity className="h-4 w-4 mr-2" />
                Ver métricas
              </Button>
              <Button variant="outline" onClick={() => router.push('/slas/result')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Voltar ao resultado
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default function Page() {
  return (
    <Suspense fallback={<div>Carregando status...</div>}>
      <StatusPage />
    </Suspense>
  )
}
