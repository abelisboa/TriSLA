# Auditoria de Observabilidade TriSLA v3.9.2
**Data:** 2025-01-21  
**Ambiente:** NASP (node006)  
**Namespace:** trisla  
**Versão:** v3.9.2  
**Status:** ✅ AUDITORIA COMPLETA - FASE 1 (READ-ONLY)

---

## 📋 RESUMO EXECUTIVO

Esta auditoria verifica a existência e funcionalidade da observabilidade na arquitetura TriSLA v3.9.2, conforme especificado no prompt de correção. A auditoria foi executada em modo **READ-ONLY**, sem alterações no sistema.

### Decisão Final

🔧 **A observabilidade precisa de correções mínimas, aqui especificadas**

---

## 🧭 MACROFASE I — AUDITORIA DE OBSERVABILIDADE EXISTENTE

### FASE 1 — Auditoria de Latência End-to-End

#### Objetivo
Verificar se o sistema gera timestamps reais para:
- Submissão de SLA
- Decisão
- Kafka
- Blockchain

#### Ações Executadas

1. **Inspeção de Código-Fonte (read-only):**
   - ✅ Portal Backend: `portal-backend-patch/src/routers/sla.py`
   - ✅ Decision Engine: `apps/decision-engine/src/decision_engine.py`
   - ✅ ML-NSMF: `apps/ml-nsmf/src/ml_nsmf.py`
   - ✅ BC-NSSMF: `apps/bc-nssmf/src/`

2. **Busca por Timestamps:**
   - ✅ `time.time()` encontrado em múltiplos arquivos
   - ✅ `datetime.utcnow()` encontrado em alguns arquivos
   - ⚠️ `datetime.now()` encontrado em alguns arquivos

#### Evidências Encontradas

**Portal Backend (`sla.py`):**
- Linha 329: Tenta obter `timestamp` de `result.get("timestamp")`
- ⚠️ **NÃO gera timestamp próprio na submissão**

**Decision Engine (`decision_engine.py`):**
- Linha 170: `start_time = time.time()` - usado apenas para latência interna
- Linha 263: `observe_decision_latency(start_time)` - métrica Prometheus
- ⚠️ **NÃO persiste timestamp na resposta de decisão**

**Decision Engine Models (`models.py`):**
- Linha 77: `MLPrediction` **REQUER** campo `timestamp: str` (obrigatório)
- Linha 120: `DecisionResult` tem `timestamp` com default factory
- ✅ Modelo Pydantic está correto

**ML-NSMF (`ml_nsmf.py`):**
- Linha 262: `start_time = time.time()` - usado apenas para latência interna
- ⚠️ **NÃO inclui timestamp na resposta de `assess_viability()`**

**ML-NSMF API (`main.py`):**
- Endpoint `/api/v1/predict` (linhas 120-125)
- ⚠️ **NÃO inclui timestamp no retorno**

**ML-NSMF Predictor (`predictor.py`):**
- Método `predict()` (linhas 100-115)
- ⚠️ **NÃO inclui timestamp no dicionário retornado**

#### Critério de Sucesso

❌ **FALHA:** Timestamps não são gerados e persistidos no runtime

**Problemas Identificados:**
1. ML-NSMF não retorna campo `timestamp` obrigatório, causando erro de validação Pydantic no Decision Engine
2. Portal Backend não captura timestamp de submissão
3. Decision Engine não persiste timestamp de decisão na resposta
4. Timestamps são usados apenas para métricas internas (latência), não para rastreabilidade

---

### FASE 2 — Auditoria de Rastreabilidade Kafka

#### Objetivo
Confirmar se o Kafka participa efetivamente do fluxo de decisão.

#### Ações Executadas

1. **Verificação de Producers:**
   - ✅ Decision Engine: `apps/decision-engine/src/kafka_producer_retry.py`
   - ✅ ML-NSMF: `apps/ml-nsmf/src/kafka_producer.py`
   - ✅ NASP Adapter: Verificado logs

2. **Verificação de Tópicos:**
   - ❌ Tentativa de listar tópicos falhou (kafka-topics.sh não encontrado)
   - ⚠️ Kafka pod está rodando, mas ferramentas não disponíveis

