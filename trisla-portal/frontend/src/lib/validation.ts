import { z } from "zod"

// Etapa 1: Interpretação da intenção
export const Etapa1Schema = z.object({
  descricao_intencao: z.string().min(1, "Descrição da intenção é obrigatória"),
  titulo_servico: z.string().optional(),
  tenant_id: z.string().default("default"),
  categoria_servico_opcional: z.enum(["AUTO", "URLLC", "eMBB", "mMTC"]).optional().default("AUTO")
})

export type Etapa1Input = z.infer<typeof Etapa1Schema>

// Etapa 2: Parâmetros técnicos do SLA
export const Etapa2Schema = z.object({
  tipo_slice: z.enum(["URLLC", "eMBB", "mMTC"]),
  latencia_maxima_ms: z.number().min(0.1).max(1000),
  disponibilidade_percent: z.number().min(0).max(100),
  confiabilidade_percent: z.number().min(0).max(100),
  throughput_min_dl_mbps: z.number().optional(),
  throughput_min_ul_mbps: z.number().optional(),
  numero_dispositivos: z.number().optional(),
  area_cobertura: z.string().optional(),
  mobilidade: z.string().optional(),
  duracao_sla: z.string().optional()
})

export type Etapa2Input = z.infer<typeof Etapa2Schema>

// Etapa 3: Domínios e ambiente
export const Etapa3Schema = z.object({
  dominios_env: z.array(z.string()).default([]),
  penalidade_percent: z.number().optional(),
  penalidade_tipo: z.string().optional(),
  prioridade_sla: z.string().optional(),
  aceite_termos: z.boolean().optional()
})

export type Etapa3Input = z.infer<typeof Etapa3Schema>

// Schema completo do formulário SLA
export const SLAFormSchema = Etapa1Schema.merge(Etapa2Schema).merge(Etapa3Schema)

// Validation utilities
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}
