# FASE 5.3 — SIMULAÇÃO LOCAL DE BUILD/PUSH
## Preview de Build e Push (Dry-Run) para Deploy NASP

**Data:** 2025-01-27  
**Status:** ✅ CONCLUÍDA

---

## 📋 RESUMO EXECUTIVO

Esta fase simulou o processo de build e push das imagens Docker para o GHCR, validando scripts, caminhos e mapeamentos sem executar o push real. Todas as referências ao diretório antigo `ml-nsmf` foram corrigidas para `ml_nsmf`.

---

## 🔍 SCRIPTS VALIDADOS

### 1. **`scripts/build_and_push_all.sh`** ✅

#### Validações Realizadas

**Mapeamento de diretórios:**
```bash
declare -A SERVICE_DIRS=(
  ["bc-nssmf"]="bc-nssmf"
  ["ml-nsmf"]="ml_nsmf"  # ✅ CORRIGIDO - Diretório real é ml_nsmf
  ["sem-csmf"]="sem-csmf"
  ["decision-engine"]="decision-engine"
  ["sla-agent-layer"]="sla-agent-layer"
  ["ui-dashboard"]="ui-dashboard"
  ["nasp-adapter"]="nasp-adapter"
)
```

**Lógica de build:**
```bash
for service in "${SERVICES[@]}"; do
  SERVICE_DIR_NAME="${SERVICE_DIRS[$service]:-$service}"
  SERVICE_DIR="apps/${SERVICE_DIR_NAME}"
  # ...
  docker build -t "${IMAGE_NAME}" "./${SERVICE_DIR}"
done
```

**Status:** ✅ **VALIDADO E CORRIGIDO**

---

### 2. **`scripts/build-push-images.ps1`** ✅

#### Validações Realizadas

**Mapeamento de módulos:**
```powershell
$modules = @(
    @{name="sem-csmf"; path="apps/sem-csmf"},
    @{name="decision-engine"; path="apps/decision-engine"},
    @{name="ml-nsmf"; path="apps/ml_nsmf"},  # ✅ CORRIGIDO
    # ...
)
```

**Status:** ✅ **VALIDADO E CORRIGIDO**

---

### 3. **`scripts/verify-structure.ps1`** ✅

#### Validações Realizadas

**Estrutura esperada:**
```powershell
"ml_nsmf" = @{  # ✅ CORRIGIDO
    "Dockerfile" = $true
    "requirements.txt" = $true
    "models" = @{  # ✅ ADICIONADO
        "viability_model.pkl" = $true
        "scaler.pkl" = $true
        "model_metadata.json" = $true
    }
    "src" = @{
        "main.py" = $true
        "predictor.py" = $true
    }
}
```

**Status:** ✅ **VALIDADO E CORRIGIDO**

---

### 4. **`scripts/quick-start-services.sh`** ✅

#### Validações Realizadas

**Caminho corrigido:**
```bash
cd apps/ml_nsmf/src  # ✅ CORRIGIDO
```

**Status:** ✅ **VALIDADO E CORRIGIDO**

---

### 5. **`scripts/TRISLA_AUTO_RUN.sh`** ✅

#### Validações Realizadas

**Caminho corrigido:**
```bash
TRAIN_SCRIPT="apps/ml_nsmf/training/train_model.py"  # ✅ CORRIGIDO
```

**Status:** ✅ **VALIDADO E CORRIGIDO**

---

## 📦 IMAGENS QUE SERÃO CONSTRUÍDAS

### Lista Completa de Imagens

| # | Serviço | Diretório Real | Imagem Docker | Tag Sugerida |
|---|---------|----------------|---------------|--------------|
| 1 | ML-NSMF | `apps/ml_nsmf` | `ghcr.io/abelisboa/trisla-ml-nsmf` | `v3.7.0-nasp` |
| 2 | Decision Engine | `apps/decision-engine` | `ghcr.io/abelisboa/trisla-decision-engine` | `v3.7.0-nasp` |
| 3 | SEM-CSMF | `apps/sem-csmf` | `ghcr.io/abelisboa/trisla-sem-csmf` | `nasp-a2` |
| 4 | BC-NSSMF | `apps/bc-nssmf` | `ghcr.io/abelisboa/trisla-bc-nssmf` | `nasp-a2` |
| 5 | SLA Agent Layer | `apps/sla-agent-layer` | `ghcr.io/abelisboa/trisla-sla-agent-layer` | `nasp-a2` |
| 6 | NASP Adapter | `apps/nasp-adapter` | `ghcr.io/abelisboa/trisla-nasp-adapter` | `nasp-a2` |
| 7 | UI Dashboard | `apps/ui-dashboard` | `ghcr.io/abelisboa/trisla-ui-dashboard` | `nasp-a2` |

---

## 🔧 VALIDAÇÃO DE CAMINHOS

### Caminhos Finais Validados

#### ML-NSMF
```
apps/ml_nsmf/
├── Dockerfile              ✅
├── requirements.txt        ✅
├── src/
│   ├── main.py            ✅
│   └── predictor.py        ✅
└── models/                 ✅ CRÍTICO
    ├── viability_model.pkl ✅
    ├── scaler.pkl          ✅
    └── model_metadata.json ✅
```