3. **Verificação de Status:**
   - ✅ Kafka pod: `kafka-c948b8d64-jgmz5` - Running (1/1)
   - ⚠️ Health check Decision Engine: `"kafka": "offline"`
   - ⚠️ Health check ML-NSMF: `"kafka": "offline"`

#### Evidências Encontradas

**Decision Engine Health Check:**
```json
{
  "status": "healthy",
  "module": "decision-engine",
  "kafka": "offline",
  "rule_engine": "ready",
  "decision_service": "ready"
}
```

**ML-NSMF Health Check:**
```json
{
  "status": "healthy",
  "module": "ml-nsmf",
  "kafka": "offline",
  "predictor": "ready"
}
```

**Código-Fonte:**
- ✅ `kafka_producer.py` existe em ML-NSMF
- ✅ `kafka_producer_retry.py` existe em Decision Engine
- ⚠️ Kafka está configurado como opcional (`KAFKA_ENABLED=false`)

#### Critério de Sucesso

❌ **FALHA:** Kafka está offline e não participa do fluxo real

**Problemas Identificados:**
1. Kafka está configurado como opcional e desabilitado por padrão
2. Mensagens não são persistidas em tópicos
3. Rastreabilidade via Kafka não está funcional

---

### FASE 3 — Auditoria de Métricas de Machine Learning

#### Objetivo
Verificar se o ML-NSMF expõe e persiste métricas quantitativas reais.

#### Campos Obrigatórios a Auditar
- `model_used`
- `confidence`
- `probability`
- `risk_score`

#### Ações Executadas

1. **Inspeção de Payload de Inferência:**
   - ✅ `apps/ml-nsmf/src/ml_nsmf.py` - função `assess_viability()`

2. **Inspeção de Resposta da API:**
   - ✅ `apps/ml-nsmf/src/main.py` - endpoint `/api/v1/predict`

3. **Inspeção de Logs:**
   - ⚠️ Logs não mostram métricas estruturadas

#### Evidências Encontradas

**ML-NSMF `assess_viability()` (linhas 364-373):**
```python
return {
    "prediction": prediction,
    "confidence": confidence,  # ✅ Presente
    "viability_score": viability_score,
    "model_used": True,  # ✅ Presente
    "metrics_ran": metrics_ran,
    "metrics_tn": metrics_tn,
    "metrics_core": metrics_core,
    "reason": f"Modelo ML aplicado com {total_metrics} métricas..."
}
```

**Campos Encontrados:**
- ✅ `model_used`: Presente
- ✅ `confidence`: Presente
- ⚠️ `probability`: Não encontrado (usado `viability_score`)
- ⚠️ `risk_score`: Não encontrado (usado `viability_score`)

**ML-NSMF Predictor (`predictor.py`):**
- Linhas 100-115: Retorna `risk_score` e `risk_level`
- ⚠️ Mas não é usado pelo endpoint principal

**Problema Conhecido:**
- ❌ ML-NSMF retorna HTTP 500 devido à falta de campo `timestamp` obrigatório
- Documentado em: `trisla/docs/technical/TRISLA_AUDIT_S6_BLOCKCHAIN_PIPELINE.md`

#### Critério de Sucesso

⚠️ **PARCIAL:** Métricas existem no código, mas não são expostas devido a erro de validação

**Problemas Identificados:**
1. Campo `timestamp` ausente causa falha antes de retornar métricas
2. `probability` e `risk_score` não estão no formato esperado
3. Métricas não são persistidas em arquivos/CSV

---

### FASE 4 — Auditoria de Explicabilidade (XAI)

#### Objetivo
Confirmar se o XAI está integrado ao fluxo real de inferência.

#### Ações Executadas

1. **Verificação de Chamadas XAI:**
   - ✅ `apps/ml-nsmf/src/ml_nsmf.py` - função `explain_prediction()` (linhas 390-546)
   - ✅ `apps/ml-nsmf/src/xai_logging.py` - persistência de explicações

2. **Verificação de Arquivos:**
   - ✅ `xai_logging.py` existe e implementa CSV logging
   - ⚠️ `xai_registry.csv` não encontrado (pode estar no container)

3. **Verificação de Integração:**
   - ✅ Endpoint `/api/v1/explain` existe em `main.py` (linhas 147-200)
   - ⚠️ Endpoint principal `/api/v1/predict` não chama XAI automaticamente

#### Evidências Encontradas

