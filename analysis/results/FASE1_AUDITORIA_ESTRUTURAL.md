# FASE 1 — AUDITORIA ESTRUTURAL DO PROJETO ML-NSMF v3.7.0

**Data:** 2025-01-27  
**Status:** CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

A auditoria identificou **PROBLEMAS CRÍTICOS** de duplicidade de diretórios, inconsistências de nomenclatura e divergências de código que podem causar falhas no pipeline de ML-NSMF.

---

## 🔴 PROBLEMAS CRÍTICOS ENCONTRADOS

### 1. DUPLICIDADE DE DIRETÓRIOS

**Situação:**
- ✅ `apps/ml-nsmf/` — Diretório **OFICIAL** e completo
  - Contém: models/, training/, data/, src/, Dockerfile, requirements.txt
  - Modelos presentes: `viability_model.pkl`, `scaler.pkl`, `model_metadata.json`
  
- ❌ `apps/ml_nsmf/` — Diretório **DUPLICADO** e incompleto
  - Contém apenas: `src/predictor.py` (versão diferente)
  - **NÃO contém models/** — modelos não estão aqui
  - Arquivo estranho: `ml-nsmf` (sem extensão)

**Impacto:** Confusão sobre qual diretório usar, imports quebrados.

---

### 2. INCONSISTÊNCIA DE IMPORTS

**Arquivo:** `analysis/scripts/test_predictor_v3_7_0.py`

```python
from apps.ml_nsmf.src.predictor import RiskPredictor  # ❌ Importa de ml_nsmf (underscore)
```

**Mas:**
- Modelos estão em `apps/ml-nsmf/models/` (hífen)
- O predictor em `ml_nsmf` tenta resolver isso com workaround, mas é frágil

**Impacto:** Testes podem falhar se o workaround não funcionar.

---

### 3. DIVERGÊNCIAS DE CÓDIGO ENTRE PREDICTORS

#### 3.1 Encoding de slice_type

**`apps/ml-nsmf/src/predictor.py` (OFICIAL):**
```python
slice_type_encoded = {"URLLC": 1, "eMBB": 2, "mMTC": 3}.get(slice_type, 2)
```

**`apps/ml_nsmf/src/predictor.py` (DUPLICADO):**
```python
slice_type_encoded = {"URLLC": 0, "eMBB": 1, "mMTC": 2}.get(metrics.get("slice_type"), 1)
```

**❌ INCONSISTÊNCIA:** Encoding diferente! O modelo foi treinado com `{URLLC:1, eMBB:2, mMTC:3}`.

#### 3.2 Valor de epsilon

**`apps/ml-nsmf/src/predictor.py` (OFICIAL):**
```python
epsilon = 0.001
```

**`apps/ml_nsmf/src/predictor.py` (DUPLICADO):**
```python
eps = 1e-9  # ❌ Diferente!
```

**❌ INCONSISTÊNCIA:** Epsilon diferente afeta cálculo de features derivadas.

#### 3.3 Função resolve_model_path()

**`apps/ml_nsmf/src/predictor.py` (DUPLICADO):**
- Tem função `resolve_model_path()` para resolver duplicidade
- É um workaround, não uma solução definitiva

**`apps/ml-nsmf/src/predictor.py` (OFICIAL):**
- Não tem essa função
- Usa caminhos relativos simples

---

### 4. ESTRUTURA DE ARQUIVOS

#### ✅ Arquivos Presentes e Corretos:

```
apps/ml-nsmf/
├── models/
│   ├── viability_model.pkl          ✅
│   ├── scaler.pkl                    ✅
│   └── model_metadata.json           ✅
├── src/
│   └── predictor.py                  ✅ (versão oficial)
├── training/
│   └── train_model.py                ✅
└── data/
    └── datasets/
        └── trisla_ml_dataset.csv      ✅
```

#### ❌ Arquivos Duplicados/Inconsistentes:

```
apps/ml_nsmf/
├── src/
│   └── predictor.py                  ❌ (versão diferente, com bugs)
└── ml-nsmf                           ❓ (arquivo sem extensão, estranho)
```

#### ✅ Scripts de Teste:

```
analysis/scripts/
├── test_predictor_v3_7_0.py           ✅ (mas importa de ml_nsmf)
├── test_ml_nsmf_model_v3_7_0.py      ✅
└── validate_model_integrity.py       ✅
```

#### ✅ Notebooks:

```
analysis/notebooks/
└── FASE_M_Retreino_v3.7.0.ipynb      ✅
```

---

### 5. VALIDAÇÃO DE IMPORTS PYTHON

**Problema:** Python não pode importar módulos com hífen diretamente:

```python
# ❌ ISSO NÃO FUNCIONA:
from apps.ml-nsmf.src.predictor import RiskPredictor  # SyntaxError

# ✅ ISSO FUNCIONA:
from apps.ml_nsmf.src.predictor import RiskPredictor  # OK
```

**Solução necessária:**
- Padronizar para `ml_nsmf` (underscore) OU
- Usar imports absolutos com sys.path

---

## 📊 MAPA DE DEPENDÊNCIAS

```
test_predictor_v3_7_0.py
    ↓ importa
apps.ml_nsmf.src.predictor (underscore)
    ↓ tenta carregar
apps/ml-nsmf/models/ (hífen)  ← WORKAROUND resolve_model_path()
```

**Problema:** Cadeia frágil e dependente de workaround.

---

## 🎯 CORREÇÕES NECESSÁRIAS

### Prioridade ALTA:

1. **Eliminar duplicidade:**
   - Remover `apps/ml_nsmf/` completamente OU
   - Mover tudo para `apps/ml_nsmf/` e remover `apps/ml-nsmf/`

2. **Padronizar nomenclatura:**
   - Escolher: `ml-nsmf` OU `ml_nsmf`
   - Atualizar todos os imports

3. **Corrigir encoding:**
   - Garantir que slice_type_encoded = {URLLC:1, eMBB:2, mMTC:3}

4. **Corrigir epsilon:**
   - Padronizar epsilon = 0.001

5. **Atualizar test_predictor_v3_7_0.py:**
   - Corrigir import para usar diretório correto

---

## 📝 RECOMENDAÇÃO

**Padronizar para `apps/ml_nsmf/` (underscore)** porque:
- Python não suporta imports com hífen
- Já existe estrutura em `ml_nsmf`
- Testes já importam de `ml_nsmf`

**Ações:**
1. Mover `apps/ml-nsmf/models/` → `apps/ml_nsmf/models/`
2. Mover `apps/ml-nsmf/src/` → `apps/ml_nsmf/src/` (substituir)
3. Mover `apps/ml-nsmf/training/` → `apps/ml_nsmf/training/`
4. Mover `apps/ml-nsmf/data/` → `apps/ml_nsmf/data/`
5. Remover `apps/ml-nsmf/` completamente
6. Atualizar predictor.py para remover workaround
7. Corrigir encoding e epsilon no predictor

---

## ✅ VALIDAÇÕES REALIZADAS

- [x] Estrutura de diretórios verificada
- [x] Arquivos do modelo localizados
- [x] Duplicidades identificadas
- [x] Imports analisados
- [x] Divergências de código detectadas
- [x] Inconsistências de encoding identificadas
- [x] Inconsistências de epsilon identificadas

---

**FIM DA FASE 1**

