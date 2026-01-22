# AUDITORIA TÉCNICA — ML-NSMF (FASE 1)
## Relatório de Execução

**Data da Auditoria:** 2025-01-27  
**Ambiente:** node006  
**Branch:** main  
**Commit Hash:** fb4e5df179be2408bf95531bfeb7b18a60e8126a  
**Estado Git:** Modificações não commitadas presentes (não afeta auditoria de leitura)

---

## 📌 PASSO 1 — Ambiente e Contexto Congelado

### ✅ Confirmação do Ambiente

- **SSH:** node006 - ✅ Conectado com sucesso
- **Diretório Base:** `/home/porvir5g/gtp5g/trisla`
- **Branch Atual:** `main`
- **Commit Hash:** `fb4e5df179be2408bf95531bfeb7b18a60e8126a`
- **Estado Git:** Modificações não commitadas (apenas leitura realizada)

---

## 📌 PASSO 2 — Localização do ML-NSMF

### ✅ Diretórios Identificados

**ML-NSMF:**
- `./apps/ml-nsmf/` - Módulo principal
- `./apps/ml-nsmf/src/` - Código fonte
- `./apps/ml-nsmf/models/` - Modelos treinados
- `./apps/ml-nsmf/training/` - Scripts de treinamento
- `./apps/ml-nsmf/data/` - Datasets

**Decision Engine:**
- `./apps/decision-engine/` - Módulo principal
- `./apps/decision-engine/src/` - Código fonte

### ✅ Arquivos Principais Identificados

**ML-NSMF:**
- `apps/ml-nsmf/src/main.py` - API FastAPI principal
- `apps/ml-nsmf/src/predictor.py` - Classe RiskPredictor (previsão de risco)
- `apps/ml-nsmf/src/kafka_consumer.py` - Consumidor Kafka
- `apps/ml-nsmf/src/kafka_producer.py` - Produtor Kafka
- `apps/ml-nsmf/models/viability_model.pkl` - Modelo ML treinado
- `apps/ml-nsmf/models/scaler.pkl` - Scaler para normalização
- `apps/ml-nsmf/models/model_metadata.json` - Metadados do modelo

**Decision Engine:**
- `apps/decision-engine/src/main.py` - API FastAPI principal
- `apps/decision-engine/src/engine.py` - **MOTOR PRINCIPAL DE DECISÃO**
- `apps/decision-engine/src/service.py` - Camada de serviço
- `apps/decision-engine/src/decision_maker.py` - Classe DecisionMaker
- `apps/decision-engine/src/rule_engine.py` - Engine de regras
- `apps/decision-engine/src/models.py` - Modelos Pydantic
- `apps/decision-engine/src/ml_client.py` - Cliente para ML-NSMF (Interface I-05)

---

## 📌 PASSO 3 — Identificação do Decision Engine

### ✅ Ocorrências de ACCEPT, REJECT, RENEG

**Arquivos com lógica de decisão:**

1. **`apps/decision-engine/src/models.py`** (linha 29-31)
   - Define enum `DecisionAction`: `ACCEPT = "AC"`, `RENEGOTIATE = "RENEG"`, `REJECT = "REJ"`

2. **`apps/decision-engine/src/decision_maker.py`** (linhas 21-23, 58-62)
   - Define enum `DecisionAction`
   - Método `_determine_action()` - lógica básica de decisão

3. **`apps/decision-engine/src/engine.py`** (linhas 113, 201, 212, 214, 222, 231, 239)
   - **FUNÇÃO PRINCIPAL:** `_apply_decision_rules()` - **PONTO ÚNICO DE DECISÃO**
   - Método `decide()` - orquestra o fluxo completo

4. **`apps/decision-engine/src/rule_engine.py`** (linhas 25, 31, 37, 43, 72-73)
   - Regras de decisão (não é o ponto principal, apenas auxiliar)

---

## 📌 PASSO 4 — Função de Decisão Isolada

### ✅ PONTO ÚNICO DE DECISÃO IDENTIFICADO

**Arquivo:** `apps/decision-engine/src/engine.py`  
**Função:** `_apply_decision_rules()`  
**Linhas:** 143-239

#### 📋 Assinatura da Função

