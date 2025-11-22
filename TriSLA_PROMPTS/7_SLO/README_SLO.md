# README - SLO Reports

**TriSLA – Service Level Objective Reports e Monitoramento**

---

## 🎯 Função do Módulo

O **SLO Reporter** é responsável por:

1. **Coletar métricas** do NASP via NASP Adapter
2. **Calcular SLOs** (Service Level Objectives)
3. **Comparar SLOs com SLAs** (Service Level Agreements)
4. **Detectar violações** de SLA
5. **Registrar violações** on-chain via BC-NSSMF
6. **Gerar relatórios** de SLO para auditoria

---

## 📥 Entradas

### 1. Métricas do NASP

```json
{
  "domain": "RAN",
  "metrics": {
    "latency": 12.5,
    "throughput": 95.0,
    "reliability": 0.9998,
    "cpu_utilization": 0.65
  },
  "timestamp": "2025-01-19T10:30:00Z"
}
```

### 2. SLAs Registrados

```json
{
  "sla_id": "sla-001",
  "requirements": {
    "latency": {"max": 10, "unit": "ms"},
    "reliability": 0.99999
  },
  "status": "ACTIVE"
}
```

---

## 📤 Saídas

### 1. Relatório de SLO

```json
{
  "sla_id": "sla-001",
  "slo_metrics": {
    "latency": 12.5,
    "reliability": 0.9998
  },
  "sla_requirements": {
    "latency": {"max": 10},
    "reliability": 0.99999
  },
  "compliance": {
    "latency": false,
    "reliability": false
  },
  "overall_compliance": false,
  "violation_detected": true,
  "timestamp": "2025-01-19T10:30:00Z"
}
```

### 2. Evento de Violação

```json
{
  "sla_id": "sla-001",
  "violation_type": "LATENCY",
  "violation_value": 12.5,
  "threshold": 10.0,
  "timestamp": "2025-01-19T10:30:00Z"
}
```

---

## 🔗 Integrações

### Integração com NASP Adapter

**Fluxo:**
1. SLO Reporter solicita métricas ao NASP Adapter
2. NASP Adapter coleta métricas reais do NASP
3. NASP Adapter retorna métricas ao SLO Reporter
4. SLO Reporter calcula SLOs

### Integração com BC-NSSMF

**Fluxo:**
1. SLO Reporter detecta violação
2. SLO Reporter registra violação on-chain via BC-NSSMF
3. BC-NSSMF retorna tx_hash e block_number

### Integração com Prometheus/Grafana

**Fluxo:**
1. SLO Reporter exporta métricas para Prometheus
2. Grafana visualiza métricas e SLOs
3. Alertas configurados no Prometheus

---

## 🎯 Responsabilidades

1. **Coleta contínua** de métricas do NASP
2. **Cálculo de SLOs** em tempo real
3. **Comparação** SLO vs SLA
4. **Detecção de violações** automática
5. **Registro on-chain** de violações
6. **Geração de relatórios** para auditoria
7. **Observabilidade** (métricas, traces, logs)

---

## 🔄 Relação com Decision Engine

O SLO Reporter **não se comunica diretamente** com o Decision Engine:

- **Comunica com:** NASP Adapter (métricas) e BC-NSSMF (violações)
- **Decision Engine** pode consultar relatórios de SLO
- **Relação:** Indireta (via BC-NSSMF)

---

## 📋 Requisitos Técnicos

### Tecnologias

- **Python 3.12+**
- **FastAPI** - Framework web
- **Prometheus** - Armazenamento de métricas
- **Grafana** - Visualização
- **OTLP** - Observabilidade

### Dependências

- **6_NASP** - Coleta métricas via NASP Adapter
- **4_BLOCKCHAIN** - Registra violações via BC-NSSMF
- **Prometheus/Grafana** - Armazenamento e visualização

---

## 📚 Referências à Dissertação

- **Capítulo 4** - Arquitetura e Design
- **Capítulo 5** - Implementação e Validação
- **SLO Reports** - Monitoramento e auditoria
- **Violações** - Detecção e registro

---

## ✔ Módulo Completo e Documentado

