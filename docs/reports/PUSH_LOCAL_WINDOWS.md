# Comandos para Push Local (Windows) — TriSLA v3.5.0

**Data:** 2025-01-27  
**Ambiente:** Windows Local (TriSLA-clean)  
**Status:** ✅ TriSLA_PROMPTS removida do índice Git

---

## ⚠️ IMPORTANTE

- **Pasta local:** `C:\Users\USER\Documents\TriSLA-clean`
- **Pasta no node1 (NASP):** `~/gtp5g/trisla` (apenas durante deploy)
- **Este guia é para o ambiente local Windows**

---

## 🚀 Comandos para Push (PowerShell)

### Passo 1: Navegar para o Diretório

```powershell
cd C:\Users\USER\Documents\TriSLA-clean
```

### Passo 2: Verificar Status

```powershell
# Ver status completo
git status

# Verificar que TriSLA_PROMPTS não está mais sendo rastreado
git ls-files | Select-String -Pattern "TriSLA_PROMPTS"
# Deve retornar vazio (nenhum resultado) ✅
```

### Passo 3: Adicionar Mudanças

```powershell
# Adicionar todas as mudanças (incluindo remoção de TriSLA_PROMPTS)
git add .

# Verificar que TriSLA_PROMPTS não foi adicionada
git status | Select-String -Pattern "TriSLA_PROMPTS"
# Deve mostrar apenas "D" (deleted) ou nada ✅
```

### Passo 4: Commit

```powershell
git commit -m "🔒 TriSLA v3.5.0 — Remove TriSLA_PROMPTS do repositório público

- Remove pasta privada TriSLA_PROMPTS do índice Git
- Pasta permanece localmente mas não será enviada ao GitHub
- Proteções .gitignore validadas
- Release v3.5.0 alinhada e pronta para produção

A pasta TriSLA_PROMPTS contém prompts privados e não deve ser pública."
```

### Passo 5: Push para GitHub

```powershell
# Push do commit
git push origin main

# Se houver tag v3.5.0, push da tag também
git push origin v3.5.0
```

---

## ✅ Verificação Pós-Push

### 1. Verificar no GitHub

1. Acessar: https://github.com/abelisboa/TriSLA
2. Verificar que a pasta `TriSLA_PROMPTS` **NÃO** aparece no repositório
3. Verificar que os arquivos removidos não estão mais visíveis

### 2. Verificar Localmente

```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Verificar que TriSLA_PROMPTS ainda existe localmente
Test-Path TriSLA_PROMPTS
# Deve retornar True (a pasta ainda existe localmente) ✅

# Verificar que não está sendo rastreado
git ls-files | Select-String -Pattern "TriSLA_PROMPTS"
# Deve retornar vazio ✅
```

---

## 📋 Resumo dos Comandos (Copiar e Colar)

```powershell
# 1. Navegar
cd C:\Users\USER\Documents\TriSLA-clean

# 2. Verificar
git status
git ls-files | Select-String -Pattern "TriSLA_PROMPTS"

# 3. Adicionar
git add .

# 4. Commit
git commit -m "🔒 TriSLA v3.5.0 — Remove TriSLA_PROMPTS do repositório público"

# 5. Push
git push origin main
git push origin v3.5.0
```

---

## 🔒 Proteções Implementadas

- ✅ **TriSLA_PROMPTS removida do índice Git**
- ✅ **Pasta permanece localmente** (não será deletada)
- ✅ **Não será enviada ao GitHub** (está no .gitignore)
- ✅ **Proteções validadas**

**Status:** ✅ **PRONTO PARA PUSH SEGURO**

---

**Data:** 2025-01-27  
**Ambiente:** Windows Local

