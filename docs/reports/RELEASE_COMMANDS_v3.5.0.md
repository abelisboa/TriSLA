# Comandos para Publicar Release v3.5.0 — TriSLA

**Data:** 2025-01-27  
**Release:** TriSLA v3.5.0  
**Status:** ⏳ Aguardando Execução

---

## ⚠️ IMPORTANTE: Executar Antes do Commit

### 1. Mover Arquivos Proibidos da Raiz

**⚠️ IMPORTANTE:** Execute no diretório local do repositório (TriSLA-clean)

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Executar script de movimentação (se estiver em ambiente Git Bash/WSL)
# Ou mover manualmente:
Move-Item -Path AUDIT_REPORT_COMPLETE.md -Destination docs\reports\ -ErrorAction SilentlyContinue
Move-Item -Path DEVOPS_AUDIT_REPORT.md -Destination docs\reports\ -ErrorAction SilentlyContinue
Move-Item -Path GITHUB_SAFETY_REPORT.md -Destination docs\reports\ -ErrorAction SilentlyContinue
Move-Item -Path RELEASE_CHECKLIST_v3.5.0.md -Destination docs\reports\ -ErrorAction SilentlyContinue
Move-Item -Path RELEASE_RENAME_REPORT.md -Destination docs\reports\ -ErrorAction SilentlyContinue
Move-Item -Path RELEASE_v3.5.0_SUMMARY.md -Destination docs\reports\ -ErrorAction SilentlyContinue
Move-Item -Path VALIDATION_REPORT_FINAL.md -Destination docs\reports\ -ErrorAction SilentlyContinue
Move-Item -Path ROOT_PROTECTION_REPORT.md -Destination docs\reports\ -ErrorAction SilentlyContinue

# Mover docker-compose.yml para configs/
New-Item -ItemType Directory -Path configs -Force | Out-Null
Move-Item -Path docker-compose.yml -Destination configs\ -ErrorAction SilentlyContinue
```

**Linux/Mac ou Git Bash:**
```bash
cd /caminho/para/TriSLA-clean

# Executar script de movimentação
chmod +x scripts/move-prohibited-files.sh
./scripts/move-prohibited-files.sh

# Ou mover manualmente:
mv AUDIT_REPORT_COMPLETE.md docs/reports/ 2>/dev/null || true
mv DEVOPS_AUDIT_REPORT.md docs/reports/ 2>/dev/null || true
mv GITHUB_SAFETY_REPORT.md docs/reports/ 2>/dev/null || true
mv RELEASE_CHECKLIST_v3.5.0.md docs/reports/ 2>/dev/null || true
mv RELEASE_RENAME_REPORT.md docs/reports/ 2>/dev/null || true
mv RELEASE_v3.5.0_SUMMARY.md docs/reports/ 2>/dev/null || true
mv VALIDATION_REPORT_FINAL.md docs/reports/ 2>/dev/null || true
mv ROOT_PROTECTION_REPORT.md docs/reports/ 2>/dev/null || true

# Mover docker-compose.yml para configs/
mkdir -p configs
mv docker-compose.yml configs/ 2>/dev/null || true
```

### 2. Verificar Estrutura

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Verificar se raiz está limpa (usando Git Bash ou WSL)
# Ou verificar manualmente:
Get-ChildItem -File | Where-Object { $_.Name -notmatch "^(README|LICENSE|CHANGELOG|\.gitignore)" }
```

**Linux/Mac ou Git Bash:**
```bash
cd /caminho/para/TriSLA-clean

# Verificar se raiz está limpa
./scripts/enforce-clean-root.sh
```

**Deve retornar:** ✅ Raiz do repositório está limpa!

---

## 🚀 Comandos Git para Publicar Release

### Passo 1: Verificar Estado

**⚠️ IMPORTANTE:** Execute no diretório local do repositório (TriSLA-clean)

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Ver estado do repositório
git status

# Ver diferenças
git diff
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

# Ver estado do repositório
git status

# Ver diferenças
git diff
```

### Passo 2: Adicionar Mudanças

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Adicionar todos os arquivos
git add .
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

# Adicionar todos os arquivos
git add .
```

### Passo 3: Commit

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

