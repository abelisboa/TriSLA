# FASE 4.2 — ALINHAMENTO DE CONTRATOS
## Features, Tipos e Normalização - ML-NSMF v3.7.0

**Data:** 2025-01-27  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Esta fase alinhou os contratos entre Decision Engine e ML-NSMF v3.7.0, corrigindo encoding de slice type, padronizando nomes de campos, adicionando features faltantes e melhorando tratamento de erros.

---

## 🔧 CORREÇÕES APLICADAS

### 1. **Encoding de Slice Type Corrigido** ✅

**Problema:**
- Decision Engine usava: `{"eMBB": 1, "URLLC": 2, "mMTC": 3}`
- Modelo treinado com: `{"URLLC": 1, "eMBB": 2, "mMTC": 3}`

**Solução:**
```python
# ANTES (apps/decision-engine/src/ml_client.py:130)
service_type_map = {"eMBB": 1, "URLLC": 2, "mMTC": 3}
features["service_type"] = service_type_map.get(...)

# DEPOIS
slice_type_map = {"URLLC": 1, "eMBB": 2, "mMTC": 3}
features["slice_type"] = decision_input.intent.service_type.value  # String
features["slice_type_encoded"] = slice_type_map.get(..., 2)  # Numérico
```

**Impacto:** ✅ **CRÍTICO** — Encoding agora alinhado com modelo v3.7.0

---

### 2. **Nome de Campo Padronizado** ✅

**Problema:**
- Decision Engine enviava: `service_type`
- Predictor esperava: `slice_type`

**Solução:**
- Agora envia ambos: `slice_type` (string) e `slice_type_encoded` (numérico)
- Predictor pode usar qualquer um, mas prefere `slice_type` string

**Impacto:** ✅ **RESOLVIDO** — Compatibilidade garantida

---

### 3. **Features de Recursos Corrigidas** ✅

**Problema:**
- Decision Engine enviava valores absolutos: `cpu_cores`, `memory_gb`, `bandwidth_mbps`
- Predictor esperava valores normalizados: `cpu_utilization`, `memory_utilization`, `network_bandwidth_available`

**Solução:**
```python
# Conversão de CPU cores → utilization (0-1)
cpu_cores = float(resources.get("cpu", 0))
features["cpu_utilization"] = min(1.0, cpu_cores / 10.0) if cpu_cores > 0 else 0.5

# Conversão de Memory GB → utilization (0-1)
memory_gb = float(memory_str) if memory_str else 0.0
features["memory_utilization"] = min(1.0, memory_gb / 100.0) if memory_gb > 0 else 0.5

# Bandwidth: usar diretamente em Mbps
features["network_bandwidth_available"] = float(bandwidth_str) if bandwidth_str else 500.0
```

**Defaults aplicados:**
- `cpu_utilization`: 0.5 (50%)
- `memory_utilization`: 0.5 (50%)
- `network_bandwidth_available`: 500.0 Mbps

**Impacto:** ✅ **RESOLVIDO** — Features agora no formato esperado

---

### 4. **Feature `active_slices_count` Adicionada** ✅

**Problema:**
- Feature ausente no payload
- Predictor usava default = 1

**Solução:**
```python
# Tentar obter do contexto ou NEST metadata
if decision_input.context and "active_slices_count" in decision_input.context:
    features["active_slices_count"] = float(decision_input.context["active_slices_count"])
elif decision_input.nest and decision_input.nest.metadata:
    features["active_slices_count"] = float(decision_input.nest.metadata.get("active_slices_count", 1))
else:
    features["active_slices_count"] = 1.0  # Default
```

**Impacto:** ✅ **MELHORADO** — Feature agora pode ser enviada quando disponível

---

### 5. **Extração de `viability_score` Adicionada** ✅

**Problema:**
- Decision Engine não extraía `viability_score` do response
- Perdia informação útil

**Solução:**
```python
# Extrair viability_score se disponível
viability_score = prediction_data.get("viability_score")
if viability_score is not None:
    span.set_attribute("ml.viability_score", float(viability_score))
    # Adicionar ao explanation
    if prediction.explanation:
        prediction.explanation = f"[viability_score={viability_score:.4f}] {prediction.explanation}"
```

**Impacto:** ✅ **MELHORADO** — Informação adicional disponível

---

### 6. **Tratamento de Erros Melhorado** ✅

**Problema:**
- Não verificava `model_used = false`
- Não sinalizava claramente modo fallback

**Solução:**
```python
# Verificar se modelo foi usado
model_used = prediction_data.get("model_used", True)
if not model_used:
    span.set_attribute("ml.fallback_mode", True)
    span.set_attribute("ml.warning", "ML-NSMF usando modo fallback")

# Em erros, adicionar flag [FALLBACK] no explanation
explanation=f"[FALLBACK] ML-NSMF não disponível: {str(e)}"
```

**Impacto:** ✅ **MELHORADO** — Logs mais claros sobre modo degradado

---

## 📊 TABELA: FEATURE vs FONTE vs TRATAMENTO

