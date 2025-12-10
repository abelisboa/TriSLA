'use client'

import Link from 'next/link'
import { FileText, Settings, BarChart3, Activity } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Verificar status do backend opcionalmente
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:8001/health')
        if (response.ok) {
          setBackendStatus('online')
        } else {
          setBackendStatus('offline')
        }
      } catch {
        setBackendStatus('offline')
      }
    }
    checkBackend()
  }, [])
  
  // Evitar hydration mismatch
  if (!mounted) {
    return null
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN</h1>
        <p className="text-muted-foreground">
          Portal para gerenciamento de SLA em redes 5G/O-RAN - Integração completa com todos os módulos TriSLA
        </p>
        {backendStatus !== 'checking' && (
          <div className="mt-2">
            <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
              backendStatus === 'online' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              <Activity className={`h-4 w-4 ${backendStatus === 'online' ? 'animate-pulse' : ''}`} />
              Backend: {backendStatus === 'online' ? 'Online' : 'Offline'}
            </span>
          </div>
        )}
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Link href="/slas/create/pln">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-6 w-6" />
                Criar SLA via PLN
              </CardTitle>
              <CardDescription>
                Crie um SLA usando Processamento de Linguagem Natural
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Descreva seu SLA em linguagem natural e o sistema processará através de todos os módulos TriSLA.
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/slas/create/template">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-6 w-6" />
                Criar SLA via Template
              </CardTitle>
              <CardDescription>
                Crie um SLA usando template técnico
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Use templates pré-configurados para criar SLAs rapidamente com validação completa.
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/slas/metrics">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-6 w-6" />
                Visualizar Métricas
              </CardTitle>
              <CardDescription>
                Visualize métricas de performance dos SLAs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Acompanhe métricas reais: latência, throughput, packet loss e status dos slices.
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  )
}