```python
def _apply_decision_rules(
    self,
    intent,
    nest,
    ml_prediction,
    context: Optional[dict]
) -> tuple:
    """
    Aplica regras de decisão baseadas em:
    - Tipo de slice (URLLC/eMBB/mMTC)
    - Previsão do ML (risk_score, risk_level)
    - Thresholds de SLOs
    - Domínios afetados (RAN/Transporte/Core)
    
    Returns:
        (action, reasoning, slos, domains)
    """
```

#### 📋 Parâmetros de Entrada

1. **`intent`** - Objeto `SLAIntent` (do SEM-CSMF)
   - `intent_id`
   - `service_type` (SliceType: URLLC/eMBB/mMTC)
   - `sla_requirements` (dict com latency, throughput, reliability, etc.)

2. **`nest`** - Objeto `NestSubset` (opcional, do SEM-CSMF)
   - `nest_id`
   - `resources` (CPU, memory, bandwidth)

3. **`ml_prediction`** - Objeto `MLPrediction` (do ML-NSMF)
   - `risk_score` (float 0-1)
   - `risk_level` (RiskLevel: LOW/MEDIUM/HIGH)
   - `confidence` (float 0-1)
   - `explanation` (str)

4. **`context`** - Dict opcional com contexto adicional

#### 📋 Retorno

Tupla `(action, reasoning, slos, domains)` onde:
- **`action`** - `DecisionAction` (ACCEPT/RENEGOTIATE/REJECT)
- **`reasoning`** - String com justificativa
- **`slos`** - Lista de `SLARequirement`
- **`domains`** - Lista de strings (RAN/Transporte/Core)

#### 📋 Regras de Decisão Aplicadas

**REGRA 1:** Risco ALTO → REJECT
- Condição: `ml_prediction.risk_level == RiskLevel.HIGH` OU `ml_prediction.risk_score > 0.7`
- Ação: `DecisionAction.REJECT`
- Linha: 201

**REGRA 2:** URLLC com latência baixa e risco baixo → ACCEPT
- Condição: `service_type == SliceType.URLLC` AND `risk_level == LOW` AND `latency <= 10ms`
- Ação: `DecisionAction.ACCEPT`
- Linha: 212

**REGRA 3:** Risco MÉDIO → RENEGOTIATE
- Condição: `risk_level == RiskLevel.MEDIUM` OU `0.4 <= risk_score <= 0.7`
- Ação: `DecisionAction.RENEGOTIATE`
- Linha: 222

**REGRA 4:** Risco BAIXO e SLOs viáveis → ACCEPT
- Condição: `risk_level == RiskLevel.LOW` AND `risk_score < 0.4`
- Ação: `DecisionAction.ACCEPT`
- Linha: 231

**REGRA PADRÃO:** ACCEPT (com aviso)
- Condição: Nenhuma das anteriores
- Ação: `DecisionAction.ACCEPT`
- Linha: 239

#### 📋 Quem Chama Esta Função

1. **`DecisionEngine.decide()`** (linha 113 em `engine.py`)
   - Fluxo principal: SEM-CSMF → ML-NSMF → Regras → BC-NSSMF

2. **`DecisionService.process_decision_from_input()`** (linha 65 em `service.py`)
   - Usado quando dados já estão disponíveis

---

## 📌 PASSO 5 — Mapeamento de Entradas da Decisão

### ✅ Análise das Entradas

#### A decisão usa:

1. **Métricas atuais?** ✅ **SIM**
   - Extraídas do `intent.sla_requirements`:
     - `latency` (ms)
     - `throughput` (Mbps)
     - `reliability` (ratio)
     - `jitter` (ms)
   - Extraídas do `nest.resources` (se disponível):
     - `cpu` (cores)
     - `memory` (GB)
     - `bandwidth` (Mbps)

2. **Histórico?** ❌ **NÃO**
   - A decisão NÃO usa histórico de métricas passadas
   - Apenas métricas atuais do intent/NEST

3. **Scores ML?** ✅ **SIM**
   - `ml_prediction.risk_score` (0-1)
   - `ml_prediction.risk_level` (LOW/MEDIUM/HIGH)
   - `ml_prediction.confidence` (0-1)
   - **OBSERVAÇÃO CRÍTICA:** O ML-NSMF coleta métricas reais do Prometheus (FASE C2), mas a decisão usa apenas o score/level retornado, não as métricas históricas diretamente.

