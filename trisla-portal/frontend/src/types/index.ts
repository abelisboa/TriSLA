// Module Types
export interface Module {
  name: string
  status: 'UP' | 'DOWN' | 'DEGRADED'
  latency?: number
  error_rate?: number
  throughput?: number
  pods?: Pod[]
}

export interface Pod {
  name: string
  status: string
  ready: boolean
  restarts: number
}

// Health Types
export interface HealthGlobal {
  status: string
  modules: Module[]
  timestamp: string
}

// Metrics Types
export interface Metric {
  name: string
  value: number
  labels?: Record<string, string>
  timestamp?: string
}

// Intent Types
export interface Intent {
  id: string
  tenant_id: string
  service_type: 'eMBB' | 'URLLC' | 'mMTC'
  status: string
  created_at: string
  nest_id?: string
  decision_id?: string
}

// Contract Types
export interface Contract {
  id: string
  tenant_id: string
  intent_id: string
  nest_id: string
  decision_id: string
  blockchain_tx_hash?: string
  status: 'CREATED' | 'ACTIVE' | 'VIOLATED' | 'RENEGOTIATED' | 'TERMINATED'
  version: number
  sla_requirements: SLARequirements
  domains: string[]
  created_at: string
  activated_at?: string
  terminated_at?: string
  metadata: {
    service_type: string
    priority: string
    [key: string]: any
  }
}

export interface SLARequirements {
  latency?: {
    max?: string
    p95?: string
    p99?: string
  }
  throughput?: {
    min?: string
    guaranteed?: string
  }
  reliability?: number
  availability?: number
  jitter?: string
  packet_loss?: number
}

export interface Violation {
  id: string
  contract_id: string
  violation_type: 'LATENCY' | 'THROUGHPUT' | 'RELIABILITY' | 'AVAILABILITY' | 'JITTER' | 'PACKET_LOSS'
  metric_name: string
  expected_value: any
  actual_value: any
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  detected_at: string
  resolved_at?: string
  status: 'DETECTED' | 'ACKNOWLEDGED' | 'RESOLVED' | 'IGNORED'
}

export interface Renegotiation {
  id: string
  contract_id: string
  previous_version: number
  new_version: number
  reason: 'VIOLATION' | 'TENANT_REQUEST' | 'OPTIMIZATION'
  changes: any
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED'
  requested_at: string
  completed_at?: string
  requested_by: string
}

export interface Penalty {
  id: string
  contract_id: string
  violation_id: string
  penalty_type: 'REFUND' | 'CREDIT' | 'TERMINATION'
  amount?: number
  percentage?: number
  applied_at: string
  status: 'PENDING' | 'APPLIED' | 'WAIVED'
}

// Trace Types
export interface Trace {
  trace_id: string
  spans: Span[]
  duration: number
  service_name: string
  operation_name: string
  status: string
  start_time: string
}

export interface Span {
  span_id: string
  trace_id: string
  parent_span_id?: string
  service_name: string
  operation_name: string
  start_time: string
  duration: number
  status: string
  tags?: Record<string, any>
  logs?: Log[]
}

export interface Log {
  timestamp: string
  fields: Record<string, any>
}

// SLO Types
export interface SLO {
  name: string
  module: string
  target: number
  current: number
  status: 'MET' | 'VIOLATED' | 'WARNING'
  window: string
}

// XAI Types
export interface XAIExplanation {
  explanation_id: string
  type: 'ml_prediction' | 'decision'
  prediction_id?: string
  decision_id?: string
  method: 'SHAP' | 'LIME' | 'fallback'
  viability_score?: number
  recommendation?: string
  features_importance: Record<string, number>
  shap_values?: Record<string, number>
  reasoning: string
  visualizations?: any
}

// SLA Template Types
export interface SLATemplate {
  template_id: string
  name: string
  description: string
  service_type: string
  nest_template: any
  form_fields?: FormField[]
}

export interface FormField {
  name: string
  label: string
  type: string
  default?: any
  required: boolean
}

// Batch Types
export interface BatchJob {
  batch_id: string
  tenant_id: string
  total_slas: number
  processed_slas: number
  successful_slas: number
  failed_slas: number
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  created_at: string
  completed_at?: string
  results: BatchResult[]
}

export interface BatchResult {
  sla_index: number
  tenant_id: string
  status: 'success' | 'error'
  intent_id?: string
  nest_id?: string
  error?: string
}