git commit -m "🚀 TriSLA v3.5.0 — Release final alinhada

- Auditoria DevOps completa (scripts + Helm + Ansible)
- Consolidação de values-nasp.yaml como fonte canônica
- Execução local no NASP (127.0.0.1)
- Proteções GitHub (.gitignore, workflow de safety, root protection)
- Documentação premium (README, docs/)
- Estrutura da raiz limpa e protegida
- Versão atualizada para 3.5.0

Ver CHANGELOG.md e docs/reports/FINAL_ALIGNMENT_REPORT_v3.5.0.md para detalhes completos."
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

git commit -m "🚀 TriSLA v3.5.0 — Release final alinhada

- Auditoria DevOps completa (scripts + Helm + Ansible)
- Consolidação de values-nasp.yaml como fonte canônica
- Execução local no NASP (127.0.0.1)
- Proteções GitHub (.gitignore, workflow de safety, root protection)
- Documentação premium (README, docs/)
- Estrutura da raiz limpa e protegida
- Versão atualizada para 3.5.0

Ver CHANGELOG.md e docs/reports/FINAL_ALIGNMENT_REPORT_v3.5.0.md para detalhes completos."
```

### Passo 4: Criar Tag

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

git tag -a v3.5.0 -m "TriSLA v3.5.0 — Release estável NASP local

Esta release consolida todas as melhorias de DevOps e estabelece o repositório como solução pronta para produção.

Principais mudanças:
- Deploy 100% local no NASP (127.0.0.1)
- values-nasp.yaml como arquivo canônico
- Release name padronizado: trisla
- Proteções GitHub implementadas (3 camadas)
- Documentação completa e sincronizada
- Estrutura da raiz limpa e protegida

Ver CHANGELOG.md para changelog completo."
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

git tag -a v3.5.0 -m "TriSLA v3.5.0 — Release estável NASP local

Esta release consolida todas as melhorias de DevOps e estabelece o repositório como solução pronta para produção.

Principais mudanças:
- Deploy 100% local no NASP (127.0.0.1)
- values-nasp.yaml como arquivo canônico
- Release name padronizado: trisla
- Proteções GitHub implementadas (3 camadas)
- Documentação completa e sincronizada
- Estrutura da raiz limpa e protegida

Ver CHANGELOG.md para changelog completo."
```

### Passo 5: Push para GitHub

**Windows (PowerShell):**
```powershell
cd C:\Users\USER\Documents\TriSLA-clean

# Push do commit
git push origin main

# Push da tag
git push origin v3.5.0
```

**Linux/Mac:**
```bash
cd /caminho/para/TriSLA-clean

# Push do commit
git push origin main

# Push da tag
git push origin v3.5.0
```

---

## ✅ Verificação Pós-Push

### 1. Verificar Tag

```bash
git tag -l "v3.5.0"
```

**Deve mostrar:** `v3.5.0`

### 2. Verificar Push Remoto

```bash
git ls-remote --tags origin | grep v3.5.0
```

**Deve mostrar:** `refs/tags/v3.5.0`

### 3. Verificar GitHub Actions

- Acessar: https://github.com/abelisboa/TriSLA/actions
- Verificar que o workflow `root-protection` passou
- Verificar que não há erros

---

## 📝 Criar Release no GitHub

Após o push, criar a release no GitHub:

1. Acessar: https://github.com/abelisboa/TriSLA/releases/new
2. Selecionar tag: `v3.5.0`
3. Título: `TriSLA v3.5.0 — Release Estável NASP Local`
4. Descrição: Copiar do `CHANGELOG.md` (seção [3.5.0])

---

## 🎯 Resumo dos Comandos

```bash
# 1. Mover arquivos proibidos
cd ~/gtp5g/trisla
./scripts/move-prohibited-files.sh

# 2. Verificar estrutura
./scripts/enforce-clean-root.sh

# 3. Adicionar mudanças
git add .

# 4. Commit
git commit -m "🚀 TriSLA v3.5.0 — Release final alinhada"

# 5. Criar tag
git tag -a v3.5.0 -m "TriSLA v3.5.0 — Release estável NASP local"

# 6. Push
git push origin main
git push origin v3.5.0
```

---

**Status:** ⏳ Aguardando execução manual pelo operador

