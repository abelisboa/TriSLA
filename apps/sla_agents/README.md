# TriSLA SLA-Agent Layer

Camada Federada de Agentes SLA para monitoramento e reporte de métricas em tempo real conforme especificado na FASE 2 da dissertação.

## 🎯 Visão Geral

A **SLA-Agent Layer** é uma camada federada de agentes especializados que monitoram métricas específicas de cada domínio da rede 5G/O-RAN:

- **RAN Agent**: Monitora latência, throughput, cobertura e qualidade do sinal
- **Transport Network Agent**: Monitora largura de banda, latência, jitter e perda de pacotes
- **Core Network Agent**: Monitora processamento, memória, CPU e disponibilidade de serviços

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAN Agent     │    │   TN Agent      │    │   Core Agent    │
│  (Radio Access) │    │ (Transport Net) │    │  (Core Network) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SLA COORDINATOR                             │
│  • Orquestração de agentes                                    │
│  • Interface I-05 (Kafka)                                     │
│  • Monitoramento geral                                        │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Decision Engine│
│  (Via Kafka)    │
└─────────────────┘
```

## 🚀 Funcionalidades

### **1. Agentes Especializados**

#### **RAN Agent**
- **Métricas**: Latência, throughput, cobertura, qualidade do sinal
- **Domínios**: Células de rádio, handover, densidade de conexões
- **Políticas SLA**: URLLC (< 10ms), eMBB (≥ 1 Gbps), mMTC (≥ 10k dispositivos)

#### **Transport Network Agent**
- **Métricas**: Largura de banda, latência, jitter, perda de pacotes
- **Domínios**: Links de transporte, congestionamento, utilização
- **Políticas SLA**: Latência (< 5ms), Jitter (< 1ms), Disponibilidade (≥ 99.9%)

#### **Core Network Agent**
- **Métricas**: CPU, memória, latência de processamento, disponibilidade
- **Domínios**: Serviços 5GC (AMF, SMF, UPF, PCF, UDM, AUSF, NRF, NSSF)
- **Políticas SLA**: CPU (< 80%), Memória (< 85%), Latência (< 50ms)

### **2. Interface I-05 (Kafka)**
- **Publicação**: Métricas, violações, status em tempo real
- **Consumo**: Comandos do Decision Engine
- **Tópicos**: `sla-metrics`, `sla-violations`, `sla-commands`, `sla-status`

### **3. SLA Coordinator**
- **Orquestração**: Gerencia todos os agentes SLA
- **Monitoramento**: Status geral da camada
- **Comunicação**: Interface com Decision Engine via Kafka

## 📡 APIs Disponíveis

### **Status dos Agentes**
```python
# Obter status de agente específico
sla_status = await agent.get_sla_status()

# Obter resumo de métricas
metrics_summary = await agent.get_metrics_summary()
```

### **Configuração de Políticas**
```python
# Adicionar política SLA
policy = RANSLAPolicy(
    metric_type=MetricType.LATENCY,
    threshold=10.0,
    operator="lte",
    severity="critical",
    description="Latência RAN deve ser ≤ 10ms"
)
agent.add_sla_policy(policy)
```

### **Interface Kafka**
```python
# Publicar métricas
await kafka_interface.publish_metrics("RAN", metrics)

# Publicar violação
await kafka_interface.publish_violation("RAN", violation)

# Consumir comandos
await kafka_interface.start_consuming_commands(callback)
```

## 🔧 Configuração

### **Variáveis de Ambiente**
```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Monitoramento
MONITORING_INTERVAL=5.0
RAN_MONITORING_INTERVAL=1.0
TN_MONITORING_INTERVAL=2.0
CORE_MONITORING_INTERVAL=3.0

# Logging
LOG_LEVEL=INFO
```

### **Configuração de Agentes**
```yaml
# helm/sla-agents/values.yaml
agents:
  ran:
    enabled: true
    monitoringInterval: 1.0
    cells: ["cell-001", "cell-002", "cell-003"]
  tn:
    enabled: true
    monitoringInterval: 2.0
    links: ["link-001", "link-002", "link-003"]
  core:
    enabled: true
    monitoringInterval: 3.0
    services: ["amf", "smf", "upf", "pcf"]
```

## 🚀 Deploy

### **Docker**
```bash
# Build da imagem
docker build -t ghcr.io/abelisboa/trisla-sla-agents:latest .

# Executar container
docker run -p 8080:8080 \
  -e KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
  -e MONITORING_INTERVAL=5.0 \
  ghcr.io/abelisboa/trisla-sla-agents:latest
```

### **Kubernetes/Helm**
```bash
# Deploy com Helm
helm install sla-agents ./helm/sla-agents \
  --namespace trisla-nsp \
  --values ./helm/sla-agents/values.yaml

# Verificar status
kubectl get pods -n trisla-nsp -l app.kubernetes.io/name=sla-agents
```

## 🧪 Testes

### **Teste Automatizado**
```bash
# Executar script de teste
./scripts/test_sla_agents.sh
```

### **Teste Manual**
```bash
# Verificar logs dos agentes
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents

# Verificar métricas SLA
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents | grep -i "metric"

# Verificar violações
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sla-agents | grep -i "violation"
```

## 📊 Monitoramento

### **Métricas por Domínio**

#### **RAN**
- `ran_latency_ms`: Latência de rádio
- `ran_throughput_mbps`: Throughput de rádio
- `ran_coverage_percent`: Cobertura de células
- `ran_signal_quality_dbm`: Qualidade do sinal

#### **Transport Network**
- `tn_bandwidth_mbps`: Largura de banda
- `tn_latency_ms`: Latência de transporte
- `tn_jitter_ms`: Jitter de rede
- `tn_packet_loss_percent`: Perda de pacotes

#### **Core Network**
- `core_cpu_percent`: Uso de CPU
- `core_memory_percent`: Uso de memória
- `core_processing_latency_ms`: Latência de processamento
- `core_service_availability_percent`: Disponibilidade de serviços

### **Logs Estruturados**
```json
{
  "timestamp": "2025-10-29T18:00:00Z",
  "level": "WARNING",
  "agent_id": "ran-agent-001",
  "domain": "RAN",
  "metric_type": "latency",
  "value": 12.5,
  "threshold": 10.0,
  "severity": "critical",
  "description": "Latência RAN excedeu limite"
}
```

## 🔗 Integração

### **Com Decision Engine**
- **Interface I-05**: Comunicação via Kafka
- **Métricas**: Publicação em tempo real
- **Comandos**: Recebimento de ajustes de política

### **Com Módulos TriSLA**
- **SEM-NSMF**: Análise semântica de métricas
- **ML-NSMF**: Predições baseadas em métricas
- **BC-NSSMF**: Validação contratual de SLA

## 📚 Referências

- [TriSLA Architecture](https://github.com/abelisboa/TriSLA-Portal)
- [Dissertação - Capítulo 5](docs/Referencia_Tecnica_TriSLA.md)
- [Interface I-05](docs/Referencia_Tecnica_TriSLA.md#a-interfaces-internas-i-)

## 👥 Autores

- **Abel Lisboa** - *Desenvolvimento* - [@abelisboa](https://github.com/abelisboa)
- **NASP-UNISINOS** - *Infraestrutura*

---

**TriSLA SLA-Agent Layer** - Camada Federada de Agentes SLA para Redes 5G/O-RAN 🔍