4. **Previsão futura explícita?** ⚠️ **PARCIAL**
   - O ML-NSMF retorna `risk_score` que é uma previsão de viabilidade futura
   - Mas a decisão usa apenas o score atual, não projeta cenários futuros
   - **GAP IDENTIFICADO:** Não há avaliação de risco futuro explícito (ex: "em 5 minutos, o risco será X")

### ✅ Fluxo de Dados

```
SEM-CSMF (I-01)
    ↓
    intent (SLAIntent) + nest (NestSubset)
    ↓
ML-NSMF (I-05) - ml_client.py
    ↓
    Extrai features do intent/nest
    ↓
    Chama /api/v1/predict do ML-NSMF
    ↓
    ML-NSMF coleta métricas reais do Prometheus (FASE C2)
    ↓
    ML-NSMF usa modelo treinado (viability_model.pkl)
    ↓
    Retorna MLPrediction (risk_score, risk_level, confidence)
    ↓
Decision Engine - _apply_decision_rules()
    ↓
    Aplica regras baseadas em:
    - ml_prediction.risk_score
    - ml_prediction.risk_level
    - intent.service_type
    - intent.sla_requirements (SLOs)
    ↓
    Retorna (action, reasoning, slos, domains)
    ↓
BC-NSSMF (I-06) - apenas se action == ACCEPT
```

### ⚠️ GAP IDENTIFICADO

**A decisão NÃO avalia risco futuro explícito:**
- Usa apenas o `risk_score` atual do ML
- Não projeta cenários futuros (ex: "em 5 minutos, o risco será X")
- Não considera tendências temporais
- Não avalia degradação futura de recursos

**O modelo ML não decide sozinho:**
- ✅ **CONFIRMADO:** O ML-NSMF apenas retorna `risk_score` e `risk_level`
- ✅ **CONFIRMADO:** A decisão final (ACCEPT/RENEG/REJECT) é tomada pelo `_apply_decision_rules()`
- ✅ **CONFIRMADO:** As regras de decisão são explícitas e baseadas em thresholds fixos

---

## 📌 PASSO 6 — Arquivos BLOQUEADOS (NÃO ALTERÁVEIS)

### 🛑 LISTA DE ARQUIVOS BLOQUEADOS

#### SEM-CSMF (BLOQUEADO)
```
apps/sem-csmf/**/*
```

#### Ontologia (BLOQUEADO)
```
apps/sem-csmf/src/ontology/**/*
```

#### PNL (BLOQUEADO)
```
apps/pnl/**/*
```

#### Templates GST / NEST (BLOQUEADO)
```
apps/sem-csmf/src/nest_generator.py
apps/sem-csmf/src/services/semantic_generator.py
```

#### Smart Contracts (BLOQUEADO)
```
apps/bc-nssmf/**/*
```

#### NASP Adapter (BLOQUEADO)
```
apps/nasp-adapter/**/*
```

#### Portal (BLOQUEADO)
```
trisla-portal/**/*
```

#### Modelos ML Treinados (BLOQUEADO)
```
apps/ml-nsmf/models/viability_model.pkl
apps/ml-nsmf/models/scaler.pkl
apps/ml-nsmf/models/model_metadata.json
```

#### Datasets (BLOQUEADO)
```
apps/ml-nsmf/data/datasets/**/*
```

#### Pipelines de Treino (BLOQUEADO)
```
apps/ml-nsmf/training/**/*
```

#### Código do ML-NSMF (BLOQUEADO - exceto interface)
```
apps/ml-nsmf/src/predictor.py
apps/ml-nsmf/src/main.py
apps/ml-nsmf/src/kafka_consumer.py
apps/ml-nsmf/src/kafka_producer.py
```

**NOTA:** O `ml_client.py` do Decision Engine pode ser ajustado apenas para extração de features, mas não para alterar a lógica de predição.

---

## 📌 PASSO 7 — Relatório de Auditoria (Resumo Técnico)

### ✅ Resultados da Auditoria

#### 1. Ponto Único de Decisão Identificado

