'use client'

import { useEffect, useState, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/lib/api'
import { Contract, Violation, Renegotiation, Penalty } from '@/types'
import { ArrowLeft, AlertTriangle, RefreshCw, DollarSign } from 'lucide-react'

export default function ContractDetailPage() {
  const params = useParams()
  const router = useRouter()
  const contractId = params.id as string
  const [contract, setContract] = useState<Contract | null>(null)
  const [violations, setViolations] = useState<Violation[]>([])
  const [renegotiations, setRenegotiations] = useState<Renegotiation[]>([])
  const [penalties, setPenalties] = useState<Penalty[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Função estável com useCallback para evitar loops infinitos
  const fetchContractData = useCallback(async () => {
    if (!contractId) return
    setLoading(true)
    setError(null)
    try {
      const [contractData, violationsData, renegotiationsData, penaltiesData] = await Promise.all([
        api.getContract(contractId),
        api.getContractViolations(contractId),
        api.getContractRenegotiations(contractId),
        api.getContractPenalties(contractId),
      ])
      setContract(contractData)
      setViolations(violationsData)
      setRenegotiations(renegotiationsData)
      setPenalties(penaltiesData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [contractId])

  useEffect(() => {
    if (contractId) {
      fetchContractData()
    }
  }, [contractId, fetchContractData])

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

  if (error || !contract) {
    return (
      <div className="space-y-6">
        <Button variant="outline" onClick={() => router.push('/contracts')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </Button>
        <Card>
          <CardHeader>
            <CardTitle className="text-destructive">Erro</CardTitle>
            <CardDescription>{error || 'Contrato não encontrado'}</CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => router.push('/contracts')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Contrato {contract.id.slice(0, 8)}</h1>
          <p className="text-muted-foreground">
            Detalhes completos do contrato
          </p>
        </div>
      </div>

      {/* Contract Info */}
      <Card>
        <CardHeader>
          <CardTitle>Informações do Contrato</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <div className="text-sm text-muted-foreground">Tenant ID</div>
              <div className="font-semibold">{contract.tenant_id}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Status</div>
              <div className="font-semibold">{contract.status}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Versão</div>
              <div className="font-semibold">{contract.version}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Tipo de Serviço</div>
              <div className="font-semibold">{contract.metadata.service_type}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Criado em</div>
              <div className="font-semibold">
                {new Date(contract.created_at).toLocaleString('pt-BR')}
              </div>
            </div>
            {contract.blockchain_tx_hash && (
              <div>
                <div className="text-sm text-muted-foreground">Blockchain TX Hash</div>
                <div className="font-mono text-sm">{contract.blockchain_tx_hash}</div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* SLA Requirements */}
      <Card>
        <CardHeader>
          <CardTitle>Requisitos SLA</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {contract.sla_requirements.latency && (
              <div>
                <span className="text-sm text-muted-foreground">Latência: </span>
                <span className="font-semibold">
                  {contract.sla_requirements.latency.max || 'N/A'}
                </span>
              </div>
            )}
            {contract.sla_requirements.throughput && (
              <div>
                <span className="text-sm text-muted-foreground">Throughput: </span>
                <span className="font-semibold">
                  {contract.sla_requirements.throughput.min || 'N/A'}
                </span>
              </div>
            )}
            {contract.sla_requirements.reliability && (
              <div>
                <span className="text-sm text-muted-foreground">Confiabilidade: </span>
                <span className="font-semibold">
                  {(contract.sla_requirements.reliability * 100).toFixed(5)}%
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Violations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Violações ({violations.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {violations.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground">
              Nenhuma violação registrada
            </div>
          ) : (
            <div className="space-y-2">
              {violations.map((violation) => (
                <div key={violation.id} className="p-3 border rounded">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold">{violation.violation_type}</div>
                      <div className="text-sm text-muted-foreground">
                        {violation.metric_name}: Esperado {String(violation.expected_value)}, 
                        Obtido {String(violation.actual_value)}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(violation.detected_at).toLocaleString('pt-BR')}
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      violation.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                      violation.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      violation.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {violation.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Renegotiations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Renegociações ({renegotiations.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {renegotiations.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground">
              Nenhuma renegociação registrada
            </div>
          ) : (
            <div className="space-y-2">
              {renegotiations.map((reneg) => (
                <div key={reneg.id} className="p-3 border rounded">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold">
                        Versão {reneg.previous_version} → {reneg.new_version}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Razão: {reneg.reason}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(reneg.requested_at).toLocaleString('pt-BR')}
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      reneg.status === 'ACCEPTED' ? 'bg-green-100 text-green-800' :
                      reneg.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {reneg.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Penalties */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Penalidades ({penalties.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {penalties.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground">
              Nenhuma penalidade aplicada
            </div>
          ) : (
            <div className="space-y-2">
              {penalties.map((penalty) => (
                <div key={penalty.id} className="p-3 border rounded">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-semibold">{penalty.penalty_type}</div>
                      {penalty.amount && (
                        <div className="text-sm">Valor: R$ {penalty.amount.toFixed(2)}</div>
                      )}
                      {penalty.percentage && (
                        <div className="text-sm">Percentual: {penalty.percentage}%</div>
                      )}
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(penalty.applied_at).toLocaleString('pt-BR')}
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      penalty.status === 'APPLIED' ? 'bg-red-100 text-red-800' :
                      penalty.status === 'WAIVED' ? 'bg-green-100 text-green-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {penalty.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}







