'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { apiFetch } from '@/lib/api'
import { Contract } from '@/types'
import { FileCheck, Eye, GitCompare } from 'lucide-react'

export default function ContractsPage() {
  const router = useRouter()
  const [contracts, setContracts] = useState<Contract[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchContracts()
  }, [])

  const fetchContracts = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiFetch("/contracts")
      setContracts(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-100 text-green-800'
      case 'VIOLATED':
        return 'bg-red-100 text-red-800'
      case 'RENEGOTIATED':
        return 'bg-yellow-100 text-yellow-800'
      case 'TERMINATED':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-blue-100 text-blue-800'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Card>
          <CardContent className="p-6">
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Contratos</h1>
          <p className="text-muted-foreground">
            Lista de contratos SLA do TriSLA
          </p>
        </div>
        <Button onClick={() => router.push('/contracts/analytics')}>
          <GitCompare className="mr-2 h-4 w-4" />
          Analytics
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Contratos ({contracts.length})</CardTitle>
          <CardDescription>
            Todos os contratos SLA registrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {contracts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                Nenhum contrato encontrado
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">ID</th>
                      <th className="text-left p-2">Tenant</th>
                      <th className="text-left p-2">Status</th>
                      <th className="text-left p-2">Tipo</th>
                      <th className="text-left p-2">Versão</th>
                      <th className="text-left p-2">Criado em</th>
                      <th className="text-left p-2">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contracts.map((contract) => (
                      <tr key={contract.id} className="border-b hover:bg-muted/50">
                        <td className="p-2 font-mono text-sm">{contract.id.slice(0, 8)}...</td>
                        <td className="p-2">{contract.tenant_id}</td>
                        <td className="p-2">
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(contract.status)}`}>
                            {contract.status}
                          </span>
                        </td>
                        <td className="p-2">{contract.metadata.service_type}</td>
                        <td className="p-2">{contract.version}</td>
                        <td className="p-2 text-sm text-muted-foreground">
                          {new Date(contract.created_at).toLocaleDateString('pt-BR')}
                        </td>
                        <td className="p-2">
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => router.push(`/contracts/${contract.id}`)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => router.push(`/contracts/compare?ids=${contract.id}`)}
                            >
                              <GitCompare className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}







