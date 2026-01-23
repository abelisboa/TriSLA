# Comandos para Push Seguro — TriSLA v3.5.0

**Data:** 2025-01-27  
**Status:** ✅ TriSLA_PROMPTS removida do índice Git

---

## ✅ Verificações Realizadas

1. ✅ **TriSLA_PROMPTS removida do índice Git**
   - Todos os arquivos da pasta foram removidos do rastreamento
   - Pasta ainda existe localmente (não será enviada ao GitHub)
   - Está no `.gitignore` (não será rastreada no futuro)

2. ✅ **.gitignore validado**
   - `TriSLA_PROMPTS/` está no `.gitignore`
   - Outros diretórios privados também protegidos

---

## 🚀 Comandos para Push

### Passo 1: Verificar Status

**⚠️ IMPORTANTE:** Execute no diretório local do repositório (TriSLA-clean)

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Ver status completo
git status

# Verificar que TriSLA_PROMPTS não está mais sendo rastreado
git ls-files | Select-String -Pattern "TriSLA_PROMPTS"
# Deve retornar vazio (nenhum resultado)
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

# Ver status completo
git status

# Verificar que TriSLA_PROMPTS não está mais sendo rastreado
git ls-files | grep TriSLA_PROMPTS
# Deve retornar vazio (nenhum resultado)
```

### Passo 2: Adicionar Todas as Mudanças (exceto TriSLA_PROMPTS)

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Adicionar todas as mudanças
git add .

# Verificar que TriSLA_PROMPTS não foi adicionada
git status | Select-String -Pattern "TriSLA_PROMPTS"
# Não deve aparecer nada (ou apenas "D" para deleted, que é correto)
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

# Adicionar todas as mudanças
git add .

# Verificar que TriSLA_PROMPTS não foi adicionada
git status | grep TriSLA_PROMPTS
# Não deve aparecer nada (ou apenas "D" para deleted, que é correto)
```

### Passo 3: Commit

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

git commit -m "🔒 TriSLA v3.5.0 — Remove TriSLA_PROMPTS do repositório público

- Remove pasta privada TriSLA_PROMPTS do índice Git
- Pasta permanece localmente mas não será enviada ao GitHub
- Proteções .gitignore validadas
- Release v3.5.0 alinhada e pronta para produção

A pasta TriSLA_PROMPTS contém prompts privados e não deve ser pública."
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

git commit -m "🔒 TriSLA v3.5.0 — Remove TriSLA_PROMPTS do repositório público

- Remove pasta privada TriSLA_PROMPTS do índice Git
- Pasta permanece localmente mas não será enviada ao GitHub
- Proteções .gitignore validadas
- Release v3.5.0 alinhada e pronta para produção

A pasta TriSLA_PROMPTS contém prompts privados e não deve ser pública."
```

### Passo 4: Push para GitHub

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Push do commit
git push origin main

# Se houver tag v3.5.0, push da tag também
git push origin v3.5.0 2>$null; if ($LASTEXITCODE -ne 0) { Write-Host "Tag não existe ou já foi enviada" }
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

# Push do commit
git push origin main

# Se houver tag v3.5.0, push da tag também
git push origin v3.5.0 2>/dev/null || echo "Tag não existe ou já foi enviada"
```

---

## ✅ Verificação Pós-Push

### 1. Verificar no GitHub

1. Acessar: https://github.com/abelisboa/TriSLA
2. Verificar que a pasta `TriSLA_PROMPTS` **NÃO** aparece no repositório
3. Verificar que os arquivos removidos não estão mais visíveis

### 2. Verificar Localmente

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Verificar que TriSLA_PROMPTS ainda existe localmente
Test-Path TriSLA_PROMPTS
# Deve retornar True (a pasta ainda existe localmente)

# Verificar que não está sendo rastreado
git ls-files | Select-String -Pattern "TriSLA_PROMPTS"
# Deve retornar vazio
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

# Verificar que TriSLA_PROMPTS ainda existe localmente
ls -la TriSLA_PROMPTS
# Deve mostrar a pasta (ela ainda existe localmente)

# Verificar que não está sendo rastreado
git ls-files | grep TriSLA_PROMPTS
# Deve retornar vazio
```

---

## 🔒 Proteções Implementadas

### 1. .gitignore

A pasta `TriSLA_PROMPTS/` está no `.gitignore`:
```
TriSLA_PROMPTS/
```

### 2. Remoção do Índice Git

Todos os arquivos de `TriSLA_PROMPTS/` foram removidos do índice Git usando:
```bash
git rm -r --cached TriSLA_PROMPTS/
```

### 3. Script de Limpeza

Criado script `scripts/clean-git-before-push.sh` para limpeza automática antes de pushes futuros.

---

## 📋 Resumo

- ✅ **TriSLA_PROMPTS removida do índice Git**
- ✅ **Pasta permanece localmente** (não será deletada)
- ✅ **Não será enviada ao GitHub** (está no .gitignore)
- ✅ **Proteções validadas**

**Status:** ✅ **PRONTO PARA PUSH SEGURO**

---

**Data:** 2025-01-27  
**Ação:** Remoção de TriSLA_PROMPTS do repositório público

