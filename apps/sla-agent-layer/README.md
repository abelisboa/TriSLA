# SLA-Agent Layer

Módulo de agentes federados para gerenciamento de SLA na TriSLA.

## Visão Geral

O SLA-Agent Layer implementa agentes autônomos para domínios RAN, Transport e Core, com coordenação federada e políticas distribuídas.

## Arquitetura

### Componentes Principais

- **AgentRAN**: Agente para domínio RAN (Radio Access Network)
- **AgentTransport**: Agente para domínio Transport
- **AgentCore**: Agente para domínio Core
- **AgentCoordinator**: Coordenador de agentes federados
- **SLOEvaluator**: Avaliador de SLOs (Service Level Objectives)
- **ActionConsumer**: Consumidor Kafka para decisões do Decision Engine (I-05)
- **EventProducer**: Produtor Kafka para eventos I-06 e I-07

### Interfaces

- **I-05**: Consumo de decisões do Decision Engine via Kafka
- **I-06**: Publicação de eventos de violação/risco de SLO e coordenação de ações
- **I-07**: Publicação de resultados de ações executadas

## Políticas Federadas

Políticas federadas permitem ações coordenadas entre múltiplos domínios:

```python
policy = {
    "name": "multi-domain-policy",
    "priority": "high",
    "actions": [
        {
            "domain": "RAN",
            "action": {"type": "ADJUST_PRB", "parameters": {...}},
            "depends_on": []  # Sem dependências
        },
        {
            "domain": "Transport",
            "action": {"type": "ADJUST_BANDWIDTH", "parameters": {...}},
            "depends_on": ["RAN"]  # Depende de RAN
        }
    ]
}
```

### Características

- **Ordem de Execução**: Ordenação topológica baseada em dependências
- **Prioridades**: Políticas podem ter prioridade alta, média ou baixa
- **Dependências**: Ações podem depender de outras ações em diferentes domínios
- **Coordenação**: Execução coordenada entre múltiplos agentes

## Coordenação de Agentes

O `AgentCoordinator` gerencia a coordenação entre agentes:

### Funcionalidades

1. **Coordenação de Ações**: Executa ações em múltiplos domínios simultaneamente
2. **Coleta Agregada**: Coleta métricas de todos os agentes
3. **Avaliação Agregada**: Avalia SLOs de todos os domínios
4. **Políticas Federadas**: Aplica políticas que envolvem múltiplos domínios

### Exemplo de Uso

```python
# Coordenar ação em múltiplos domínios
action = {
    "type": "ADJUST_RESOURCES",
    "parameters": {"resource_level": 0.8}
}

result = await coordinator.coordinate_action(
    action,
    target_domains=["RAN", "Transport"]
)
```

## SLOs (Service Level Objectives)

Cada domínio possui SLOs configurados em arquivos YAML:

- `src/config/slo_ran.yaml`: SLOs para RAN
- `src/config/slo_transport.yaml`: SLOs para Transport
- `src/config/slo_core.yaml`: SLOs para Core

### Status de SLO

- **OK**: Métrica dentro do target
- **RISK**: Métrica próxima do limite (threshold de risco)
- **VIOLATED**: Métrica violou o target

## API REST

### Endpoints

- `GET /health`: Health check dos agentes
- `POST /api/v1/agents/ran/collect`: Coleta métricas RAN
- `POST /api/v1/agents/ran/action`: Executa ação RAN
- `POST /api/v1/agents/transport/collect`: Coleta métricas Transport
- `POST /api/v1/agents/transport/action`: Executa ação Transport
- `POST /api/v1/agents/core/collect`: Coleta métricas Core
- `POST /api/v1/agents/core/action`: Executa ação Core
- `GET /api/v1/metrics/realtime`: Métricas em tempo real de todos os domínios
- `GET /api/v1/slos`: SLOs e status de compliance
- `POST /api/v1/coordinate`: Coordena ação entre múltiplos domínios (I-06)
- `POST /api/v1/policies/federated`: Aplica política federada (I-06)

## Integração com NASP

O SLA-Agent Layer integra com o NASP Adapter para:

- Coleta de métricas reais do NASP
- Execução de ações corretivas no NASP
- Monitoramento de SLOs em tempo real

### Modo Degradado

Se o NASP Adapter não estiver disponível, o sistema opera em modo degradado com métricas stub.

## Kafka Integration

### Tópicos

- `trisla-i05-actions`: Decisões do Decision Engine (consumo)
- `trisla-i06-agent-events`: Eventos de violação/risco de SLO (publicação)
- `trisla-i07-agent-actions`: Resultados de ações executadas (publicação)

### Configuração

Variáveis de ambiente:

- `KAFKA_ENABLED`: Habilitar Kafka (padrão: false)
- `KAFKA_BROKERS`: Lista de brokers Kafka (separados por vírgula)
- `KAFKA_BOOTSTRAP_SERVERS`: Servidores bootstrap (padrão: localhost:29092,kafka:9092)

## Testes

### Testes Unitários

```bash
pytest tests/unit/test_sla_agent_layer_agents.py -v
pytest tests/unit/test_sla_agent_layer_coordinator.py -v
```

### Testes de Integração

```bash
pytest tests/integration/test_sla_agent_layer_integration.py -v
```

### Testes E2E

```bash
pytest tests/integration/test_sla_agent_layer_e2e.py -v
```

## Execução Local

```bash
cd apps/sla-agent-layer
python -m uvicorn src.main:app --host 0.0.0.0 --port 8084
```

## Docker

```bash
docker build -t trisla-sla-agent-layer:latest -f apps/sla-agent-layer/Dockerfile .
docker run -p 8084:8084 trisla-sla-agent-layer:latest
```

## Observabilidade

O SLA-Agent Layer suporta OpenTelemetry (OTLP) para observabilidade distribuída.

Variáveis de ambiente:

- `OTLP_ENABLED`: Habilitar OTLP (padrão: false)
- `OTLP_ENDPOINT`: Endpoint do OTLP Collector (padrão: http://otlp-collector:4317)

## Versão

v3.7.6 (FASE A)