| Feature | Fonte | Tratamento | Default | Status |
|---------|-------|------------|---------|--------|
| `latency` | `sla_requirements["latency"]` | Parse string, remove "ms" | 0.0 | ✅ |
| `throughput` | `sla_requirements["throughput"]` | Parse string, remove "Mbps"/"Gbps" | 0.0 | ✅ |
| `reliability` | `sla_requirements["reliability"]` | Convert to float | 0.99 | ✅ |
| `jitter` | `sla_requirements["jitter"]` | Parse string, remove "ms" | 0.0 | ✅ |
| `packet_loss` | `sla_requirements["packet_loss"]` ou calculado | `1.0 - reliability` se ausente | Calculado | ✅ |
| `slice_type` | `intent.service_type.value` | String direto | "eMBB" | ✅ |
| `slice_type_encoded` | Calculado de `slice_type` | `{URLLC:1, eMBB:2, mMTC:3}` | 2 | ✅ |
| `cpu_utilization` | `nest.resources["cpu"]` | Convert cores → 0-1 (cores/10) | 0.5 | ✅ |
| `memory_utilization` | `nest.resources["memory"]` | Convert GB → 0-1 (GB/100) | 0.5 | ✅ |
| `network_bandwidth_available` | `nest.resources["bandwidth"]` | Parse string, remove "Mbps" | 500.0 | ✅ |
| `active_slices_count` | `context["active_slices_count"]` ou `nest.metadata` | Convert to float | 1.0 | ✅ |
| `latency_throughput_ratio` | **Calculado no predictor** | `latency / (throughput + epsilon)` | N/A | ✅ |
| `reliability_packet_loss_ratio` | **Calculado no predictor** | `reliability / (packet_loss + epsilon)` | N/A | ✅ |
| `jitter_latency_ratio` | **Calculado no predictor** | `jitter / (latency + epsilon)` | N/A | ✅ |

---

## 🔄 FLUXO ATUALIZADO

### Request (Decision Engine → ML-NSMF)

```json
{
    "latency": 5.0,
    "throughput": 100.0,
    "reliability": 0.999,
    "jitter": 1.0,
    "packet_loss": 0.001,
    "slice_type": "URLLC",              // ✅ NOVO: String
    "slice_type_encoded": 1,             // ✅ NOVO: Numérico correto
    "cpu_utilization": 0.5,              // ✅ CORRIGIDO: Nome e tipo
    "memory_utilization": 0.5,           // ✅ CORRIGIDO: Nome e tipo
    "network_bandwidth_available": 500.0, // ✅ CORRIGIDO: Nome
    "active_slices_count": 1.0           // ✅ NOVO: Adicionado
}
```

### Response (ML-NSMF → Decision Engine)

```json
{
    "prediction": {
        "risk_score": 0.3,
        "risk_level": "low",
        "viability_score": 0.7,          // ✅ EXTRAÍDO agora
        "confidence": 0.9,
        "model_used": true,              // ✅ VERIFICADO agora
        "timestamp": "2025-01-27T..."
    },
    "explanation": {
        "method": "SHAP",
        "features_importance": {...},
        "reasoning": "[viability_score=0.7000] ..."  // ✅ MELHORADO
    }
}
```

---

## ✅ VALIDAÇÕES REALIZADAS

### 1. Encoding de Slice Type
- ✅ Alinhado com modelo v3.7.0: `{URLLC:1, eMBB:2, mMTC:3}`
- ✅ Testado com todos os tipos de slice

### 2. Nomes de Campos
- ✅ `slice_type` (string) enviado
- ✅ `slice_type_encoded` (numérico) enviado
- ✅ Predictor aceita ambos

### 3. Features de Recursos
- ✅ Conversão de cores → utilization implementada
- ✅ Conversão de GB → utilization implementada
- ✅ Bandwidth em Mbps mantido
- ✅ Defaults aplicados quando ausente

### 4. Feature `active_slices_count`
- ✅ Adicionada ao payload
- ✅ Busca em múltiplas fontes (context, nest.metadata)
- ✅ Default = 1.0 aplicado

### 5. Viability Score
- ✅ Extraído do response
- ✅ Adicionado ao explanation
- ✅ Logado em OpenTelemetry

### 6. Tratamento de Erros
- ✅ Verifica `model_used = false`
- ✅ Sinaliza modo fallback em logs
- ✅ Adiciona prefixo `[FALLBACK]` em explanations

---

## 📝 ARQUIVOS MODIFICADOS

### `apps/decision-engine/src/ml_client.py`

**Mudanças:**
1. Linha 129-133: Encoding de slice type corrigido
2. Linha 135-160: Features de recursos convertidas para formato esperado
3. Linha 161-167: Feature `active_slices_count` adicionada
4. Linha 52-60: Extração de `viability_score` e verificação de `model_used`
5. Linha 67-85: Tratamento de erros melhorado com flags de fallback

**Linhas modificadas:** ~50 linhas

---

## 🎯 CONCLUSÃO

### Status: ✅ **CONTRATOS ALINHADOS**

**Todas as correções foram aplicadas:**
- ✅ Encoding de slice type corrigido
- ✅ Nomes de campos padronizados
- ✅ Features de recursos convertidas
- ✅ Feature `active_slices_count` adicionada
- ✅ Viability score extraído
- ✅ Tratamento de erros melhorado

**Próximos passos:**
- FASE 4.3: Criar testes de integração para validar correções
- FASE 4.4: Ajustes finos de código e logs adicionais

---

**FIM DA FASE 4.2**

