'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiFetch, APIError } from '@/lib/api'
import { Sparkles, CheckCircle, XCircle, Clock, Activity } from 'lucide-react'

export default function SLACreationPLNPage() {
  const router = useRouter()
  const [intentText, setIntentText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)
  const [interpretedTemplate, setInterpretedTemplate] = useState<any>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleInterpret = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    setInterpretedTemplate(null)

    try {
      const data = await apiFetch("/sla/interpret", {
        method: "POST",
        body: JSON.stringify({
          intent: intentText
        }),
        headers: { "Content-Type": "application/json" }
      })
      setInterpretedTemplate(data)
      setResult(data)
    } catch (err: any) {
      const apiError = err as APIError
      setError(apiError.message || 'Erro ao interpretar SLA')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!interpretedTemplate) return
    
    setSubmitting(true)
    setError(null)

    try {
      const data = await apiFetch("/sla/submit", {
        method: "POST",
        body: JSON.stringify({
          tenant_id: "default",
          template_id: interpretedTemplate.intent_id || "pln-generated",
          form_values: {
            type: interpretedTemplate.service_type,
            service_type: interpretedTemplate.service_type,
            ...interpretedTemplate.sla_requirements,
            ...interpretedTemplate.technical_parameters
          }
        }),
        headers: { "Content-Type": "application/json" }
      })
      setResult(data)
      // Redirecionar para página de resultado após submissão
      router.push(`/slas/result?decision=${data.decision}&sla_id=${data.sla_id || ''}`)
    } catch (err: any) {
      const apiError = err as APIError
      setError(apiError.message || 'Erro ao submeter SLA')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Sparkles className="h-8 w-8" />
          Criar SLA por Linguagem Natural (PLN)
        </h1>
        <p className="text-muted-foreground mt-2">
          A descrição é interpretada semanticamente (PLN → Ontologia → Template GST). O SEM-CSMF do NASP processa sua solicitação e gera um template GST editável antes da submissão final.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Formulário</CardTitle>
            <CardDescription>
              Descreva o SLA desejado em linguagem natural
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleInterpret} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Intent (Linguagem Natural)</label>
                <textarea
                  value={intentText}
                  onChange={(e) => setIntentText(e.target.value)}
                  className="w-full mt-1 px-3 py-2 border rounded-md min-h-[200px]"
                  placeholder="Ex: Quero um slice URLLC com latência máxima de 10ms e confiabilidade de 99.999%"
                  required
                />
              </div>
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
                  <div className="font-medium">Erro:</div>
                  <div>{error}</div>
                  {error.includes('SEM-CSMF') && (
                    <div className="mt-2 text-xs">Módulo SEM-CSMF offline ou retornou erro. Verifique se o port-forward está ativo em localhost:8080</div>
                  )}
                  {error.includes('422') && (
                    <div className="mt-2 text-xs">Erro semântico: O SEM-CSMF rejeitou o intent. Verifique a sintaxe.</div>
                  )}
                </div>
              )}
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Interpretando...' : 'Interpretar (PLN → Ontologia → Template GST)'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Template GST Gerado</CardTitle>
            <CardDescription>
              Template resultante da interpretação semântica (PLN → Ontologia → Template GST)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {interpretedTemplate ? (
              <div className="space-y-4">
                {/* Mostrar template antes da submissão */}
                <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                  <div className="text-sm font-medium text-blue-900 mb-2">Template GST Gerado:</div>
                  <div className="space-y-2 text-sm">
                    {interpretedTemplate.service_type && (
                      <div>
                        <span className="font-medium">Tipo de Serviço:</span> {interpretedTemplate.service_type}
                      </div>
                    )}
                    {interpretedTemplate.technical_parameters && Object.keys(interpretedTemplate.technical_parameters).length > 0 && (
                      <div>
                        <span className="font-medium">Parâmetros Técnicos:</span>
                        <pre className="mt-1 p-2 bg-white rounded text-xs overflow-auto">
                          {JSON.stringify(interpretedTemplate.technical_parameters, null, 2)}
                        </pre>
                      </div>
                    )}
                    {interpretedTemplate.sla_requirements && Object.keys(interpretedTemplate.sla_requirements).length > 0 && (
                      <div>
                        <span className="font-medium">Requisitos SLA:</span>
                        <pre className="mt-1 p-2 bg-white rounded text-xs overflow-auto">
                          {JSON.stringify(interpretedTemplate.sla_requirements, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
                
                <Button 
                  onClick={handleSubmit} 
                  disabled={submitting} 
                  className="w-full"
                >
                  {submitting ? 'Submetendo...' : 'Submeter SLA ao NASP'}
                </Button>
              </div>
            ) : result ? (
              <div className="space-y-4">
                {/* Intent ID */}
                {result.intent_id && (
                  <div>
                    <div className="text-sm text-muted-foreground">Intent ID</div>
                    <div className="font-mono text-sm">{result.intent_id}</div>
                  </div>
                )}
                
                {/* Service Type */}
                {result.service_type && (
                  <div>
                    <div className="text-sm text-muted-foreground">Service Type</div>
                    <div className="text-sm font-medium">{result.service_type}</div>
                  </div>
                )}
                
                {/* SLA Requirements */}
                {result.sla_requirements && Object.keys(result.sla_requirements).length > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">SLA Requirements</div>
                    <pre className="p-3 bg-muted rounded text-xs overflow-auto max-h-[200px]">
                      {JSON.stringify(result.sla_requirements, null, 2)}
                    </pre>
                  </div>
                )}
                
                {/* SLA ID */}
                {result.sla_id && (
                  <div>
                    <div className="text-sm text-muted-foreground">SLA ID</div>
                    <div className="font-mono text-sm">{result.sla_id}</div>
                  </div>
                )}
                
                {/* NEST ID */}
                {result.nest_id && (
                  <div>
                    <div className="text-sm text-muted-foreground">NEST ID</div>
                    <div className="font-mono text-sm">{result.nest_id}</div>
                  </div>
                )}
                
                {/* Slice Type (compatibilidade) */}
                {result.slice_type && (
                  <div>
                    <div className="text-sm text-muted-foreground">Tipo de Slice</div>
                    <div className="text-sm font-medium">{result.slice_type}</div>
                  </div>
                )}
                
                {/* Status */}
                <div>
                  <div className="text-sm text-muted-foreground">Status</div>
                  <div className="text-sm font-medium">
                    <span className={`px-2 py-1 rounded text-xs ${
                      result.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                      result.status === 'active' ? 'bg-green-100 text-green-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {result.status || 'N/A'}
                    </span>
                  </div>
                </div>
                
                {/* Message */}
                {result.message && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded text-green-800 text-sm">
                    {result.message}
                  </div>
                )}
                
                {/* Botão para métricas */}
                {result.sla_id && (
                  <Button
                    variant="outline"
                    onClick={() => router.push(`/slas/metrics?id=${result.sla_id}`)}
                    className="w-full"
                  >
                    Monitorar SLA
                  </Button>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                O template GST aparecerá aqui após a interpretação
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