✅ **CONFIRMADO**
- **Arquivo:** `apps/decision-engine/src/engine.py`
- **Função:** `_apply_decision_rules()` (linhas 143-239)
- **Método chamador:** `DecisionEngine.decide()` (linha 113)

#### 2. Modelo ML Não Decide Sozinho

✅ **CONFIRMADO**
- O ML-NSMF retorna apenas `risk_score` e `risk_level`
- A decisão final (ACCEPT/RENEG/REJECT) é tomada por `_apply_decision_rules()`
- As regras são explícitas e baseadas em thresholds fixos:
  - `risk_score > 0.7` → REJECT
  - `0.4 <= risk_score <= 0.7` → RENEGOTIATE
  - `risk_score < 0.4` → ACCEPT

#### 3. Decisão é Baseada em Estado Atual

✅ **CONFIRMADO**
- Usa métricas atuais do intent/NEST
- Usa `risk_score` atual do ML
- **NÃO usa histórico de métricas passadas**
- **NÃO projeta cenários futuros**

#### 4. Não Há Risco Futuro Explícito

⚠️ **GAP IDENTIFICADO**
- A decisão não avalia risco futuro explícito
- Não projeta degradação de recursos
- Não considera tendências temporais
- **Este é o gap que precisa ser corrigido na Fase 2**

#### 5. Correção Pode Ser Local e Mínima

✅ **CONFIRMADO**
- O ponto único de decisão está isolado em `_apply_decision_rules()`
- A correção pode ser feita apenas neste método
- Não requer alterações em:
  - Modelos ML
  - SEM-CSMF
  - BC-NSSMF
  - NASP Adapter
  - Portal

---

## 📋 MAPA DE DEPENDÊNCIAS DA DECISÃO

```
Decision Engine (apps/decision-engine/src/engine.py)
    │
    ├── SEM-CSMF (apps/sem-csmf/) [BLOQUEADO]
    │   └── Fornece: intent (SLAIntent) + nest (NestSubset)
    │
    ├── ML-NSMF (apps/ml-nsmf/) [BLOQUEADO - exceto interface]
    │   └── Fornece: MLPrediction (risk_score, risk_level)
    │   └── Interface: I-05 (HTTP REST)
    │   └── Cliente: ml_client.py (apps/decision-engine/src/ml_client.py)
    │
    └── BC-NSSMF (apps/bc-nssmf/) [BLOQUEADO]
        └── Recebe: DecisionResult (apenas se action == ACCEPT)
        └── Interface: I-06 (HTTP REST)
        └── Cliente: bc_client.py (apps/decision-engine/src/bc_client.py)
```

---

## 🎯 CONCLUSÃO DA AUDITORIA

### ✅ Objetivos Alcançados

1. ✅ **Ponto único de decisão identificado:** `_apply_decision_rules()` em `engine.py`
2. ✅ **Entradas mapeadas:** intent, nest, ml_prediction, context
3. ✅ **Saídas mapeadas:** action (ACCEPT/RENEG/REJECT), reasoning, slos, domains
4. ✅ **Critérios documentados:** 5 regras explícitas baseadas em thresholds
5. ✅ **Arquivos bloqueados listados:** SEM-CSMF, Ontologia, PNL, Templates, Smart Contracts, NASP Adapter, Portal, Modelos ML, Datasets, Pipelines
6. ✅ **Dependências mapeadas:** SEM-CSMF → ML-NSMF → Decision Engine → BC-NSSMF
7. ✅ **Prova de que modelo ML não decide sozinho:** Confirmado - decisão final é do `_apply_decision_rules()`

### ⚠️ Gap Identificado

**A decisão não avalia risco futuro explícito:**
- Usa apenas `risk_score` atual
- Não projeta cenários futuros
- Não considera degradação de recursos ao longo do tempo

**Este gap será corrigido na Fase 2, alterando apenas `_apply_decision_rules()`.**

---

## 🛑 REGRA DE OURO CUMPRIDA

✅ **Nenhum código foi alterado**  
✅ **Nenhum arquivo foi salvo** (exceto este relatório)  
✅ **Nenhuma dependência foi tocada**  
✅ **Apenas documentação foi gerada**

---

**Fim da Auditoria Fase 1**

