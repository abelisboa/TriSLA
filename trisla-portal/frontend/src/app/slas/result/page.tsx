'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiFetch } from '@/lib/api'
import { CheckCircle, XCircle, Clock, FileText, Activity, ExternalLink } from 'lucide-react'

function ResultPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [decision, setDecision] = useState<string>('')
  const [slaId, setSlaId] = useState<string>('')
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setMounted(true)
    const decisionParam = searchParams.get('decision') || ''
    const slaIdParam = searchParams.get('sla_id') || ''
    setDecision(decisionParam.toUpperCase())
    setSlaId(slaIdParam)
    
    if (slaIdParam) {
      fetchStatus(slaIdParam)
    } else {
      setLoading(false)
    }
  }, [searchParams])

  const fetchStatus = async (id: string) => {
    try {
      const data = await apiFetch(`/sla/status/${id}`)
      setStatus(data)
    } catch (err: any) {
      console.warn('Status não encontrado:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!mounted) {
    return null
  }

  const getDecisionIcon = () => {
    switch (decision) {
      case 'ACCEPT':
      case 'ACCEPTED':
        return <CheckCircle className="h-12 w-12 text-green-600" />
      case 'RENEG':
      case 'RENEGOTIATION':
        return <Clock className="h-12 w-12 text-yellow-600" />
      case 'REJECT':
      case 'REJECTED':
        return <XCircle className="h-12 w-12 text-red-600" />
      default:
        return <Activity className="h-12 w-12 text-gray-600" />
    }
  }

  const getDecisionColor = () => {
    switch (decision) {
      case 'ACCEPT':
      case 'ACCEPTED':
        return 'bg-green-50 border-green-200 text-green-800'
      case 'RENEG':
      case 'RENEGOTIATION':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      case 'REJECT':
      case 'REJECTED':
        return 'bg-red-50 border-red-200 text-red-800'
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }

  const getDecisionMessage = () => {
    switch (decision) {
      case 'ACCEPT':
      case 'ACCEPTED':
        return 'SLA aceito. Execução contratual automatizada via Smart Contract (quando aplicável).'
      case 'RENEG':
      case 'RENEGOTIATION':
        return 'SLA em renegociação. Ajuste os parâmetros e tente novamente.'
      case 'REJECT':
      case 'REJECTED':
        return 'SLA rejeitado. Verifique os requisitos e tente novamente.'
      default:
        return 'Status desconhecido.'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <FileText className="h-8 w-8" />
          Resultado da Solicitação de SLA
        </h1>
        <p className="text-muted-foreground mt-2">
          Decisão e informações sobre a solicitação de SLA
        </p>
      </div>

      <Card className={getDecisionColor()}>
        <CardHeader>
          <div className="flex items-center gap-4">
            {getDecisionIcon()}
            <div>
              <CardTitle className="text-2xl">Status: {decision || 'N/A'}</CardTitle>
              <CardDescription className="mt-1">
                {getDecisionMessage()}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {slaId && (
              <div>
                <div className="text-sm font-medium mb-1">SLA ID</div>
                <div className="font-mono text-sm bg-white/50 p-2 rounded">{slaId}</div>
              </div>
            )}
            
            {status?.created_at && (
              <div>
                <div className="text-sm font-medium mb-1">Timestamp</div>
                <div className="text-sm">{new Date(status.created_at).toLocaleString('pt-BR')}</div>
              </div>
            )}
            
            {!status?.created_at && (
              <div>
                <div className="text-sm font-medium mb-1">Timestamp</div>
                <div className="text-sm">{new Date().toLocaleString('pt-BR')}</div>
              </div>
            )}

            {status?.tenant_id && (
              <div>
                <div className="text-sm font-medium mb-1">Tenant ID</div>
                <div className="font-mono text-sm">{status.tenant_id}</div>
              </div>
            )}

            {status?.nest_id && (
              <div>
                <div className="text-sm font-medium mb-1">NEST ID</div>
                <div className="font-mono text-sm">{status.nest_id}</div>
              </div>
            )}

            {(decision === 'ACCEPT' || decision === 'ACCEPTED') && (
              <div className="mt-4 p-3 bg-white/50 rounded border">
                <div className="text-sm font-medium mb-1">Execução Contratual</div>
                <div className="text-xs text-muted-foreground">
                  Execução contratual automatizada via Smart Contract (quando aplicável).
                </div>
              </div>
            )}

            <div className="flex gap-2 mt-4">
              {slaId && (
                <>
                  <Button
                    variant="outline"
                    onClick={() => router.push(`/slas/metrics?id=${slaId}`)}
                  >
                    <Activity className="h-4 w-4 mr-2" />
                    Ver Métricas
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => router.push(`/slas/status?id=${slaId}`)}
                  >
                    Ver Status Detalhado
                  </Button>
                </>
              )}
              <Button
                variant="outline"
                onClick={() => router.push('/slas/create/pln')}
              >
                Criar Novo SLA (PLN)
              </Button>
              <Button
                variant="outline"
                onClick={() => router.push('/slas/create/template')}
              >
                Criar Novo SLA (Template)
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function Page() {
  return (
    <Suspense fallback={<div>Carregando resultado...</div>}>
      <ResultPage />
    </Suspense>
  )
}