**XAI Logging (`xai_logging.py`):**
- ✅ Implementa persistência em CSV
- ✅ Headers: `timestamp`, `slice_type`, `nest_id`, `prediction`, `confidence`, `model_used`, `method`, `explanation_available`, `top_features`, `feature_count`
- ✅ Usa `datetime.now(timezone.utc).isoformat()` para timestamps

**XAI Function (`ml_nsmf.py`):**
- ✅ Função `explain_prediction()` implementada (linhas 390-546)
- ✅ Usa SHAP quando disponível
- ✅ Retorna `feature_importance`, `shap_values`, `top_features`
- ⚠️ SHAP pode não estar instalado (`SHAP_AVAILABLE` check)

**Integração:**
- ⚠️ Endpoint `/api/v1/predict` não chama `explain_prediction()` automaticamente
- ✅ Endpoint `/api/v1/explain` existe mas requer chamada separada

#### Critério de Sucesso

⚠️ **PARCIAL:** XAI existe mas não está integrado ao fluxo principal

**Problemas Identificados:**
1. XAI não é chamado automaticamente no fluxo de predição
2. Explicações não são geradas para cada decisão
3. Persistência em CSV existe mas pode não estar sendo usada

---

### FASE 5 — Auditoria de Blockchain

#### Objetivo
Verificar se:
- O BC-NSSMF está funcional
- A ausência de dados é apenas consequência lógica (sem ACCEPT)

#### Ações Executadas

1. **Verificação de Regra:**
   - ✅ Portal Backend: Gate lógico implementado (linhas 320-355 em `sla.py`)
   - ✅ Blockchain executa apenas para ACCEPT

2. **Verificação de Logs:**
   - ⚠️ Deployment `bc-nssmf` não encontrado (nome pode ser diferente)
   - ✅ Pods BC-NSSMF: `trisla-bc-nssmf-7c8ff9c4fc-kwmqd` - Running (1/1)

3. **Verificação de Código:**
   - ✅ `apps/bc-nssmf/src/main.py` existe
   - ✅ `apps/bc-nssmf/src/service.py` existe

#### Evidências Encontradas

**Portal Backend Gate (`sla.py`):**
- Linha 321: `if decision == "ACCEPT":` - Gate explícito
- Linha 322: Log indica que BC-NSSMF deve ser acionado
- ✅ Comportamento consistente com especificação

**Status dos Pods:**
- ✅ `trisla-bc-nssmf-7c8ff9c4fc-kwmqd` - Running (1/1)
- ⚠️ `trisla-bc-nssmf-59b5d676ff-h6ngq` - ImagePullBackOff

**Problema Conhecido:**
- ❌ Fluxo não alcança BC-NSSMF devido a bloqueio no ML-NSMF
- Documentado em: `trisla/docs/technical/S6_11_NASP_RESULTS.md`

#### Critério de Sucesso

✅ **COMPORTAMENTO CONSISTENTE:** BC-NSSMF não é chamado porque não há ACCEPT (devido a bloqueio anterior)

**Observações:**
1. Gate lógico está correto
2. BC-NSSMF não recebe requisições porque fluxo bloqueia antes
3. Comportamento é esperado dado o bloqueio no ML-NSMF

---

## 🧪 MACROFASE II — DIAGNÓSTICO E DECISÃO

### FASE 6 — Consolidação da Auditoria

#### O que já existe

1. ✅ **Estrutura de Observabilidade:**
   - Módulos de métricas Prometheus implementados
   - Funções de latência implementadas
   - XAI implementado (mas não integrado)

2. ✅ **Modelos Pydantic:**
   - `MLPrediction` requer `timestamp` (correto)
   - `DecisionResult` tem `timestamp` com default (correto)

3. ✅ **Gate Lógico:**
   - Portal Backend implementa gate ACCEPT/RENEG/REJECT corretamente

4. ✅ **XAI Logging:**
   - Implementação de persistência em CSV existe

#### O que não existe

1. ❌ **Timestamps Persistidos:**
   - ML-NSMF não retorna `timestamp` na resposta
   - Portal Backend não captura timestamp de submissão
   - Decision Engine não persiste timestamp de decisão

2. ❌ **Kafka Funcional:**
   - Kafka está offline/desabilitado
   - Mensagens não são persistidas

