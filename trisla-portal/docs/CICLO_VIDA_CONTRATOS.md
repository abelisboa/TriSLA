# Ciclo de Vida dos Contratos - TriSLA Observability Portal v4.0

**Versão:** 4.0  
**Data:** 2025-01-XX

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Estados do Contrato](#estados-do-contrato)
3. [Transições de Estado](#transições-de-estado)
4. [Violações](#violações)
5. [Renegociações](#renegociações)
6. [Penalidades](#penalidades)
7. [Histórico e Versões](#histórico-e-versões)

---

## 🎯 Visão Geral

O ciclo de vida de um contrato SLA no TriSLA Observability Portal v4.0 inclui:

- **Criação**: Contrato criado a partir de intent/NEST
- **Ativação**: Contrato ativado e em execução
- **Monitoramento**: Verificação contínua de violações
- **Renegociação**: Ajuste de termos quando necessário
- **Terminação**: Encerramento do contrato

---

## 📊 Estados do Contrato

### Diagrama de Estados

```
    ┌──────────┐
    │ CREATED  │
    └────┬─────┘
         │
         │ activate()
         ▼
    ┌──────────┐
    │  ACTIVE  │◄────┐
    └────┬─────┘     │
         │           │
         │ violate() │ renegotiate()
         ▼           │
    ┌──────────┐     │
    │ VIOLATED │─────┘
    └────┬─────┘
         │
         │ terminate()
         ▼
    ┌──────────────┐
    │ TERMINATED   │
    └──────────────┘
```

### Estados

1. **CREATED**
   - Contrato criado mas não ativado
   - Aguardando ativação

2. **ACTIVE**
   - Contrato ativo e em execução
   - Monitoramento ativo

3. **VIOLATED**
   - Violação de SLA detectada
   - Pode ser renegociado ou terminado

4. **RENEGOTIATED**
   - Contrato renegociado
   - Nova versão criada

5. **TERMINATED**
   - Contrato encerrado
   - Não pode ser reativado

---

## 🔄 Transições de Estado

### CREATED → ACTIVE

**Trigger**: Ativação manual ou automática

**Ações**:
- Define `activated_at`
- Inicia monitoramento
- Registra em blockchain (BC-NSSMF)

### ACTIVE → VIOLATED

**Trigger**: Detecção de violação de SLA

**Ações**:
- Registra violação
- Notifica tenant
- Calcula penalidade (se aplicável)

### VIOLATED → RENEGOTIATED

**Trigger**: Renegociação aprovada

**Ações**:
- Cria nova versão do contrato
- Atualiza SLA requirements
- Registra renegociação

### ACTIVE/VIOLATED → TERMINATED

**Trigger**: Terminação manual ou automática

**Ações**:
- Define `terminated_at`
- Encerra monitoramento
- Finaliza contrato

---

## ⚠️ Violações

### Tipos de Violação

1. **LATENCY**: Latência acima do limite
2. **THROUGHPUT**: Throughput abaixo do mínimo
3. **RELIABILITY**: Confiabilidade abaixo do acordado
4. **AVAILABILITY**: Disponibilidade abaixo do acordado
5. **JITTER**: Jitter acima do limite
6. **PACKET_LOSS**: Perda de pacotes acima do limite

### Severidades

- **LOW**: Violação menor, não crítica
- **MEDIUM**: Violação moderada
- **HIGH**: Violação significativa
- **CRITICAL**: Violação crítica, ação imediata necessária

### Processo de Detecção

```
1. Monitoramento contínuo de métricas
2. Comparação com SLA requirements
3. Detecção de violação
4. Registro de violação
5. Notificação (se configurado)
6. Cálculo de penalidade (se aplicável)
```

### Exemplo de Violação

```json
{
  "id": "violation-001",
  "contract_id": "contract-001",
  "violation_type": "LATENCY",
  "metric_name": "latency",
  "expected_value": "10ms",
  "actual_value": "15ms",
  "severity": "HIGH",
  "detected_at": "2025-01-19T11:00:00Z",
  "status": "DETECTED"
}
```

---

## 🔄 Renegociações

### Motivos de Renegociação

1. **VIOLATION**: Violação de SLA detectada
2. **TENANT_REQUEST**: Solicitação do tenant
3. **OPTIMIZATION**: Otimização de recursos

### Processo de Renegociação

```
1. Solicitação de renegociação
2. Análise de mudanças propostas
3. Aprovação/Rejeição
4. Se aprovada:
   - Cria nova versão do contrato
   - Atualiza SLA requirements
   - Registra histórico
```

### Exemplo de Renegociação

```json
{
  "id": "reneg-001",
  "contract_id": "contract-001",
  "previous_version": 1,
  "new_version": 2,
  "reason": "VIOLATION",
  "changes": {
    "sla_requirements": {
      "latency": {
        "old": {"max": "10ms"},
        "new": {"max": "15ms"}
      }
    }
  },
  "status": "ACCEPTED",
  "requested_at": "2025-01-19T12:00:00Z",
  "completed_at": "2025-01-19T12:05:00Z",
  "requested_by": "system"
}
```

---

## 💰 Penalidades

### Tipos de Penalidade

1. **REFUND**: Reembolso ao tenant
2. **CREDIT**: Crédito para uso futuro
3. **TERMINATION**: Terminação do contrato

### Cálculo de Penalidade

- **Baseado em severidade**: Violações críticas = penalidades maiores
- **Baseado em duração**: Violações prolongadas = penalidades maiores
- **Baseado em frequência**: Múltiplas violações = penalidades acumuladas

### Exemplo de Penalidade

```json
{
  "id": "penalty-001",
  "contract_id": "contract-001",
  "violation_id": "violation-001",
  "penalty_type": "CREDIT",
  "amount": 100.00,
  "percentage": 10.0,
  "applied_at": "2025-01-19T11:30:00Z",
  "status": "APPLIED"
}
```

---

## 📜 Histórico e Versões

### Versionamento

Cada renegociação cria uma nova versão do contrato:

- **Versão 1**: Contrato original
- **Versão 2**: Primeira renegociação
- **Versão 3**: Segunda renegociação
- ...

### Comparação de Versões

O portal permite comparar versões de contratos:

- **Diff visual**: Mostra mudanças entre versões
- **Tabela comparativa**: Compara todos os campos
- **Timeline**: Linha do tempo de mudanças

### Exemplo de Comparação

```json
{
  "contract_1": {
    "version": 1,
    "sla_requirements": {
      "latency": {"max": "10ms"}
    }
  },
  "contract_2": {
    "version": 2,
    "sla_requirements": {
      "latency": {"max": "15ms"}
    }
  },
  "diff": {
    "sla_requirements": {
      "latency": {
        "max": {
          "old": "10ms",
          "new": "15ms"
        }
      }
    }
  }
}
```

---

## ✅ Conclusão

O ciclo de vida dos contratos no TriSLA Observability Portal v4.0 fornece:

- **Estados claros**: CREATED, ACTIVE, VIOLATED, RENEGOTIATED, TERMINATED
- **Transições controladas**: Mudanças de estado rastreáveis
- **Violações**: Detecção e registro completo
- **Renegociações**: Processo estruturado de ajuste
- **Penalidades**: Cálculo e aplicação automática
- **Histórico**: Versionamento e comparação completa

---

**Status:** ✅ **CICLO DE VIDA DOS CONTRATOS DOCUMENTADO**







