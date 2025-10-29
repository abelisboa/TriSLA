# TriSLA Closed Loop

Sistema de Closed Loop completo para orquestração SLA-aware conforme especificado na FASE 5 da dissertação.

## 🎯 Visão Geral

O Closed Loop TriSLA implementa um ciclo contínuo de:

1. **OBSERVAR** - Coletar métricas e status do sistema
2. **ANALISAR** - Detectar violações e problemas
3. **DECIDIR** - Tomar decisões baseadas na análise
4. **EXECUTAR** - Executar ações decididas
5. **AJUSTAR** - Ajustar sistema baseado nos resultados

## 🏗️ Arquitetura do Closed Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOSED LOOP CONTROLLER                      │
│  • Ciclo contínuo de observação e ajuste                      │
│  • Políticas SLA-aware                                        │
│  • Políticas adaptativas com ML                               │
│  • Ações automáticas                                          │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OBSERVAR      │    │   ANALISAR      │    │   DECIDIR       │
│  • Métricas SLA │    │  • Violações    │    │  • Ações        │
│  • Status       │    │  • Problemas    │    │  • Prioridades  │
│  • Performance  │    │  • Tendências   │    │  • Políticas    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EXECUTAR      │    │   AJUSTAR       │    │   APRENDER      │
│  • Ações SLA    │    │  • Políticas    │    │  • Adaptação    │
│  • Escalonamento│    │  • Configurações│    │  • ML Models    │
│  • Failover     │    │  • Recursos     │    │  • Otimização   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Funcionalidades

### **1. Closed Loop Controller**

#### **Ciclo Contínuo**
```python
from apps.closed_loop.controllers.closed_loop_controller import create_closed_loop_controller

# Criar controlador
controller = await create_closed_loop_controller()

# Iniciar ciclo contínuo
await controller.start()

# Parar controlador
await controller.stop()
```

#### **Estados do Ciclo**
- **IDLE**: Aguardando próximo ciclo
- **OBSERVING**: Coletando métricas e status
- **ANALYZING**: Detectando violações e problemas
- **DECIDING**: Tomando decisões baseadas na análise
- **EXECUTING**: Executando ações decididas
- **ADJUSTING**: Ajustando sistema baseado nos resultados

### **2. Políticas SLA**

#### **Tipos de Políticas**
```python
from apps.closed_loop.policies.sla_policies import create_sla_policy_manager

policy_manager = create_sla_policy_manager()

# Políticas URLLC
policy_manager.add_policy(SLAPolicy(
    policy_id="urllc_latency_critical",
    name="URLLC Latency Critical",
    policy_type=PolicyType.LATENCY,
    domain="RAN",
    slice_type="URLLC",
    threshold=10.0,
    operator="lte",
    severity=ViolationSeverity.CRITICAL,
    action_type=ActionType.ADJUST,
    parameters={"adjustment_factor": 0.8}
))

# Políticas eMBB
policy_manager.add_policy(SLAPolicy(
    policy_id="embb_bandwidth_high",
    name="eMBB Bandwidth High",
    policy_type=PolicyType.BANDWIDTH,
    domain="Transport",
    slice_type="eMBB",
    threshold=1000.0,
    operator="gte",
    severity=ViolationSeverity.HIGH,
    action_type=ActionType.SCALE,
    parameters={"scale_factor": 1.5}
))
```

#### **Avaliação de Políticas**
```python
# Avaliar métricas contra políticas
evaluations = policy_manager.evaluate_metrics({
    "latency": 15.0,
    "bandwidth": 800.0,
    "availability": 99.5
})

# Obter violações
violations = policy_manager.get_violations(ViolationSeverity.CRITICAL)
```

### **3. Políticas Adaptativas**

#### **Aprendizado Automático**
```python
from apps.closed_loop.policies.adaptive_policies import create_adaptive_policy_manager

adaptive_manager = create_adaptive_policy_manager()

# Adicionar dados de aprendizado
adaptive_manager.add_learning_data("adaptive_urllc_latency", {
    "metric_value": 12.0,
    "violated": True,
    "context": {
        "cpu_usage": 75.0,
        "memory_usage": 60.0,
        "domain": "RAN",
        "slice_type": "URLLC"
    },
    "performance": 0.8
})

# Adaptar política
result = adaptive_manager.adapt_policy("adaptive_urllc_latency", base_policy)
```

#### **Tipos de Adaptação**
- **Threshold**: Ajuste automático de thresholds
- **Parameters**: Ajuste de parâmetros usando ML
- **Action**: Seleção da melhor ação baseada na efetividade

### **4. Ações Automáticas**

#### **Tipos de Ações**
```python
from apps.closed_loop.controllers.closed_loop_controller import ActionType

# Ativação de slice
action = ClosedLoopAction(
    action_id="action-001",
    action_type=ActionType.SLICE_ACTIVATION,
    target_module="nasp-api",
    parameters={"slice_id": "slice-001", "type": "URLLC"},
    priority=4
)

# Escalonamento de recursos
action = ClosedLoopAction(
    action_id="action-002",
    action_type=ActionType.RESOURCE_SCALING,
    target_module="kubernetes",
    parameters={"resource_type": "cpu", "scale_factor": 1.5},
    priority=3
)

# Ajuste de política
action = ClosedLoopAction(
    action_id="action-003",
    action_type=ActionType.POLICY_ADJUSTMENT,
    target_module="decision-engine",
    parameters={"policy_name": "latency_policy", "threshold": 8.0},
    priority=2
)
```

