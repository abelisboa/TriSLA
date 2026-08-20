# Decision Engine — Regras de Decisão Formais

> **Historical/experimental policy reference.** This 2025 rule set is preserved
> as implementation evidence; it is not the current article's scientific
> architecture baseline.

**Versão:** 3.7.4  
**Fase:** D (Decision Engine)  
**Data:** 2025-01-27

---

## 📋 Visão Geral

Este documento descreve formalmente as **regras de decisão** implementadas no Decision Engine do TriSLA. As regras determinam se um SLA (Service Level Agreement) deve ser **ACCEPT**, **RENEGOTIATE** ou **REJECT**.

---

## 🎯 Fluxo de Decisão

```
Intent (SEM-CSMF) → ML Prediction (ML-NSMF) → Decision Rules → Decision (AC/RENEG/REJ)
```

### Entradas

1. **Intent** (do SEM-CSMF)
   - Tipo de slice (URLLC, eMBB, mMTC)
   - Requisitos de SLA (latency, throughput, reliability, jitter, packet_loss)
   - Tenant ID
   - Metadata

2. **ML Prediction** (do ML-NSMF)
   - `risk_score` (0.0 - 1.0)
   - `risk_level` (low, medium, high)
   - `confidence` (0.0 - 1.0)
   - `explanation` (XAI)

3. **NEST** (opcional)
   - Network Slice Template
   - Recursos alocados
   - Status

### Saída

**DecisionResult** com:
- `action`: ACCEPT, RENEGOTIATE ou REJECT
- `reasoning`: Justificativa detalhada
- `confidence`: Confiança na decisão
- `slos`: Lista de SLOs extraídos
- `domains`: Domínios afetados (RAN, Transporte, Core)

---

## 📐 Regras de Decisão

### REGRA 1: Risco ALTO → REJECT

**Condição:**
- `ml_prediction.risk_level == HIGH` **OU**
- `ml_prediction.risk_score > 0.7`

**Ação:** `REJECT`

**Justificativa:**
```
"SLA {service_type} rejeitado. ML prevê risco ALTO (score: {risk_score:.2f}, nível: {risk_level}). 
Dominios: {domains}. {ml_explanation}"
```

**Exemplo:**
- URLLC com `risk_score = 0.8` → REJECT
- eMBB com `risk_level = HIGH` → REJECT

---

### REGRA 2: URLLC com Latência Crítica e Risco Baixo → ACCEPT

**Condição:**
- `service_type == URLLC` **E**
- `ml_prediction.risk_level == LOW` **E**
- `latency <= 10ms` (SLO de latência)

**Ação:** `ACCEPT`

**Justificativa:**
```
"SLA URLLC aceito. Latência crítica ({latency}ms) viável. 
ML prevê risco BAIXO (score: {risk_score:.2f}). 
Dominios: {domains}."
```

**Exemplo:**
- URLLC com `latency = 5ms` e `risk_score = 0.2` → ACCEPT

---

### REGRA 3: Risco MÉDIO → RENEGOTIATE

**Condição:**
- `ml_prediction.risk_level == MEDIUM` **OU**
- `0.4 <= ml_prediction.risk_score <= 0.7`

**Ação:** `RENEGOTIATE`

**Justificativa:**
```
"SLA {service_type} requer renegociação. ML prevê risco MÉDIO (score: {risk_score:.2f}). 
Recomenda-se ajustar SLOs ou recursos. Dominios: {domains}. {ml_explanation}"
```

**Exemplo:**
- eMBB com `risk_score = 0.5` → RENEGOTIATE
- mMTC com `risk_level = MEDIUM` → RENEGOTIATE

---

### REGRA 4: Risco BAIXO e SLOs Viáveis → ACCEPT

**Condição:**
- `ml_prediction.risk_level == LOW` **E**
- `ml_prediction.risk_score < 0.4`

**Ação:** `ACCEPT`

**Justificativa:**
```
"SLA {service_type} aceito. ML prevê risco BAIXO (score: {risk_score:.2f}). 
SLOs viáveis. Dominios: {domains}."
```

**Exemplo:**
- eMBB com `risk_score = 0.2` → ACCEPT
- mMTC com `risk_level = LOW` e `risk_score = 0.3` → ACCEPT

---

### REGRA PADRÃO: ACCEPT (com aviso)

**Condição:**
- Nenhuma das regras acima aplica

**Ação:** `ACCEPT`

**Justificativa:**
```
"SLA {service_type} aceito (padrão). ML score: {risk_score:.2f}. Dominios: {domains}."
```

**Observação:** Esta regra é um fallback de segurança. Em produção, deve-se revisar casos que chegam aqui.

---

## 🎯 Thresholds

### Thresholds Globais

| Threshold | Valor | Unidade | Descrição |
|-----------|-------|---------|-----------|
| `latency_max` | 100.0 | ms | Latência máxima aceitável |
| `throughput_min` | 50.0 | Mbps | Throughput mínimo aceitável |
| `packet_loss_max` | 0.01 | ratio | Packet loss máximo (1%) |
| `sla_compliance_min` | 0.95 | ratio | SLA compliance mínimo (95%) |

### Thresholds por Tipo de Slice

#### URLLC
- **Latência:** ≤ 10ms (crítico)
- **Reliability:** ≥ 0.999 (99.9%)
- **Domínios:** RAN, Transporte, Core (todos)