3. ❌ **Métricas Expostas:**
   - ML-NSMF não retorna métricas devido a erro de validação
   - Métricas não são persistidas em arquivos

4. ❌ **XAI Integrado:**
   - XAI não é chamado automaticamente no fluxo

#### O que existe mas não funciona

1. ⚠️ **ML-NSMF API:**
   - Endpoint existe mas retorna HTTP 500
   - Falta campo `timestamp` obrigatório

2. ⚠️ **Kafka:**
   - Código existe mas está desabilitado
   - Health checks mostram "offline"

3. ⚠️ **XAI:**
   - Implementação existe mas não é chamada automaticamente

---

### FASE 7 — DECISÃO CONDICIONAL (OBRIGATÓRIA)

#### Análise

**Timestamps:** ❌ Não existem ou não são persistidos  
**Kafka:** ❌ Offline/desabilitado  
**Métricas ML:** ⚠️ Existem mas não são expostas (erro de validação)  
**XAI:** ⚠️ Existe mas não integrado  
**Blockchain:** ✅ Comportamento consistente (não recebe requisições por bloqueio anterior)

#### Decisão

➡️ **AUTORIZAR MACROFASE III**

**Justificativa:**
- Timestamps são críticos e estão ausentes
- Kafka está offline e precisa ser habilitado
- ML-NSMF precisa retornar `timestamp` para funcionar
- XAI precisa ser integrado ao fluxo principal

---

## 🔧 MACROFASE III — CORREÇÃO SEM REGRESSÃO (CONDICIONAL)

### FASE 8 — Proposição de Correções Mínimas

#### C1: Adicionar Timestamp na Resposta do ML-NSMF 🔴 CRÍTICO

**Arquivo:** `apps/ml-nsmf/src/ml_nsmf.py`  
**Função:** `assess_viability()` (linha ~364)  
**Linha:** ~373

**Correção:**
```python
from datetime import datetime, timezone

# No retorno de assess_viability(), adicionar:
return {
    "prediction": prediction,
    "confidence": confidence,
    "viability_score": viability_score,
    "model_used": True,
    "metrics_ran": metrics_ran,
    "metrics_tn": metrics_tn,
    "metrics_core": metrics_core,
    "reason": f"Modelo ML aplicado com {total_metrics} métricas...",
    "timestamp": datetime.now(timezone.utc).isoformat()  # ✅ ADICIONAR
}
```

**Impacto:** Apenas instrumentação, sem alterar lógica decisória

---

#### C2: Adicionar Timestamp no Endpoint ML-NSMF API

**Arquivo:** `apps/ml-nsmf/src/main.py`  
**Função:** `predict_risk()` (endpoint `/api/v1/predict`)  
**Linha:** ~120

**Correção:**
```python
from datetime import datetime, timezone

# No retorno do endpoint, adicionar timestamp:
return {
    "prediction": prediction,
    "explanation": explanation,
    "metrics_used": prediction["metrics_used"],
    "timestamp": datetime.now(timezone.utc).isoformat()  # ✅ ADICIONAR
}
```

**Impacto:** Apenas instrumentação

---

#### C3: Adicionar Timestamp na Submissão do Portal Backend

**Arquivo:** `portal-backend-patch/src/routers/sla.py`  
**Função:** `submit_sla_template()`  
**Linha:** ~248

**Correção:**
```python
from datetime import datetime, timezone

# Após receber request, capturar timestamp:
t_submit = datetime.now(timezone.utc).isoformat()
logger.info(f"🔍 PAYLOAD_RECEBIDO: template_id={request.template_id}, t_submit={t_submit}")

# Incluir no nest_template ou passar para nasp_service
```

**Impacto:** Apenas instrumentação

---

#### C4: Adicionar Timestamp na Decisão do Decision Engine

**Arquivo:** `apps/decision-engine/src/decision_engine.py`  
**Função:** `evaluate_decision()`  
**Linha:** ~276

**Correção:**
```python
from datetime import datetime, timezone

# No retorno de evaluate_decision(), adicionar:
return {
    "decision": decision,
    "reason": reason,
    "justification": reason,
    "sla_compliance": sla_compliance,
    "threshold": threshold_min,
    "slice_type": slice_type.upper(),
    "model_used": model_used,
    "metrics_used": threshold_config["metrics_required"],
    "ml_prediction": ml_prediction,
    "timestamp": datetime.now(timezone.utc).isoformat()  # ✅ ADICIONAR
}
```

