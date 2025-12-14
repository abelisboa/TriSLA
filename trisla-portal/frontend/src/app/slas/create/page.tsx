'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiFetch, APIError } from '@/lib/api'
import { Etapa1Schema, Etapa2Schema, Etapa3Schema, SLAFormSchema, type Etapa1Input, type Etapa2Input, type Etapa3Input } from '@/lib/validation'
import { z } from 'zod'
import { FileText, CheckCircle, XCircle, ArrowRight, ArrowLeft } from 'lucide-react'

export default function SLACreationPage() {
  const router = useRouter()
  const [etapa, setEtapa] = useState<1 | 2 | 3>(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Dados das etapas
  const [etapa1Data, setEtapa1Data] = useState<Partial<Etapa1Input>>({
    categoria_servico_opcional: 'AUTO',
    tenant_id: 'default'
  })
  const [etapa2Data, setEtapa2Data] = useState<Partial<Etapa2Input>>({})
  const [etapa3Data, setEtapa3Data] = useState<Partial<Etapa3Input>>({
    dominios_env: []
  })
  
  // Resultado da interpretação (ETAPA 1 → ETAPA 2)
  const [interpretResult, setInterpretResult] = useState<any>(null)

  // ETAPA 1: Interpretar intenção
  const handleEtapa1 = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    
    try {
      // Validar com Zod
      const validated = Etapa1Schema.parse(etapa1Data)
      
      setLoading(true)
      const data = await apiFetch("/sla/interpret", {
        method: "POST",
        body: JSON.stringify({
          tenant_id: validated.tenant_id,
          intent_text: validated.descricao_intencao
        }),
        headers: { "Content-Type": "application/json" }
      })
      
      setInterpretResult(data)
      
      // Preencher ETAPA 2 com dados sugeridos pelo SEM-CSMF
      if (data.service_type || data.slice_type) {
        const tipoSlice = (data.service_type || data.slice_type || 'URLLC').toUpperCase()
        setEtapa2Data({
          tipo_slice: tipoSlice as 'URLLC' | 'eMBB' | 'mMTC',
          latencia_maxima_ms: data.sla_requirements?.latency ? parseFloat(String(data.sla_requirements.latency).replace('ms', '')) : (tipoSlice === 'URLLC' ? 10 : tipoSlice === 'eMBB' ? 50 : 100),
          disponibilidade_percent: data.sla_requirements?.availability ? parseFloat(String(data.sla_requirements.availability).replace('%', '')) : (tipoSlice === 'URLLC' ? 99.99 : tipoSlice === 'eMBB' ? 99.9 : 95),
          confiabilidade_percent: data.sla_requirements?.reliability ? parseFloat(String(data.sla_requirements.reliability).replace('%', '')) : (tipoSlice === 'URLLC' ? 99.99 : tipoSlice === 'eMBB' ? 99.9 : 95),
        })
      }
      
      setEtapa(2)
    } catch (err: any) {
      if (err instanceof z.ZodError) {
        setError(err.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', '))
      } else {
        const apiError = err as APIError
        setError(apiError.message || 'Erro ao interpretar SLA')
      }
    } finally {
      setLoading(false)
    }
  }

  // ETAPA 2: Validar e avançar
  const handleEtapa2 = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    
    try {
      Etapa2Schema.parse(etapa2Data)
      setEtapa(3)
    } catch (err: any) {
      if (err instanceof z.ZodError) {
        setError(err.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', '))
      }
    }
  }

  // ETAPA 3: Submeter SLA completo
  const handleEtapa3 = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    
    try {
      // Validar todas as etapas
      const validated = SLAFormSchema.parse({
        ...etapa1Data,
        ...etapa2Data,
        ...etapa3Data
      })
      
      setLoading(true)
      
      // Converter para formato esperado pelo backend
      const submitData = {
        template_id: `template-${validated.tipo_slice.toLowerCase()}`,
        tenant_id: validated.tenant_id,
        form_values: {
          type: validated.tipo_slice,
          latency: validated.latencia_maxima_ms,
          reliability: validated.confiabilidade_percent,
          availability: validated.disponibilidade_percent,
          throughput_dl: validated.throughput_min_dl_mbps,
          throughput_ul: validated.throughput_min_ul_mbps,
          device_count: validated.numero_dispositivos,
          coverage_area: validated.area_cobertura,
          mobility: validated.mobilidade,
          duration: validated.duracao_sla,
          priority: validated.prioridade_sla,
          penalty_type: validated.penalidade_tipo,
          penalty_percent: validated.penalidade_percent,
          domains: validated.dominios_env
        }
      }
      
      const result = await apiFetch("/sla/submit", {
        method: "POST",
        body: JSON.stringify(submitData),
        headers: { "Content-Type": "application/json" }
      })
      
      // Redirecionar para página de resultado ou métricas
      if (result.sla_id) {
        router.push(`/slas/metrics?id=${result.sla_id}`)
      }
    } catch (err: any) {
      if (err instanceof z.ZodError) {
        setError(err.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', '))
      } else {
        const apiError = err as APIError
        setError(apiError.message || 'Erro ao criar SLA')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <FileText className="h-8 w-8" />
          TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN
        </h1>
        <p className="text-muted-foreground">
          Formulário em 3 etapas conforme arquitetura TriSLA (Cap. 4, 5 e 6)
        </p>
      </div>

      {/* Indicador de Etapas */}
      <div className="flex items-center justify-center gap-4 mb-6">
        <div className={`flex items-center gap-2 ${etapa >= 1 ? 'text-primary' : 'text-muted-foreground'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${etapa >= 1 ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
            {etapa > 1 ? <CheckCircle className="h-5 w-5" /> : '1'}
          </div>
          <span className="text-sm font-medium">Intenção</span>
        </div>
        <ArrowRight className="h-5 w-5 text-muted-foreground" />
        <div className={`flex items-center gap-2 ${etapa >= 2 ? 'text-primary' : 'text-muted-foreground'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${etapa >= 2 ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
            {etapa > 2 ? <CheckCircle className="h-5 w-5" /> : '2'}
          </div>
          <span className="text-sm font-medium">Parâmetros</span>
        </div>
        <ArrowRight className="h-5 w-5 text-muted-foreground" />
        <div className={`flex items-center gap-2 ${etapa >= 3 ? 'text-primary' : 'text-muted-foreground'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${etapa >= 3 ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
            3
          </div>
          <span className="text-sm font-medium">Negócio</span>
        </div>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="text-red-800 text-sm">
              <div className="font-medium mb-1">Erro:</div>
              <div>{error}</div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ETAPA 1: Intenção de SLA */}
      {etapa === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>ETAPA 1 — Intenção de SLA (PNL + Dados gerais)</CardTitle>
            <CardDescription>
              Descreva sua intenção em linguagem natural. O SEM-CSMF interpretará e sugerirá parâmetros técnicos.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleEtapa1} className="space-y-4">
              <div>
                <label className="text-sm font-medium">
                  Título do Serviço <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={etapa1Data.titulo_servico || ''}
                  onChange={(e) => setEtapa1Data({ ...etapa1Data, titulo_servico: e.target.value })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  placeholder="Ex: Cirurgia Remota com Baixa Latência"
                  minLength={5}
                  maxLength={80}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1">5-80 caracteres</p>
              </div>

              <div>
                <label className="text-sm font-medium">
                  Descrição da Intenção <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={etapa1Data.descricao_intencao || ''}
                  onChange={(e) => setEtapa1Data({ ...etapa1Data, descricao_intencao: e.target.value })}
                  className="w-full mt-1 px-3 py-2 border rounded-md min-h-[150px]"
                  placeholder="Ex: Preciso de um slice para cirurgia remota com latência máxima de 5ms e confiabilidade de 99.999%. O serviço deve suportar até 10 dispositivos médicos simultâneos."
                  minLength={50}
                  required
                />
                <p className="text-xs text-muted-foreground mt-1">Mínimo 50 caracteres. Aceita erros de digitação.</p>
              </div>

              <div>
                <label className="text-sm font-medium">Categoria de Serviço (Opcional)</label>
                <select
                  value={etapa1Data.categoria_servico_opcional || 'AUTO'}
                  onChange={(e) => setEtapa1Data({ ...etapa1Data, categoria_servico_opcional: e.target.value as any })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                >
                  <option value="AUTO">AUTO (SEM-CSMF decide)</option>
                  <option value="URLLC">URLLC</option>
                  <option value="eMBB">eMBB</option>
                  <option value="mMTC">mMTC</option>
                </select>
                <p className="text-xs text-muted-foreground mt-1">Se AUTO, o SEM-CSMF (PNL) decidirá o tipo de slice</p>
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Interpretando...' : 'Interpretar e Avançar'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* ETAPA 2: Parâmetros Técnicos */}
      {etapa === 2 && (
        <Card>
          <CardHeader>
            <CardTitle>ETAPA 2 — Parâmetros Técnicos Sugeridos pelo SEM-CSMF (editáveis)</CardTitle>
            <CardDescription>
              Ajuste os parâmetros técnicos sugeridos pelo SEM-CSMF conforme necessário.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleEtapa2} className="space-y-4">
              {interpretResult && (
                <div className="p-3 bg-green-50 border border-green-200 rounded text-green-800 text-sm mb-4">
                  <div className="font-medium">Interpretação do SEM-CSMF:</div>
                  <div>Service Type: {interpretResult.service_type || interpretResult.slice_type || 'N/A'}</div>
                  {interpretResult.sla_requirements && (
                    <div className="mt-1">SLA Requirements: {JSON.stringify(interpretResult.sla_requirements)}</div>
                  )}
                </div>
              )}

              <div>
                <label className="text-sm font-medium">
                  Tipo de Slice <span className="text-red-500">*</span>
                </label>
                <select
                  value={etapa2Data.tipo_slice || ''}
                  onChange={(e) => setEtapa2Data({ ...etapa2Data, tipo_slice: e.target.value as any })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  required
                >
                  <option value="">Selecione...</option>
                  <option value="URLLC">URLLC (1-20ms, min 99.99%)</option>
                  <option value="eMBB">eMBB (10-100ms, min 99.9%)</option>
                  <option value="mMTC">mMTC (50-1000ms, min 95%)</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">
                  Latência Máxima (ms) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={etapa2Data.latencia_maxima_ms || ''}
                  onChange={(e) => setEtapa2Data({ ...etapa2Data, latencia_maxima_ms: parseFloat(e.target.value) || 0 })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  min={1}
                  max={1000}
                  step={0.1}
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">
                  Disponibilidade (%) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={etapa2Data.disponibilidade_percent || ''}
                  onChange={(e) => setEtapa2Data({ ...etapa2Data, disponibilidade_percent: parseFloat(e.target.value) || 0 })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  min={95}
                  max={99.999}
                  step={0.001}
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">
                  Confiabilidade (%) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={etapa2Data.confiabilidade_percent || ''}
                  onChange={(e) => setEtapa2Data({ ...etapa2Data, confiabilidade_percent: parseFloat(e.target.value) || 0 })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  min={95}
                  max={99.999}
                  step={0.001}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Throughput DL (Mbps)</label>
                  <input
                    type="number"
                    value={etapa2Data.throughput_min_dl_mbps || ''}
                    onChange={(e) => setEtapa2Data({ ...etapa2Data, throughput_min_dl_mbps: parseFloat(e.target.value) || undefined })}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    min={1}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Throughput UL (Mbps)</label>
                  <input
                    type="number"
                    value={etapa2Data.throughput_min_ul_mbps || ''}
                    onChange={(e) => setEtapa2Data({ ...etapa2Data, throughput_min_ul_mbps: parseFloat(e.target.value) || undefined })}
                    className="w-full mt-1 px-3 py-2 border rounded-md"
                    min={1}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Número de Dispositivos</label>
                <input
                  type="number"
                  value={etapa2Data.numero_dispositivos || ''}
                  onChange={(e) => setEtapa2Data({ ...etapa2Data, numero_dispositivos: parseInt(e.target.value) || undefined })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  min={1}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Área de Cobertura</label>
                <input
                  type="text"
                  value={etapa2Data.area_cobertura || ''}
                  onChange={(e) => setEtapa2Data({ ...etapa2Data, area_cobertura: e.target.value })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Mobilidade</label>
                <select
                  value={etapa2Data.mobilidade || ''}
                  onChange={(e) => setEtapa2Data({ ...etapa2Data, mobilidade: e.target.value as any })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                >
                  <option value="">Selecione...</option>
                  <option value="ESTATICO">ESTATICO</option>
                  <option value="PEDESTRE">PEDESTRE</option>
                  <option value="VEICULAR">VEICULAR</option>
                  <option value="ALTA">ALTA</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">Duração do SLA</label>
                <input
                  type="text"
                  value={etapa2Data.duracao_sla || ''}
                  onChange={(e) => setEtapa2Data({ ...etapa2Data, duracao_sla: e.target.value })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  placeholder="Ex: 1 ano, 6 meses"
                />
              </div>

              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => setEtapa(1)} className="flex-1">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Voltar
                </Button>
                <Button type="submit" className="flex-1">
                  Avançar
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* ETAPA 3: Requisitos de Negócio */}
      {etapa === 3 && (
        <Card>
          <CardHeader>
            <CardTitle>ETAPA 3 — Requisitos de Negócio (Capítulo 6 — BC-NSSMF)</CardTitle>
            <CardDescription>
              Configure os requisitos de negócio que alimentarão o modelo de contratos inteligentes.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleEtapa3} className="space-y-4">
              <div>
                <label className="text-sm font-medium">
                  Prioridade do SLA <span className="text-red-500">*</span>
                </label>
                <select
                  value={etapa3Data.prioridade_sla || ''}
                  onChange={(e) => setEtapa3Data({ ...etapa3Data, prioridade_sla: e.target.value as any })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  required
                >
                  <option value="">Selecione...</option>
                  <option value="BRONZE">BRONZE</option>
                  <option value="PRATA">PRATA</option>
                  <option value="OURO">OURO</option>
                  <option value="PLATINA">PLATINA</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">
                  Tipo de Penalidade <span className="text-red-500">*</span>
                </label>
                <select
                  value={etapa3Data.penalidade_tipo || ''}
                  onChange={(e) => setEtapa3Data({ ...etapa3Data, penalidade_tipo: e.target.value as any })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  required
                >
                  <option value="">Selecione...</option>
                  <option value="DESCONTO">DESCONTO</option>
                  <option value="REEMBOLSO">REEMBOLSO</option>
                  <option value="CREDITO">CREDITO</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">
                  Percentual de Penalidade (0-100%) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={etapa3Data.penalidade_percent || ''}
                  onChange={(e) => setEtapa3Data({ ...etapa3Data, penalidade_percent: parseFloat(e.target.value) || 0 })}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                  min={0}
                  max={100}
                  step={0.1}
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">
                  Domínios Envolvidos <span className="text-red-500">*</span>
                </label>
                <div className="mt-2 space-y-2">
                  {['RAN', 'TRANSPORTE', 'CORE'].map(dominio => (
                    <label key={dominio} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={etapa3Data.dominios_env?.includes(dominio as any) || false}
                        onChange={(e) => {
                          const current = etapa3Data.dominios_env || []
                          if (e.target.checked) {
                            setEtapa3Data({ ...etapa3Data, dominios_env: [...current, dominio as any] })
                          } else {
                            setEtapa3Data({ ...etapa3Data, dominios_env: current.filter(d => d !== dominio) })
                          }
                        }}
                        className="rounded"
                      />
                      <span className="text-sm">{dominio}</span>
                    </label>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Selecione pelo menos um domínio</p>
              </div>

              <div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={etapa3Data.aceite_termos || false}
                    onChange={(e) => setEtapa3Data({ ...etapa3Data, aceite_termos: e.target.checked })}
                    className="rounded"
                    required
                  />
                  <span className="text-sm font-medium">
                    Aceito os termos e condições <span className="text-red-500">*</span>
                  </span>
                </label>
              </div>

              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => setEtapa(2)} className="flex-1">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Voltar
                </Button>
                <Button type="submit" disabled={loading || !etapa3Data.aceite_termos} className="flex-1">
                  {loading ? 'Criando SLA...' : 'Criar SLA'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