#### eMBB
- **Latência:** ≤ 50ms
- **Throughput:** ≥ 100Mbps
- **Domínios:** RAN, Transporte

#### mMTC
- **Latência:** ≤ 1000ms (tolerável)
- **Throughput:** ≥ 10Mbps
- **Domínios:** RAN, Core

---

## 🔄 Prioridade das Regras

As regras são avaliadas na seguinte ordem (prioridade):

1. **REGRA 1** (Prioridade 1) — Risco ALTO → REJECT
2. **REGRA 2** (Prioridade 2) — URLLC crítico → ACCEPT
3. **REGRA 3** (Prioridade 3) — Risco MÉDIO → RENEGOTIATE
4. **REGRA 4** (Prioridade 4) — Risco BAIXO → ACCEPT
5. **REGRA PADRÃO** (Prioridade 5) — ACCEPT

**Nota:** A primeira regra que faz match é aplicada (short-circuit evaluation).

---

## 📊 Mapeamento de Domínios

### Por Tipo de Slice

| Tipo de Slice | Domínios Afetados | Justificativa |
|---------------|-------------------|---------------|
| **URLLC** | RAN, Transporte, Core | Requer todos os domínios para garantir latência ultra-baixa |
| **eMBB** | RAN, Transporte | Foca em banda larga e throughput |
| **mMTC** | RAN, Core | Foca em densidade e conectividade |

---

## 🔍 Integração com ML-NSMF

### Uso do Risk Score

O `risk_score` do ML-NSMF é usado diretamente nas regras:

- **risk_score > 0.7** → REJECT (REGRA 1)
- **0.4 ≤ risk_score ≤ 0.7** → RENEGOTIATE (REGRA 3)
- **risk_score < 0.4** → ACCEPT (REGRA 4)

### Uso do Risk Level

O `risk_level` (low, medium, high) é usado como critério adicional:

- **HIGH** → REJECT (REGRA 1)
- **MEDIUM** → RENEGOTIATE (REGRA 3)
- **LOW** → ACCEPT (REGRA 4)

### Uso da Explicação XAI

A `explanation` do ML-NSMF é incluída na justificativa da decisão quando disponível.

---

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Thresholds (opcional - usar valores padrão se não definidos)
DECISION_LATENCY_MAX=100.0
DECISION_THROUGHPUT_MIN=50.0
DECISION_PACKET_LOSS_MAX=0.01
DECISION_SLA_COMPLIANCE_MIN=0.95

# Risk Score Thresholds
DECISION_RISK_HIGH_THRESHOLD=0.7
DECISION_RISK_MEDIUM_THRESHOLD=0.4
```

---

## 🧪 Validação

### Testes Unitários

- ✅ `test_rule_engine_high_risk_reject` — REGRA 1
- ✅ `test_rule_engine_medium_risk_renegotiate` — REGRA 3
- ✅ `test_rule_engine_high_sla_compliance_accept` — REGRA 4
- ✅ `test_rule_engine_default_accept` — REGRA PADRÃO

### Testes de Integração

- ✅ `test_integration_decision_service_accept` — Fluxo ACCEPT
- ✅ `test_integration_decision_service_reject` — Fluxo REJECT
- ✅ `test_integration_decision_service_different_slice_types` — Todos os tipos

### Testes E2E

- ✅ `test_e2e_urllc_low_risk_accept` — URLLC → ACCEPT
- ✅ `test_e2e_embb_high_risk_reject` — eMBB → REJECT
- ✅ `test_e2e_mmtc_medium_risk_renegotiate` — mMTC → RENEGOTIATE

---

## 📝 Exemplos de Decisões

### Exemplo 1: URLLC Aceito

**Input:**
- Tipo: URLLC
- Latência: 5ms
- ML: risk_score = 0.2, risk_level = LOW

**Output:**
- Action: ACCEPT
- Reasoning: "SLA URLLC aceito. Latência crítica (5ms) viável. ML prevê risco BAIXO (score: 0.20). Dominios: RAN, Transporte, Core."

---

### Exemplo 2: eMBB Rejeitado

**Input:**
- Tipo: eMBB
- ML: risk_score = 0.8, risk_level = HIGH

**Output:**
- Action: REJECT
- Reasoning: "SLA eMBB rejeitado. ML prevê risco ALTO (score: 0.80, nível: high). Dominios: RAN, Transporte. [explicação XAI]"

---

### Exemplo 3: mMTC Renegociado

**Input:**
- Tipo: mMTC
- ML: risk_score = 0.5, risk_level = MEDIUM

**Output:**
- Action: RENEGOTIATE
- Reasoning: "SLA mMTC requer renegociação. ML prevê risco MÉDIO (score: 0.50). Recomenda-se ajustar SLOs ou recursos. Dominios: RAN, Core. [explicação XAI]"

---

## 🔄 Atualizações Futuras

### Melhorias Planejadas

1. **Regras Configuráveis:** Carregar regras de arquivo YAML/JSON
2. **Machine Learning de Regras:** Aprender thresholds ótimos
3. **Multi-tenant:** Regras específicas por tenant
4. **Time-based Rules:** Regras que variam por horário/carga

---

**Status:** ✅ Documentação formal das regras concluída

**Última atualização:** 2025-01-27






