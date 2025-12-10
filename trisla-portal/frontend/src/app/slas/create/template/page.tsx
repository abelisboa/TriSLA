'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api, APIError } from '@/lib/api'
import { Settings, CheckCircle, XCircle, Clock, Activity, Hash } from 'lucide-react'

const TEMPLATES = [
  {
    template_id: 'urllc-template-001',
    name: 'URLLC',
    description: 'Ultra-Reliable Low Latency Communication',
    service_type: 'URLLC',
    fields: [
      { name: 'type', label: 'Service Type', type: 'hidden', value: 'URLLC', required: false },
      { name: 'latency', label: 'Latência Máxima (ms)', type: 'number', required: true, min: 1, max: 100 },
      { name: 'reliability', label: 'Confiabilidade (%)', type: 'number', required: true, min: 99, max: 99.999, step: 0.001 },
    ]
  },
  {
    template_id: 'embb-template-001',
    name: 'eMBB',
    description: 'Enhanced Mobile Broadband',
    service_type: 'eMBB',
    fields: [
      { name: 'type', label: 'Service Type', type: 'hidden', value: 'eMBB', required: false },
      { name: 'throughput_ul', label: 'Throughput UL (Mbps)', type: 'number', required: true, min: 1 },
      { name: 'throughput_dl', label: 'Throughput DL (Mbps)', type: 'number', required: true, min: 1 },
    ]
  },
  {
    template_id: 'mmtc-template-001',
    name: 'mMTC',
    description: 'Massive Machine Type Communication',
    service_type: 'mMTC',
    fields: [
      { name: 'type', label: 'Service Type', type: 'hidden', value: 'mMTC', required: false },
      { name: 'device_density', label: 'Densidade de Dispositivos (por km²)', type: 'number', required: true, min: 1 },
      { name: 'battery_life', label: 'Vida Útil da Bateria (anos)', type: 'number', required: true, min: 1 },
    ]
  },
]