**Impacto:** Apenas instrumentação

---

#### C5: Habilitar Kafka (Opcional - Requer Configuração)

**Arquivo:** `apps/decision-engine/src/main.py` e `apps/ml-nsmf/src/main.py`  
**Ação:** Verificar variável de ambiente `KAFKA_ENABLED`

**Correção:**
- Verificar se Kafka está configurado corretamente
- Habilitar `KAFKA_ENABLED=true` se infraestrutura estiver pronta
- Adicionar timestamps nas mensagens Kafka

**Impacto:** Requer configuração de infraestrutura

---

#### C6: Integrar XAI ao Fluxo Principal

**Arquivo:** `apps/ml-nsmf/src/main.py`  
**Função:** `predict_risk()`  
**Linha:** ~120

**Correção:**
```python
# Após gerar prediction, chamar explain_prediction automaticamente:
explanation = explain_prediction(
    slice_type=metrics.get("slice_type", "UNKNOWN"),
    sla_requirements=metrics.get("sla_requirements", {}),
    prediction_result=prediction,
    nest_id=metrics.get("nest_id")
)

# Salvar explicação:
from xai_logging import log_xai_explanation, save_xai_to_csv
log_xai_explanation(explanation, slice_type, nest_id)
save_xai_to_csv(explanation, slice_type, nest_id)
```

**Impacto:** Apenas instrumentação, sem alterar lógica decisória

---

### FASE 9 — Plano de Correção Controlada

#### Ordem Segura de Aplicação

1. **C1 + C2:** Adicionar timestamp no ML-NSMF (crítico para desbloquear fluxo)
2. **C4:** Adicionar timestamp no Decision Engine
3. **C3:** Adicionar timestamp no Portal Backend
4. **C6:** Integrar XAI ao fluxo principal
5. **C5:** Habilitar Kafka (após verificar infraestrutura)

#### Rollback Simples

Todas as correções são aditivas (apenas adicionam campos). Rollback:
- Reverter commits
- Ou remover linhas adicionadas

#### Impacto Esperado

✅ **Apenas em observabilidade:**
- Timestamps serão gerados e persistidos
- XAI será chamado automaticamente
- Kafka será habilitado (se infraestrutura permitir)
- **Nenhuma alteração em lógica decisória**
- **Nenhuma alteração em thresholds**
- **Nenhuma alteração em modelos ML**

---

### FASE 10 — Gate Final

#### Critérios de Aprovação

✅ **Observabilidade completa:**
- Timestamps em submissão, decisão, Kafka, Blockchain
- Métricas ML expostas e persistidas
- XAI integrado e persistido

✅ **Sem regressão funcional:**
- Lógica decisória inalterada
- Thresholds inalterados
- Modelos ML inalterados

✅ **Sem impacto arquitetural:**
- Apenas instrumentação adicionada
- Contratos de API mantidos (apenas campos adicionados)

✅ **Métricas suficientes para banca e artigo:**
- Timestamps para latência end-to-end
- Rastreabilidade Kafka
- Métricas ML quantitativas
- Explicações XAI

---

## 📄 RESULTADO FINAL

### Decisão

🔧 **"A observabilidade precisa de correções mínimas, aqui especificadas"**

### Correções Necessárias

1. ✅ **C1 + C2:** Adicionar `timestamp` no ML-NSMF (CRÍTICO)
2. ✅ **C4:** Adicionar `timestamp` no Decision Engine
3. ✅ **C3:** Adicionar `timestamp` no Portal Backend
4. ✅ **C6:** Integrar XAI ao fluxo principal
5. ⚠️ **C5:** Habilitar Kafka (requer verificação de infraestrutura)

### Evidências Técnicas

- ✅ Código-fonte inspecionado
- ✅ Logs verificados
- ✅ Modelos Pydantic verificados
- ✅ Health checks verificados
- ✅ Problemas conhecidos documentados

### Próximos Passos

1. Aplicar correções C1, C2, C4, C3, C6
2. Testar fluxo end-to-end
3. Verificar persistência de timestamps
4. Verificar geração de explicações XAI
5. Avaliar habilitar Kafka (C5)

---

**Fim da Auditoria**