## 🔧 Configuração

### **Variáveis de Ambiente**

```bash
# Closed Loop Controller
CLOSED_LOOP_ENABLED=true
CYCLE_INTERVAL=5.0
MAX_CYCLE_DURATION=300.0

# Políticas SLA
SLA_POLICIES_ENABLED=true
POLICY_EVALUATION_INTERVAL=10.0

# Políticas Adaptativas
ADAPTIVE_POLICIES_ENABLED=true
LEARNING_RATE=0.1
ADAPTATION_WINDOW=50
MIN_CONFIDENCE=0.8
```

### **Configuração de Ciclos**

```yaml
# Configuração do Closed Loop
closed_loop:
  enabled: true
  cycle_interval: 5.0
  max_cycle_duration: 300.0
  max_history_size: 100
  
  policies:
    sla_enabled: true
    adaptive_enabled: true
    evaluation_interval: 10.0
  
  actions:
    slice_activation: true
    slice_deactivation: true
    slice_modification: true
    policy_adjustment: true
    resource_scaling: true
    alert_notification: true
```

## 🧪 Testes

### **Teste Automatizado**

```bash
# Executar teste completo do Closed Loop
./scripts/test_closed_loop.sh
```

### **Teste Manual**

```bash
# Verificar logs do Closed Loop
kubectl logs -n trisla-nsp --all-containers=true | grep -i "closed.loop"

# Verificar políticas SLA
kubectl logs -n trisla-nsp --all-containers=true | grep -i "policy\|violation"

# Verificar ações automáticas
kubectl logs -n trisla-nsp --all-containers=true | grep -i "action\|automatic"
```

## 📊 Monitoramento

### **Métricas do Closed Loop**

#### **Ciclos**
- `closed_loop_cycles_total`: Total de ciclos executados
- `closed_loop_cycle_duration_seconds`: Duração dos ciclos
- `closed_loop_cycle_success_rate`: Taxa de sucesso dos ciclos

#### **Políticas**
- `sla_policies_total`: Total de políticas SLA
- `sla_violations_total`: Total de violações detectadas
- `sla_violations_by_severity`: Violações por severidade

#### **Ações**
- `closed_loop_actions_total`: Total de ações executadas
- `closed_loop_actions_by_type`: Ações por tipo
- `closed_loop_action_success_rate`: Taxa de sucesso das ações

#### **Adaptação**
- `adaptive_policies_total`: Total de políticas adaptativas
- `policy_adaptations_total`: Total de adaptações realizadas
- `adaptation_confidence_avg`: Confiança média das adaptações

### **Traces do Closed Loop**

#### **Operações Rastreadas**
- `closed_loop_cycle`: Ciclo completo do Closed Loop
- `observe_system`: Observação do sistema
- `analyze_system`: Análise do sistema
- `decide_actions`: Decisão de ações
- `execute_actions`: Execução de ações
- `adjust_system`: Ajuste do sistema

#### **Atributos de Trace**
- `cycle_id`: ID do ciclo
- `cycle_state`: Estado do ciclo
- `actions_count`: Número de ações
- `violations_count`: Número de violações
- `adaptations_count`: Número de adaptações

### **Logs Estruturados**

```json
{
  "timestamp": "2025-10-29T18:00:00Z",
  "level": "INFO",
  "service": "closed-loop",
  "cycle_id": "cycle-abc123",
  "state": "EXECUTING",
  "event": "action_executed",
  "action_type": "SLICE_MODIFICATION",
  "target_module": "nasp-api",
  "success": true,
  "duration_ms": 150
}
```

## 🔗 Integração

### **Com Módulos TriSLA**
- **Decision Engine**: Decisões SLA-aware
- **SLA-Agent Layer**: Métricas em tempo real
- **SEM-NSMF**: Análise semântica
- **ML-NSMF**: Predições e adaptação
- **BC-NSSMF**: Validação contratual

### **Com NASP**
- **Ativação de slices**: Via Interface I-06
- **Modificação de slices**: Via Interface I-07
- **Monitoramento**: Via telemetria em tempo real

### **Com Observabilidade**
- **OpenTelemetry**: Traces, métricas e logs
- **Jaeger**: Visualização de traces
- **Prometheus**: Consulta de métricas
- **Loki**: Consulta de logs

## 📚 Referências

- [TriSLA Architecture](https://github.com/abelisboa/TriSLA-Portal)
- [Dissertação - Capítulo 8](docs/Referencia_Tecnica_TriSLA.md)
- [Closed Loop Design](docs/Referencia_Tecnica_TriSLA.md#closed-loop-design)

## 👥 Autores

- **Abel Lisboa** - *Desenvolvimento* - [@abelisboa](https://github.com/abelisboa)
- **NASP-UNISINOS** - *Infraestrutura*

---

**TriSLA Closed Loop** - Orquestração SLA-Aware Automática 🔄