export default function SLACreationTemplatePage() {
  const router = useRouter()
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [formValues, setFormValues] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)

  const template = TEMPLATES.find(t => t.template_id === selectedTemplate)

  // Inicializar campos hidden quando template for selecionado
  useEffect(() => {
    if (template) {
      const hiddenFields: Record<string, any> = {}
      template.fields.forEach(field => {
        if (field.type === 'hidden' && field.value) {
          hiddenFields[field.name] = field.value
        }
      })
      if (Object.keys(hiddenFields).length > 0) {
        setFormValues(prev => ({ ...prev, ...hiddenFields }))
      }
    }
  }, [selectedTemplate, template])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTemplate) {
      setError('Selecione um template')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await api("/sla/submit", {
        method: "POST",
        body: JSON.stringify({
          tenant_id: "default",
          template_id: selectedTemplate,
          form_values: formValues
        }),
      })
      setResult(data)
    } catch (err: any) {
      const apiError = err as APIError
      setError(apiError.message || 'Erro ao criar SLA')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Settings className="h-8 w-8" />
          TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN
        </h1>
        <p className="text-muted-foreground">
          Criar SLA via Template - será processado por todos os módulos TriSLA (SEM-CSMF → ML-NSMF → Decision Engine → BC-NSSMF)
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Formulário</CardTitle>
            <CardDescription>
              Selecione um template e preencha os valores
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Template</label>
                <select
                  value={selectedTemplate}
                  onChange={(e) => {
                    setSelectedTemplate(e.target.value)
                    // Limpar formValues, mas manter campos hidden serão preenchidos pelo useEffect
                    const newTemplate = TEMPLATES.find(t => t.template_id === e.target.value)
                    const initialValues: Record<string, any> = {}
                    if (newTemplate) {
                      newTemplate.fields.forEach(field => {
                        if (field.type === 'hidden' && field.value) {
                          initialValues[field.name] = field.value
                        }
                      })
                    }
                    setFormValues(initialValues)
                  }}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  required
                >
                  <option value="">Selecione um template...</option>
                  {TEMPLATES.map(t => (
                    <option key={t.template_id} value={t.template_id}>
                      {t.name} - {t.description}
                    </option>
                  ))}
                </select>
              </div>

              {template && (
                <div className="space-y-3 pt-2 border-t">
                  <div className="text-sm text-muted-foreground mb-2">
                    {template.description}
                  </div>
                  {template.fields.map(field => {
                    // Campos hidden são preenchidos automaticamente
                    if (field.type === 'hidden') {
                      if (!formValues[field.name]) {
                        setFormValues({
                          ...formValues,
                          [field.name]: field.value
                        })
                      }
                      return null
                    }
                    
                    return (
                      <div key={field.name}>
                        <label className="text-sm font-medium">
                          {field.label}
                          {field.required && <span className="text-red-500"> *</span>}
                        </label>
                        <input
                          type={field.type}
                          value={formValues[field.name] || ''}
                          onChange={(e) => setFormValues({
                            ...formValues,
                            [field.name]: field.type === 'number' ? parseFloat(e.target.value) || '' : e.target.value
                          })}
                          className="w-full mt-1 px-3 py-2 border rounded-md"
                          required={field.required}
                          min={"min" in field ? field.min : undefined}
                          max={"max" in field ? field.max : undefined}
                          step={"step" in field ? field.step : undefined}
                        />
                      </div>
                    )
                  })}
                </div>
              )}

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
                  <div className="font-medium">Erro:</div>
                  <div>{error}</div>
                  {error.includes('SEM-CSMF') && (
                    <div className="mt-2 text-xs">Módulo SEM-CSMF offline ou retornou erro. Verifique se o port-forward está ativo.</div>
                  )}
                  {error.includes('ML-NSMF') && (
                    <div className="mt-2 text-xs">Módulo ML-NSMF offline. Verifique se o port-forward está ativo.</div>
                  )}
                  {error.includes('Decision Engine') && (
                    <div className="mt-2 text-xs">Decision Engine offline. Verifique se o port-forward está ativo.</div>
                  )}
                  {error.includes('BC-NSSMF') && (
                    <div className="mt-2 text-xs">BC-NSSMF (Blockchain) offline. Verifique se o port-forward está ativo.</div>
                  )}
                </div>
              )}

              <Button type="submit" disabled={loading || !selectedTemplate} className="w-full">
                {loading ? 'Processando através de todos os módulos...' : 'Criar SLA'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pipeline Completo TriSLA</CardTitle>
            <CardDescription>
              Status de todos os módulos na criação do SLA
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading && !result ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <Clock className="h-5 w-5 text-gray-400 animate-spin" />
                  <div>
                    <div className="font-medium">SEM-CSMF</div>
                    <div className="text-sm text-muted-foreground">Processando...</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium">ML-NSMF</div>
                    <div className="text-sm text-muted-foreground">Aguardando...</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium">Decision Engine</div>
                    <div className="text-sm text-muted-foreground">Aguardando...</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium">BC-NSSMF (Blockchain)</div>
                    <div className="text-sm text-muted-foreground">Aguardando...</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <div>
                    <div className="font-medium">SLA-Agent Layer (Métricas)</div>
                    <div className="text-sm text-muted-foreground">Aguardando...</div>
                  </div>
                </div>
              </div>
            ) : result ? (
              <div className="space-y-4">
                {/* Linha do Tempo - SEM-CSMF */}
                <div className="flex items-center gap-3 p-3 rounded border">
                  {result.sem_csmf_status === 'OK' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <div className="flex-1">
                    <div className="font-medium">SEM-CSMF</div>
                    <div className={`text-sm ${
                      result.sem_csmf_status === 'OK' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {result.sem_csmf_status === 'OK' ? 'OK' : 'ERROR'}
                    </div>
                  </div>
                </div>

                {/* Linha do Tempo - ML-NSMF */}
                <div className="flex items-center gap-3 p-3 rounded border">
                  {result.ml_nsmf_status === 'OK' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <div className="flex-1">
                    <div className="font-medium">ML-NSMF</div>
                    <div className={`text-sm ${
                      result.ml_nsmf_status === 'OK' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {result.ml_nsmf_status === 'OK' ? 'OK' : 'ERROR'}
                    </div>
                  </div>
                </div>

                {/* Linha do Tempo - Decision Engine */}
                <div className="flex items-center gap-3 p-3 rounded border">
                  {result.decision ? (
                    result.decision === 'ACCEPT' ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )
                  ) : (
                    <Clock className="h-5 w-5 text-gray-400" />
                  )}
                  <div className="flex-1">
                    <div className="font-medium">Decision Engine</div>
                    {result.decision ? (
                      <div className={`text-sm font-bold ${
                        result.decision === 'ACCEPT' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {result.decision}
                      </div>
                    ) : (
                      <div className="text-sm text-muted-foreground">Aguardando...</div>
                    )}
                  </div>
                </div>

                {/* Decisão e Justificativa */}
                {result.decision && (
                  <>
                    <div className="p-3 bg-muted rounded text-sm space-y-2">
                      <div>
                        <div className="font-medium mb-1">Decisão:</div>
                        <div className={`font-bold ${
                          result.decision === 'ACCEPT' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {result.decision}
                        </div>
                      </div>
                      {(result.justification || result.reason) && (
                        <div>
                          <div className="font-medium mb-1">Justificativa:</div>
                          <div>{result.justification || result.reason}</div>
                        </div>
                      )}
                    </div>
                    
                    {/* Campos unificados */}
                    {result.intent_id && (
                      <div>
                        <div className="text-sm text-muted-foreground">Intent ID</div>
                        <div className="font-mono text-sm">{result.intent_id}</div>
                      </div>
                    )}
                    {result.service_type && (
                      <div>
                        <div className="text-sm text-muted-foreground">Service Type</div>
                        <div className="text-sm font-medium">{result.service_type}</div>
                      </div>
                    )}
                    {result.sla_requirements && Object.keys(result.sla_requirements).length > 0 && (
                      <div>
                        <div className="text-sm text-muted-foreground mb-1">SLA Requirements</div>
                        <pre className="p-2 bg-muted rounded text-xs overflow-auto max-h-[100px]">
                          {JSON.stringify(result.sla_requirements, null, 2)}
                        </pre>
                      </div>
                    )}
                    {result.ml_prediction && Object.keys(result.ml_prediction).length > 0 && (
                      <div>
                        <div className="text-sm text-muted-foreground mb-1">ML Prediction</div>
                        <pre className="p-2 bg-muted rounded text-xs overflow-auto max-h-[100px]">
                          {JSON.stringify(result.ml_prediction, null, 2)}
                        </pre>
                      </div>
                    )}
                    {result.sla_id && (
                      <div>
                        <div className="text-sm text-muted-foreground">SLA ID</div>
                        <div className="font-mono text-sm">{result.sla_id}</div>
                      </div>
                    )}
                    {(result.blockchain_tx_hash || result.tx_hash) && (
                      <div>
                        <div className="text-sm text-muted-foreground">Blockchain Tx Hash</div>
                        <div className="font-mono text-sm">{(result.blockchain_tx_hash || result.tx_hash).substring(0, 32)}...</div>
                      </div>
                    )}
                    {result.timestamp && (
                      <div>
                        <div className="text-sm text-muted-foreground">Timestamp</div>
                        <div className="font-mono text-sm">{result.timestamp}</div>
                      </div>
                    )}
                  </>
                )}

                {/* Linha do Tempo - BC-NSSMF */}
                <div className="flex items-center gap-3 p-3 rounded border">
                  {result.bc_status === 'CONFIRMED' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : result.bc_status === 'PENDING' ? (
                    <Clock className="h-5 w-5 text-yellow-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <div className="flex-1">
                    <div className="font-medium">BC-NSSMF (Blockchain)</div>
                    <div className={`text-sm ${
                      result.bc_status === 'CONFIRMED' ? 'text-green-600' :
                      result.bc_status === 'PENDING' ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {result.bc_status === 'CONFIRMED' ? 'CONFIRMED' :
                       result.bc_status === 'PENDING' ? 'PENDING' :
                       result.bc_status === 'ERROR' ? 'Blockchain indisponível' :
                       'ERROR'}
                    </div>
                    {(result.blockchain_tx_hash || result.tx_hash) && (
                      <div className="mt-1">
                        <div className="text-xs text-muted-foreground flex items-center gap-1">
                          <Hash className="h-3 w-3" />
                          TxHash: {(result.blockchain_tx_hash || result.tx_hash).substring(0, 16)}...
                        </div>
                      </div>
                    )}
                    {result.block_number && (
                      <div className="text-xs text-muted-foreground">
                        Block: {result.block_number}
                      </div>
                    )}
                  </div>
                </div>

                {/* Linha do Tempo - SLA-Agent Layer */}
                <div className="flex items-center gap-3 p-3 rounded border">
                  {result.sla_agent_status === 'OK' ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : result.sla_agent_status === 'SKIPPED' ? (
                    <Clock className="h-5 w-5 text-gray-400" />
                  ) : result.sla_agent_status === 'ERROR' ? (
                    <XCircle className="h-5 w-5 text-red-600" />
                  ) : (
                    <Clock className="h-5 w-5 text-gray-400" />
                  )}
                  <div className="flex-1">
                    <div className="font-medium">SLA-Agent Layer (Métricas)</div>
                    <div className={`text-sm ${
                      result.sla_agent_status === 'OK' ? 'text-green-600' :
                      result.sla_agent_status === 'SKIPPED' ? 'text-gray-500' :
                      result.sla_agent_status === 'ERROR' ? 'text-red-600' :
                      'text-gray-500'
                    }`}>
                      {result.sla_agent_status === 'OK' ? 'Métricas coletadas' :
                       result.sla_agent_status === 'SKIPPED' ? 'Pulado (REJECT ou não aplicável)' :
                       result.sla_agent_status === 'ERROR' ? 'Erro na coleta de métricas' :
                       'Pendente'}
                    </div>
                  </div>
                </div>

                {result.sla_id && result.decision === 'ACCEPT' && (
                  <Button
                    variant="outline"
                    onClick={() => router.push(`/slas/metrics?id=${result.sla_id}`)}
                    className="w-full"
                  >
                    Ver Métricas deste SLA
                  </Button>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                O resultado aparecerá aqui após criar o SLA
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

