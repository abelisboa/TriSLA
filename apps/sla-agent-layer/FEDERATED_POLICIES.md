# Políticas Federadas - SLA-Agent Layer

## Visão Geral

Políticas federadas permitem ações coordenadas entre múltiplos domínios (RAN, Transport, Core) no SLA-Agent Layer.

## Estrutura de Política

```yaml
name: "policy-name"
priority: "high" | "medium" | "low"
domains: ["RAN", "Transport", "Core"]
actions:
  - domain: "RAN"
    action:
      type: "ADJUST_PRB"
      parameters:
        prb_allocation: 0.7
    depends_on: []  # Opcional: lista de domínios dos quais depende
  - domain: "Transport"
    action:
      type: "ADJUST_BANDWIDTH"
      parameters:
        bandwidth: 100
    depends_on: ["RAN"]  # Depende de RAN executar primeiro
```

## Prioridades

- **high**: Política de alta prioridade (executada primeiro)
- **medium**: Política de prioridade média
- **low**: Política de baixa prioridade (executada por último)

## Dependências

Ações podem depender de outras ações em diferentes domínios:

```yaml
actions:
  - domain: "RAN"
    action: {...}
    depends_on: []  # Sem dependências
  - domain: "Transport"
    action: {...}
    depends_on: ["RAN"]  # Depende de RAN
  - domain: "Core"
    action: {...}
    depends_on: ["RAN", "Transport"]  # Depende de ambos
```

O coordenador determina automaticamente a ordem de execução usando ordenação topológica.

## Exemplos

### Exemplo 1: Ajuste Coordenado de Recursos

```json
{
  "name": "coordinated-resource-adjustment",
  "priority": "high",
  "actions": [
    {
      "domain": "RAN",
      "action": {
        "type": "ADJUST_PRB",
        "parameters": {"prb_allocation": 0.8}
      }
    },
    {
      "domain": "Transport",
      "action": {
        "type": "ADJUST_BANDWIDTH",
        "parameters": {"bandwidth": 1000}
      }
    },
    {
      "domain": "Core",
      "action": {
        "type": "SCALE_RESOURCES",
        "parameters": {"replicas": 3}
      }
    }
  ]
}
```

### Exemplo 2: Política com Dependências

```json
{
  "name": "sequential-adjustment",
  "priority": "medium",
  "actions": [
    {
      "domain": "RAN",
      "action": {
        "type": "ADJUST_PRB",
        "parameters": {"prb_allocation": 0.7}
      },
      "depends_on": []
    },
    {
      "domain": "Transport",
      "action": {
        "type": "ADJUST_BANDWIDTH",
        "parameters": {"bandwidth": 800}
      },
      "depends_on": ["RAN"]
    },
    {
      "domain": "Core",
      "action": {
        "type": "SCALE_RESOURCES",
        "parameters": {"replicas": 2}
      },
      "depends_on": ["RAN", "Transport"]
    }
  ]
}
```

## API

### Aplicar Política Federada

```bash
POST /api/v1/policies/federated
Content-Type: application/json

{
  "name": "policy-name",
  "priority": "high",
  "actions": [...]
}
```

### Resposta

```json
{
  "policy_name": "policy-name",
  "priority": "high",
  "results": {
    "RAN": {
      "executed": true,
      "result": {...}
    },
    "Transport": {
      "executed": true,
      "result": {...}
    }
  },
  "executed_count": 2,
  "total_count": 2,
  "success_rate": 1.0,
  "timestamp": "2025-01-27T12:00:00Z"
}
```

## Tratamento de Erros

Se uma ação falhar:

1. A ação é marcada como `executed: false`
2. Ações dependentes não são executadas
3. O resultado inclui informações de erro
4. O `success_rate` reflete a taxa de sucesso

## Ciclos de Dependência

Se houver ciclo de dependências, o coordenador:

1. Tenta resolver o máximo possível
2. Adiciona ações restantes ao final
3. Registra warning no log

## Integração com Interface I-06

Políticas federadas são parte da Interface I-06, permitindo:

- Coordenação de ações entre domínios
- Execução sequencial baseada em dependências
- Monitoramento de resultados agregados