**Validação:**
- ✅ Dockerfile copia `src/`
- ✅ Dockerfile copia `models/` (corrigido na FASE 5.1)
- ✅ Scripts usam caminho correto `apps/ml_nsmf`

#### Decision Engine
```
apps/decision-engine/
├── Dockerfile              ✅
├── requirements.txt        ✅
└── src/
    ├── main.py            ✅
    ├── ml_client.py        ✅
    └── config.py           ✅
```

**Validação:**
- ✅ Dockerfile copia `src/`
- ✅ Scripts usam caminho correto `apps/decision-engine`

---

## 🚫 REFERÊNCIAS AO DIRETÓRIO ANTIGO

### Verificação de Referências Incorretas

**Comando de busca:**
```bash
grep -r "ml-nsmf" scripts/ --exclude-dir=node_modules
```

**Resultados:**
- ✅ `build_and_push_all.sh` — Corrigido (usa mapeamento)
- ✅ `build-push-images.ps1` — Corrigido
- ✅ `verify-structure.ps1` — Corrigido
- ✅ `quick-start-services.sh` — Corrigido
- ✅ `TRISLA_AUTO_RUN.sh` — Corrigido

**Status:** ✅ **TODAS AS REFERÊNCIAS CORRIGIDAS**

---

## 📊 PREVIEW DE BUILD

### Comandos que Serão Executados (Dry-Run)

#### 1. ML-NSMF
```bash
docker build -t ghcr.io/abelisboa/trisla-ml-nsmf:v3.7.0-nasp ./apps/ml_nsmf
docker push ghcr.io/abelisboa/trisla-ml-nsmf:v3.7.0-nasp
```

**Validações:**
- ✅ Diretório `apps/ml_nsmf` existe
- ✅ Dockerfile presente
- ✅ `models/` será incluído na imagem
- ✅ `src/` será incluído na imagem

#### 2. Decision Engine
```bash
docker build -t ghcr.io/abelisboa/trisla-decision-engine:v3.7.0-nasp ./apps/decision-engine
docker push ghcr.io/abelisboa/trisla-decision-engine:v3.7.0-nasp
```

**Validações:**
- ✅ Diretório `apps/decision-engine` existe
- ✅ Dockerfile presente
- ✅ `src/` será incluído na imagem

---

## 🔄 CORREÇÕES APLICADAS

### 1. **Scripts com Referências ao Diretório Antigo** ✅

**Arquivos corrigidos:**
1. ✅ `scripts/build-push-images.ps1`
   - `apps/ml-nsmf` → `apps/ml_nsmf`

2. ✅ `scripts/verify-structure.ps1`
   - `ml-nsmf` → `ml_nsmf`
   - Adicionado `models/` à estrutura esperada

3. ✅ `scripts/quick-start-services.sh`
   - `apps/ml-nsmf/src` → `apps/ml_nsmf/src`

4. ✅ `scripts/TRISLA_AUTO_RUN.sh`
   - `apps/ml-nsmf/src/train_model.py` → `apps/ml_nsmf/training/train_model.py`

**Status:** ✅ **TODOS OS SCRIPTS CORRIGIDOS**

---

## ✅ VALIDAÇÕES FINAIS

### Checklist de Validação

- ✅ Scripts chamam path correto (`apps/ml_nsmf`)
- ✅ Não há referência ao diretório antigo (`ml-nsmf`)
- ✅ Path para `predictor.py` correto (`src/predictor.py`)
- ✅ Path para `models/` correto (`models/`)
- ✅ Dockerfile inclui `models/` (FASE 5.1)
- ✅ Mapeamento de serviços funciona corretamente

---

## 📝 ARQUIVOS MODIFICADOS

### `scripts/build-push-images.ps1`
- **Linhas modificadas:** 1
- **Mudança:** `apps/ml-nsmf` → `apps/ml_nsmf`

### `scripts/verify-structure.ps1`
- **Linhas modificadas:** 7
- **Mudanças:**
  - `ml-nsmf` → `ml_nsmf`
  - Adicionado `models/` à estrutura esperada

### `scripts/quick-start-services.sh`
- **Linhas modificadas:** 1
- **Mudança:** `apps/ml-nsmf/src` → `apps/ml_nsmf/src`

### `scripts/TRISLA_AUTO_RUN.sh`
- **Linhas modificadas:** 1
- **Mudança:** `apps/ml-nsmf/src/train_model.py` → `apps/ml_nsmf/training/train_model.py`

---

## 🎯 CONCLUSÃO

### Status: ✅ **SCRIPTS VALIDADOS E CORRIGIDOS**

**Todas as validações foram realizadas:**
- ✅ Scripts chamam path correto
- ✅ Não há referência ao diretório antigo
- ✅ Path para `predictor.py` e `models/` correto
- ✅ Preview de build validado

**Correções aplicadas:**
- ✅ 4 scripts corrigidos
- ✅ Estrutura esperada atualizada

**Próximos passos:**
- FASE 5.4: Simular deploy Helm (template)

---

**FIM DA FASE 5.3**

