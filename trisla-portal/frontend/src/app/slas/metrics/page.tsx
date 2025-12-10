'use client'

export const dynamic = "force-dynamic";

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api, APIError } from '@/lib/api'
import { BarChart3, Activity } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function MetricsPage() {
  const searchParams = useSearchParams()
  const [mounted, setMounted] = useState(false)
  const [slaId, setSlaId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<any>(null)
  const [metrics, setMetrics] = useState<any>(null)
  const [autoRefresh, setAutoRefresh] = useState(false)

  // Evitar hydration mismatch - inicializar slaId apenas no cliente
  useEffect(() => {
    setMounted(true)
    setSlaId(searchParams.get('id') || '')
  }, [searchParams])

  const fetchStatus = async () => {
    if (!slaId) return
    try {
      const data = await api(`/sla/status/${slaId}`)
      setStatus(data)
    } catch (err: any) {
      // Status pode não existir ainda - não é crítico
      console.warn('Status não encontrado:', err)
    }
  }

  const fetchMetrics = async () => {
    if (!slaId) return
    setLoading(true)
    setError(null)
    try {
      const data = await api(`/sla/metrics/${slaId}`)
      setMetrics(data)
    } catch (err: any) {
      const apiError = err as APIError
      setError(apiError.message || 'Erro ao buscar métricas')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (mounted && slaId) {
      fetchStatus()
      fetchMetrics()
    }
  }, [mounted, slaId])

  useEffect(() => {
    if (autoRefresh && slaId) {
      const interval = setInterval(() => {
        fetchMetrics()
      }, 5000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, slaId])

  // Extrair métricas REAIS do objeto retornado (SEM simulação)
  const latency_ms = metrics?.latency_ms
  const jitter_ms = metrics?.jitter_ms
  const throughput_ul = metrics?.throughput_ul
  const throughput_dl = metrics?.throughput_dl
  const packet_loss = metrics?.packet_loss
  const availability = metrics?.availability
  const slice_status = metrics?.slice_status

  // Dados para gráficos - apenas valores REAIS (sem simulação)
  // Se não houver dados históricos, mostrar apenas o valor atual
  const latencyData = latency_ms !== undefined ? [
    { time: 'Agora', latency_ms: latency_ms }
  ] : []

  const jitterData = jitter_ms !== undefined ? [
    { time: 'Agora', jitter_ms: jitter_ms }
  ] : []

  const throughputData = (throughput_ul !== undefined || throughput_dl !== undefined) ? [
    { 
      time: 'Agora', 
      throughput_ul: throughput_ul || 0, 
      throughput_dl: throughput_dl || 0 
    }
  ] : []

  const packetLossData = packet_loss !== undefined ? [
    { time: 'Agora', packet_loss: packet_loss }
  ] : []

  // Evitar hydration mismatch
  if (!mounted) {
    return null
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-8 w-8" />
          TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN
        </h1>
        <p className="text-muted-foreground">
          Métricas de performance dos SLAs - consulta direta ao NASP (sem simulações)
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Buscar SLA</CardTitle>
          <CardDescription>
            Informe o ID do SLA para visualizar métricas reais
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <input
              type="text"
              value={slaId}
              onChange={(e) => setSlaId(e.target.value)}
              className="flex-1 px-3 py-2 border rounded-md"
              placeholder="sla-id-123"
            />
            <Button onClick={fetchMetrics} disabled={!slaId || loading}>
              Buscar
            </Button>
            {slaId && (
              <Button
                variant={autoRefresh ? "destructive" : "outline"}
                onClick={() => setAutoRefresh(!autoRefresh)}
              >
                {autoRefresh ? 'Parar Auto-refresh' : 'Auto-refresh (5s)'}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card>
          <CardContent className="pt-6">
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
              <div className="font-medium">Erro ao buscar métricas:</div>
              <div>{error}</div>
              {error.includes('SLA-Agent Layer') && (
                <div className="mt-2 text-xs">SLA-Agent Layer offline. Verifique se o port-forward está ativo em localhost:8084</div>
              )}
              {error.includes('404') && (
                <div className="mt-2 text-xs">SLA não encontrado. Verifique se o ID está correto.</div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {status && (
        <Card>
          <CardHeader>
            <CardTitle>Status do SLA</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">SLA ID</div>
                <div className="font-mono text-sm">{status.sla_id}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Status</div>
                <div className="text-sm font-medium">
                  <span className={`px-2 py-1 rounded text-xs ${
                    status.status === 'active' ? 'bg-green-100 text-green-800' :
                    status.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {status.status}
                  </span>
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Tenant ID</div>
                <div className="font-mono text-sm">{status.tenant_id}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Slice Status</div>
                <div className="text-sm font-medium">
                  <Activity className="inline h-4 w-4 mr-1" />
                  {slice_status ? (
                    <span className={`px-2 py-1 rounded text-xs ${
                      slice_status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                      slice_status === 'FAILED' ? 'bg-red-100 text-red-800' :
                      slice_status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {slice_status}
                    </span>
                  ) : (
                    'N/A'
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {metrics && (
        <>
          <div className="grid gap-6 md:grid-cols-2">
            {/* Latência - Dados REAIS */}
            {latency_ms !== undefined && (
              <Card>
                <CardHeader>
                  <CardTitle>Latência</CardTitle>
                  <CardDescription>Latência em milissegundos (dados reais do NASP)</CardDescription>
                </CardHeader>
                <CardContent>
                  {latencyData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={latencyData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="latency_ms" stroke="#8884d8" name="Latency (ms)" />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : null}
                  <div className="mt-4 text-center">
                    <div className="text-2xl font-bold">{latency_ms.toFixed(2)} ms</div>
                    <div className="text-sm text-muted-foreground">Valor atual (real)</div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Jitter - Dados REAIS */}
            {jitter_ms !== undefined && (
              <Card>
                <CardHeader>
                  <CardTitle>Jitter</CardTitle>
                  <CardDescription>Jitter em milissegundos (dados reais do NASP)</CardDescription>
                </CardHeader>
                <CardContent>
                  {jitterData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={jitterData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="jitter_ms" stroke="#ff7300" name="Jitter (ms)" />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : null}
                  <div className="mt-4 text-center">
                    <div className="text-2xl font-bold">{jitter_ms.toFixed(2)} ms</div>
                    <div className="text-sm text-muted-foreground">Valor atual (real)</div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Throughput UL/DL - Dados REAIS */}
          {(throughput_ul !== undefined || throughput_dl !== undefined) && (
            <Card>
              <CardHeader>
                <CardTitle>Throughput</CardTitle>
                <CardDescription>Throughput UL/DL em Mbps (dados reais do NASP)</CardDescription>
              </CardHeader>
              <CardContent>
                {throughputData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={throughputData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="throughput_ul" stroke="#82ca9d" name="UL (Mbps)" />
                      <Line type="monotone" dataKey="throughput_dl" stroke="#ffc658" name="DL (Mbps)" />
                    </LineChart>
                  </ResponsiveContainer>
                ) : null}
                <div className="mt-4 grid grid-cols-2 gap-4 text-center">
                  <div>
                    <div className="text-sm text-muted-foreground">UL (Real)</div>
                    <div className="text-xl font-bold">{throughput_ul?.toFixed(2) || 'N/A'} Mbps</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">DL (Real)</div>
                    <div className="text-xl font-bold">{throughput_dl?.toFixed(2) || 'N/A'} Mbps</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Packet Loss - Dados REAIS */}
          {packet_loss !== undefined && (
            <Card>
              <CardHeader>
                <CardTitle>Packet Loss</CardTitle>
                <CardDescription>Perda de pacotes em porcentagem (dados reais do NASP)</CardDescription>
              </CardHeader>
              <CardContent>
                {packetLossData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={packetLossData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area type="monotone" dataKey="packet_loss" stroke="#ff7300" fill="#ff7300" name="Packet Loss (%)" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : null}
                <div className="mt-4 text-center">
                  <div className="text-2xl font-bold">{packet_loss.toFixed(3)}%</div>
                  <div className="text-sm text-muted-foreground">Valor atual (real)</div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Métricas adicionais - Dados REAIS */}
          <div className="grid gap-6 md:grid-cols-3">
            {jitter_ms !== undefined && (
              <Card>
                <CardHeader>
                  <CardTitle>Jitter</CardTitle>
                  <CardDescription>Variação de latência (real)</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{jitter_ms.toFixed(2)} ms</div>
                </CardContent>
              </Card>
            )}
            
            {availability !== undefined && (
              <Card>
                <CardHeader>
                  <CardTitle>Disponibilidade</CardTitle>
                  <CardDescription>Percentual de disponibilidade (real)</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{availability.toFixed(2)}%</div>
                </CardContent>
              </Card>
            )}

            {slice_status && (
              <Card>
                <CardHeader>
                  <CardTitle>Slice Status</CardTitle>
                  <CardDescription>Status atual do slice (real)</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    <span className={`px-3 py-2 rounded text-sm ${
                      slice_status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                      slice_status === 'FAILED' ? 'bg-red-100 text-red-800' :
                      slice_status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                      slice_status === 'TERMINATED' ? 'bg-gray-100 text-gray-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {slice_status}
                    </span>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {!latency_ms && !throughput_ul && !throughput_dl && !packet_loss && !jitter_ms && !availability && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-muted-foreground">
                  Métricas ainda não disponíveis para este SLA. Aguarde alguns instantes.
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

export default function Page() {
  return (
    <Suspense fallback={<div>Loading metrics...</div>}>
      <MetricsPage />
    </Suspense>
  );
}

