# AUDITORIA TÉCNICA — ML-NSMF (FASE 1) - RESUMO EXECUTIVO

**Data:** 2025-01-27  
**Ambiente:** node006  
**Commit:** fb4e5df179be2408bf95531bfeb7b18a60e8126a

---

## 🎯 RESULTADO PRINCIPAL

### ✅ PONTO ÚNICO DE DECISÃO IDENTIFICADO

**Arquivo:** `apps/decision-engine/src/engine.py`  
**Função:** `_apply_decision_rules()` (linhas 143-239)  
**Método chamador:** `DecisionEngine.decide()` (linha 113)

---

## 📋 ENTRADAS DA DECISÃO

1. **`intent`** (SLAIntent) - Do SEM-CSMF
   - `service_type` (URLLC/eMBB/mMTC)
   - `sla_requirements` (latency, throughput, reliability, etc.)

2. **`nest`** (NestSubset) - Do SEM-CSMF (opcional)
   - `resources` (CPU, memory, bandwidth)

3. **`ml_prediction`** (MLPrediction) - Do ML-NSMF
   - `risk_score` (0-1)
   - `risk_level` (LOW/MEDIUM/HIGH)
   - `confidence` (0-1)

4. **`context`** (dict) - Contexto adicional (opcional)

---

## 📋 SAÍDAS DA DECISÃO

Tupla `(action, reasoning, slos, domains)`:
- **`action`** - `DecisionAction` (ACCEPT/RENEGOTIATE/REJECT)
- **`reasoning`** - String com justificativa
- **`slos`** - Lista de `SLARequirement`
- **`domains`** - Lista de strings (RAN/Transporte/Core)

---

## 📋 CRITÉRIOS DE DECISÃO (5 REGRAS)

1. **REGRA 1:** `risk_level == HIGH` OU `risk_score > 0.7` → **REJECT**
2. **REGRA 2:** `URLLC` + `latency <= 10ms` + `risk_level == LOW` → **ACCEPT**
3. **REGRA 3:** `risk_level == MEDIUM` OU `0.4 <= risk_score <= 0.7` → **RENEGOTIATE**
4. **REGRA 4:** `risk_level == LOW` + `risk_score < 0.4` → **ACCEPT**
5. **REGRA PADRÃO:** → **ACCEPT** (com aviso)

---

## ✅ CONFIRMAÇÕES

1. ✅ **Modelo ML não decide sozinho** - Apenas retorna `risk_score`/`risk_level`
2. ✅ **Decisão é baseada em estado atual** - Não usa histórico
3. ✅ **Correção pode ser local e mínima** - Apenas `_apply_decision_rules()`

---

## ⚠️ GAP IDENTIFICADO

**A decisão NÃO avalia risco futuro explícito:**
- Usa apenas `risk_score` atual
- Não projeta cenários futuros
- Não considera degradação de recursos ao longo do tempo

**Este gap será corrigido na Fase 2.**

---

## 🛑 ARQUIVOS BLOQUEADOS (NÃO ALTERÁVEIS)

- `apps/sem-csmf/**/*`
- `apps/ontology/**/*`
- `apps/pnl/**/*`
- `apps/bc-nssmf/**/*`
- `apps/nasp-adapter/**/*`
- `trisla-portal/**/*`
- `apps/ml-nsmf/models/**/*`
- `apps/ml-nsmf/data/**/*`
- `apps/ml-nsmf/training/**/*`
- `apps/ml-nsmf/src/predictor.py`
- `apps/ml-nsmf/src/main.py`

**ÚNICO ARQUIVO PERMITIDO PARA ALTERAÇÃO:**
- `apps/decision-engine/src/engine.py` - Método `_apply_decision_rules()`

---

## 📊 MAPA DE DEPENDÊNCIAS

```
Decision Engine._apply_decision_rules()
    │
    ├── SEM-CSMF [BLOQUEADO] → intent + nest
    ├── ML-NSMF [BLOQUEADO] → ml_prediction
    └── BC-NSSMF [BLOQUEADO] ← DecisionResult (se ACCEPT)
```

---

**Relatório completo:** `docs/technical/AUDITORIA_ML_NSMF_FASE1.md`

