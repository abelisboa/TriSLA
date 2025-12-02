# FASE 4.1 — AUDITORIA DA INTEGRAÇÃO ATUAL
## Decision Engine ↔ ML-NSMF v3.7.0

**Data:** 2025-01-27  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Esta auditoria mapeia o caminho completo de integração entre o Decision Engine e o ML-NSMF, identificando pontos de chamada, formatos de request/response e possíveis desalinhamentos com o modelo v3.7.0.

---

## 🔍 ARQUIVOS-CHAVE IDENTIFICADOS

### Decision Engine

1. **`apps/decision-engine/src/ml_client.py`**
   - Classe: `MLClient`
   - Método principal: `predict_viability(decision_input: DecisionInput) -> MLPrediction`
   - Método auxiliar: `_extract_features(decision_input: DecisionInput) -> Dict[str, Any]`
   - **Endpoint chamado:** `{config.ml_nsmf_http_url}/api/v1/predict` (HTTP POST)

2. **`apps/decision-engine/src/engine.py`**
   - Classe: `DecisionEngine`
   - Método: `decide(intent_id, nest_id, context) -> DecisionResult`
   - **Linha 80:** Chama `self.ml_client.predict_viability(decision_input)`

3. **`apps/decision-engine/src/models.py`**
   - Modelos: `DecisionInput`, `MLPrediction`, `SLAIntent`, `NestSubset`
   - Define estruturas de dados para comunicação

4. **`apps/decision-engine/src/config.py`**
   - Configuração: `ml_nsmf_http_url` (padrão: `http://127.0.0.1:8081`)

### ML-NSMF

1. **`apps/ml_nsmf/src/main.py`**
   - Endpoint: `POST /api/v1/predict`
   - Função: `predict_risk(metrics: dict) -> dict`
   - **Linha 72:** Chama `predictor.normalize(metrics)`
   - **Linha 75:** Chama `predictor.predict(normalized)`

2. **`apps/ml_nsmf/src/predictor.py`**
   - Classe: `RiskPredictor`
   - Método: `normalize(metrics: Dict[str, Any]) -> np.ndarray`
   - Método: `predict(normalized_metrics: np.ndarray) -> Dict[str, Any]`
   - **Linha 120:** Encoding: `{"URLLC": 1, "eMBB": 2, "mMTC": 3}`

---

## 📤 REQUEST: Decision Engine → ML-NSMF

### Formato do Payload (JSON)

O método `_extract_features()` em `ml_client.py` monta o seguinte payload:

```python
{
    "latency": float,              # Extraído de sla_requirements["latency"]
    "throughput": float,            # Extraído de sla_requirements["throughput"]
    "reliability": float,           # Extraído de sla_requirements["reliability"] (default: 0.99)
    "jitter": float,                # Extraído de sla_requirements["jitter"]
    "packet_loss": float,           # Calculado: 1.0 - reliability (se não especificado)
    "service_type": int,            # Mapeado: {"eMBB": 1, "URLLC": 2, "mMTC": 3}
    "cpu_cores": float,             # Do NEST.resources["cpu"] (se disponível)
    "memory_gb": float,             # Do NEST.resources["memory"] (se disponível)
    "bandwidth_mbps": float         # Do NEST.resources["bandwidth"] (se disponível)
}
```

### Campos Enviados vs Campos Necessários

| Campo Enviado | Campo Necessário pelo Modelo | Status |
|---------------|------------------------------|--------|
| `latency` | `latency` | ✅ OK |
| `throughput` | `throughput` | ✅ OK |
| `reliability` | `reliability` | ✅ OK |
| `jitter` | `jitter` | ✅ OK |
| `packet_loss` | `packet_loss` | ✅ OK |
| `service_type` | `slice_type` | ⚠️ **NOME DIFERENTE** |
| `cpu_cores` | `cpu_utilization` | ⚠️ **NOME E TIPO DIFERENTE** |
| `memory_gb` | `memory_utilization` | ⚠️ **NOME E TIPO DIFERENTE** |
| `bandwidth_mbps` | `network_bandwidth_available` | ⚠️ **NOME DIFERENTE** |
| ❌ **AUSENTE** | `active_slices_count` | ❌ **FALTANDO** |
| ❌ **AUSENTE** | `latency_throughput_ratio` | ✅ Calculado no predictor |
| ❌ **AUSENTE** | `reliability_packet_loss_ratio` | ✅ Calculado no predictor |
| ❌ **AUSENTE** | `jitter_latency_ratio` | ✅ Calculado no predictor |

---

## 📥 RESPONSE: ML-NSMF → Decision Engine

### Formato do Payload (JSON)

O endpoint `/api/v1/predict` retorna:

```json
{
    "prediction": {
        "risk_score": float,        # 0.0 - 1.0
        "risk_level": str,          # "low" | "medium" | "high"
        "viability_score": float,   # 0.0 - 1.0 (se model_used = true)
        "confidence": float,        # 0.0 - 1.0
        "timestamp": str,           # ISO format
        "model_used": bool          # true se modelo foi usado
    },
    "explanation": {
        "method": str,              # "SHAP" | "LIME" | "XAI" | "fallback"
        "features_importance": {},  # Dict[str, float]
        "reasoning": str,           # Texto explicativo
        "shap_available": bool,
        "lime_available": bool
    }
}
```

### Processamento no Decision Engine

O método `predict_viability()` em `ml_client.py`:

1. **Linha 50:** Extrai `data.get("prediction", {})`
2. **Linha 54:** Mapeia `risk_score` → `MLPrediction.risk_score`
3. **Linha 55:** Mapeia `risk_level` → `MLPrediction.risk_level`
4. **Linha 56:** Mapeia `confidence` → `MLPrediction.confidence`
5. **Linha 57-58:** Extrai `explanation.features_importance` e `explanation.reasoning`
6. ⚠️ **NÃO extrai `viability_score`** — apenas `risk_score` é usado

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 1. **Desalinhamento de Encoding de Slice Type**

**Localização:** `apps/decision-engine/src/ml_client.py:130`

```python
service_type_map = {"eMBB": 1, "URLLC": 2, "mMTC": 3}
```

**Mas o predictor espera:**
```python
{"URLLC": 1, "eMBB": 2, "mMTC": 3}  # apps/ml_nsmf/src/predictor.py:120
```

**Impacto:** ❌ **CRÍTICO** — Encoding incorreto causará predições erradas!

### 2. **Nome de Campo Inconsistente**

- Decision Engine envia: `service_type`
- Predictor espera: `slice_type`

**Impacto:** ⚠️ **MÉDIO** — O predictor usa default "eMBB" se não encontrar `slice_type`.

### 3. **Features Ausentes ou Nomeadas Diferentemente**

| Feature Necessária | Feature Enviada | Status |
|-------------------|-----------------|--------|
| `cpu_utilization` (0-1) | `cpu_cores` (número absoluto) | ⚠️ Tipo diferente |
| `memory_utilization` (0-1) | `memory_gb` (GB absolutos) | ⚠️ Tipo diferente |
| `network_bandwidth_available` | `bandwidth_mbps` | ⚠️ Nome diferente |
| `active_slices_count` | ❌ Ausente | ❌ **FALTANDO** |

**Impacto:** ⚠️ **MÉDIO** — O predictor usa defaults, mas valores podem estar incorretos.

### 4. **Viability Score Não Utilizado**

O Decision Engine não extrai nem utiliza `viability_score` do response, apenas `risk_score`.

**Impacto:** ⚠️ **BAIXO** — Funcional, mas perde informação útil.

### 5. **Tratamento de Erros**

**Localização:** `apps/decision-engine/src/ml_client.py:67-85`

Em caso de erro HTTP ou exceção:
- Retorna `MLPrediction` com `risk_score=0.5` (fallback)
- Não sinaliza claramente que está em modo degradado
- Não verifica se `model_used = false` no response

**Impacto:** ⚠️ **MÉDIO** — Pode mascarar problemas de integração.

---

## 🔄 FLUXO COMPLETO DE INTEGRAÇÃO

```
1. Decision Engine.decide()
   ↓
2. MLClient.predict_viability(decision_input)
   ↓
3. MLClient._extract_features(decision_input)
   → Monta payload JSON
   ↓
4. HTTP POST → http://127.0.0.1:8081/api/v1/predict
   ↓
5. ML-NSMF main.py: predict_risk(metrics: dict)
   ↓
6. RiskPredictor.normalize(metrics)
   → Calcula features derivadas
   → Mapeia slice_type → slice_type_encoded
   → Normaliza com scaler
   ↓
7. RiskPredictor.predict(normalized)
   → Predição do modelo
   → Calcula risk_score = 1 - viability_score
   ↓
8. RiskPredictor.explain(prediction, normalized)
   → Gera explicação XAI
   ↓
9. Response JSON → Decision Engine
   ↓
10. MLClient converte para MLPrediction
   ↓
11. Decision Engine usa risk_score para decisão
```

---

## 📊 PONTOS DE POSSÍVEL DESALINHAMENTO

### 1. **Encoding de Slice Type**
- ❌ **CRÍTICO:** Decision Engine usa `{eMBB:1, URLLC:2, mMTC:3}`
- ✅ Modelo treinado com: `{URLLC:1, eMBB:2, mMTC:3}`
- **Ação necessária:** Corrigir mapeamento no `ml_client.py`

### 2. **Nome de Campo**
- ⚠️ Decision Engine envia `service_type`
- ⚠️ Predictor espera `slice_type`
- **Ação necessária:** Padronizar nome ou ajustar predictor

### 3. **Features de Recursos**
- ⚠️ Decision Engine envia valores absolutos (`cpu_cores`, `memory_gb`)
- ⚠️ Predictor espera valores normalizados (0-1) ou usa defaults
- **Ação necessária:** Converter ou ajustar defaults

### 4. **Feature Ausente**
- ❌ `active_slices_count` não é enviado
- ⚠️ Predictor usa default = 1
- **Ação necessária:** Adicionar ao payload ou ajustar default

### 5. **Viability Score**
- ⚠️ Decision Engine não utiliza `viability_score`
- ✅ Funciona, mas perde informação
- **Ação sugerida:** Extrair e usar `viability_score` também

---

## ✅ PONTOS CORRETOS

1. ✅ Endpoint HTTP correto: `/api/v1/predict`
2. ✅ Métricas básicas enviadas: latency, throughput, reliability, jitter, packet_loss
3. ✅ Features derivadas calculadas no predictor (ratios)
4. ✅ Tratamento de erros presente (fallback)
5. ✅ Estrutura de response adequada

---

## 📝 CONCLUSÃO DA AUDITORIA

### Status: ⚠️ **REQUER AJUSTES**

**Problemas críticos encontrados:**
1. ❌ Encoding de slice type incorreto (CRÍTICO)
2. ⚠️ Nome de campo inconsistente (`service_type` vs `slice_type`)
3. ⚠️ Features de recursos com nomes/tipos diferentes
4. ❌ Feature `active_slices_count` ausente

**Próximos passos:**
- FASE 4.2: Alinhar contratos e corrigir encoding
- FASE 4.3: Criar testes de integração para validar correções
- FASE 4.4: Ajustar código e melhorar logs

---

**FIM DA FASE 4.1**

