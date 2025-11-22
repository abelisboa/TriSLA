# 04 – LIMPEZA E PREPARAÇÃO DO GITHUB

Guia para limpar o repositório GitHub e configurar o que deve ser publicado.

# LIMPEZA DO REPOSITÓRIO GITHUB E CONFIGURAÇÃO INICIAL

Este documento explica como limpar completamente o repositório GitHub e configurar o `.gitignore` para publicar apenas arquivos públicos.

---

## 🗑️ PASSO 1: LIMPAR REPOSITÓRIO GITHUB

### **Opção A: Via Interface Web do GitHub (Recomendado)**

1. **Acesse o repositório**: https://github.com/abelisboa/TriSLA
2. **Vá em Settings** (Configurações)
3. **Role até o final da página**
4. **Na seção "Danger Zone"**, clique em **"Delete this repository"**
5. **Digite o nome do repositório** para confirmar
6. **Clique em "I understand the consequences, delete this repository"**

### **Opção B: Limpar via Git (Mantém repositório, apaga histórico)**

⚠️ **ATENÇÃO**: Esta opção mantém o repositório mas apaga todo o histórico. Use apenas se quiser manter o repositório vazio.

```bash
# 1. Clonar o repositório (se ainda não tiver)
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA

# 2. Criar um novo branch órfão (sem histórico)
git checkout --orphan novo-inicio

# 3. Remover todos os arquivos do staging
git rm -rf .

# 4. Adicionar apenas o .gitignore e README
# (você criará esses arquivos depois)

# 5. Fazer commit inicial
git add .gitignore README.md
git commit -m "chore: reinício do repositório - estrutura limpa"

# 6. Deletar a branch main
git branch -D main

# 7. Renomear branch atual para main
git branch -m main

# 8. Forçar push (substitui tudo no GitHub)
git push -f origin main
```

---

## 📝 PASSO 2: CRIAR REPOSITÓRIO NOVO (Se optou por deletar)

1. **Acesse**: https://github.com/new
2. **Nome do repositório**: `TriSLA`
3. **Descrição**: `TriSLA: Uma Arquitetura SLA-Aware Baseada em IA, Ontologia e Contratos Inteligentes para Garantia de SLA em Redes 5G/O-RAN`
4. **Visibilidade**: **Public** (público)
5. **NÃO marque** "Add a README file", "Add .gitignore", ou "Choose a license" (vamos criar manualmente)
6. **Clique em "Create repository"**

---

## 🚫 PASSO 3: CRIAR .gitignore COMPLETO

Crie um arquivo `.gitignore` na raiz do repositório com o seguinte conteúdo:

```gitignore
# ============================================
# TriSLA - .gitignore
# ============================================
# Este arquivo garante que apenas código público seja publicado
# ============================================

# ============================================
# PROMPTS E DOCUMENTAÇÃO INTERNA
# ============================================
# NUNCA publicar a pasta de prompts
TriSLA_PROMPTS/
**/TriSLA_PROMPTS/
*.prompt
*.prompts

# ============================================
# SECRETS E DADOS SENSÍVEIS
# ============================================
# Secrets do Kubernetes
**/secrets/
**/*secret*.yaml
**/*secret*.yml
**/*secret*.json
secrets/
*.key
*.pem
*.crt
*.p12
*.pfx

# Variáveis de ambiente com secrets
.env
.env.local
.env.*.local
*.env
!*.env.example

# Credenciais
credentials/
**/credentials/
*.credentials
**/*credentials*.json
**/*credentials*.yaml

# Chaves SSH privadas
id_rsa
id_rsa.pub
*.pem
*.key
!*.pub.example

# ============================================
# CONFIGURAÇÕES ESPECÍFICAS DO NASP
# ============================================
# Configurações com IPs, senhas, tokens reais
**/nasp-secrets/
**/nasp-configs-local/
inventory.ini.local
inventory.local.ini
**/*nasp*.local.*
**/*nasp*.private.*

# Valores reais do ambiente NASP (manter apenas templates)
values.yaml.local
values.local.yaml
**/values-*.local.yaml
!values.yaml.example
!values-template.yaml

# ============================================
# LOGS E ARQUIVOS TEMPORÁRIOS
# ============================================
logs/
*.log
*.log.*
*.tmp
*.temp
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# ============================================
# BUILD E CACHE
# ============================================
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache

# Docker
.dockerignore
*.dockerignore.local

# ============================================
# IDEs E EDITORES
# ============================================
.idea/
.vscode/
*.sublime-project
*.sublime-workspace
.project
.classpath
.settings/

# ============================================
# KUBERNETES E HELM
# ============================================
# Manifests gerados localmente
*.generated.yaml
*.generated.yml
rendered-manifests/

# Helm
.helm/
helm-charts/*.tgz
!helm-charts/*.tgz.example

# ============================================
# ANSIBLE
# ============================================
# Inventories locais
inventory.local
inventory.*.local
**/inventory-*.local.ini
!inventory.example.ini

# Vault files (secrets criptografados)
*.vault
**/*.vault.yml
**/*.vault.yaml

# ============================================
# BACKUPS E ARQUIVOS DE TESTE
# ============================================
*.bak
*.backup
*.old
test-data/
test-output/
*.test.local.*

# ============================================
# DOCUMENTAÇÃO INTERNA/PRIVADA
# ============================================
docs/internal/
docs/private/
**/internal-*.md
**/private-*.md
notes/
*.notes.md

# ============================================
# PACKAGES E DEPENDÊNCIAS LOCAIS
# ============================================
# Packages locais não devem ser commitados
*.local
*.local.*

# ============================================
# ARQUIVOS DE CONFIGURAÇÃO COM DADOS REAIS
# ============================================
# Manter apenas templates/exemplos
**/*-real.yaml
**/*-real.yml
**/*-production.yaml
**/*-production.yml
!*-example.yaml
!*-template.yaml
!*-example.yml
!*-template.yml

# ============================================
# O QUE DEVE SER PUBLICADO (NÃO IGNORAR)
# ============================================
# Estes arquivos devem estar no repositório:

# Código-fonte dos módulos
!apps/
!apps/**/*.py
!apps/**/*.js
!apps/**/*.ts

# Configurações de exemplo/template
!configs/
!configs/*.example.*
!configs/*.template.*

# Playbooks Ansible (sem secrets)
!ansible/
!ansible/*.yml
!ansible/*.yaml
!ansible/inventory.example.ini

# Helm charts
!helm/
!helm/**/*.yaml
!helm/**/*.yml

# Scripts públicos
!scripts/
!scripts/*.sh
!scripts/*.py

# Documentação pública
!docs/
!docs/*.md
!README.md

# Testes
!tests/
!tests/**/*.py
!tests/**/*.js

# CI/CD
!.github/
!.github/workflows/
!.github/workflows/*.yml

# Monitoring configs (sem secrets)
!monitoring/
!monitoring/*.yaml
!monitoring/*.yml
```

---

## ✅ PASSO 4: ESTRUTURA INICIAL DO REPOSITÓRIO

Após limpar o repositório, crie apenas estes arquivos iniciais:

### **1. README.md** (na raiz)

```markdown
# TriSLA

TriSLA: Uma Arquitetura SLA-Aware Baseada em IA, Ontologia e Contratos Inteligentes para Garantia de SLA em Redes 5G/O-RAN

## 📋 Sobre

Este repositório contém a implementação completa da arquitetura TriSLA para garantia de SLA em redes 5G/O-RAN.

## 🏗️ Estrutura

```
TriSLA/
├── apps/              # Módulos TriSLA (SEM-CSMF, ML-NSMF, etc.)
├── ansible/           # Playbooks para deploy
├── helm/              # Helm charts
├── configs/           # Configurações (templates)
├── docs/              # Documentação
├── monitoring/        # Configurações de observabilidade
├── scripts/           # Scripts de instalação/configuração
└── tests/             # Testes automatizados
```

## 🚀 Deploy

Consulte a documentação em `/docs` para instruções de deploy.

## 📄 Licença

[Adicione sua licença aqui]
```

### **2. .gitignore** (conforme criado acima)

### **3. Estrutura de diretórios vazia**

```bash
# Criar estrutura de diretórios (vazios inicialmente)
mkdir -p apps ansible helm configs docs monitoring scripts tests .github/workflows

# Criar arquivos .gitkeep para manter diretórios vazios no Git
touch apps/.gitkeep ansible/.gitkeep helm/.gitkeep configs/.gitkeep \
      docs/.gitkeep monitoring/.gitkeep scripts/.gitkeep tests/.gitkeep
```

---

## 📋 CHECKLIST: O QUE PUBLICAR E O QUE NÃO PUBLICAR

### ✅ **PUBLICAR (Código Público):**

- ✅ Código-fonte dos módulos (`/apps`)
- ✅ Playbooks Ansible genéricos (`/ansible`) - **sem secrets**
- ✅ Helm charts (`/helm`)
- ✅ Configurações de exemplo/template (`/configs/*.example.*`)
- ✅ Scripts de instalação (`/scripts`)
- ✅ Documentação pública (`/docs`)
- ✅ Testes (`/tests`)
- ✅ Workflows CI/CD (`.github/workflows`)
- ✅ Configurações de monitoring genéricas (`/monitoring`)

### ❌ **NÃO PUBLICAR (Mantém Local):**

- ❌ **TriSLA_PROMPTS/** - Pasta completa de prompts
- ❌ Secrets, senhas, tokens
- ❌ Configurações com IPs reais do NASP
- ❌ Inventories Ansible com dados reais
- ❌ Values.yaml com valores de produção
- ❌ Credenciais, chaves privadas
- ❌ Logs, arquivos temporários
- ❌ Documentação interna/privada
- ❌ Backups

---

## 🔒 SEGURANÇA: VERIFICAÇÃO ANTES DO PUSH

Antes de fazer `git push`, sempre verificar:

```bash
# Ver o que será commitado
git status

# Ver diferenças
git diff

# Verificar se há secrets acidentalmente
git diff --cached | grep -i "password\|secret\|key\|token" || echo "OK: Nenhum secret encontrado"

# Listar arquivos que serão commitados
git ls-files --cached
```

---

## 🚀 COMANDOS PARA PRIMEIRO COMMIT

```bash
# 1. Inicializar repositório (se novo)
git init

# 2. Adicionar remote (se necessário)
git remote add origin https://github.com/abelisboa/TriSLA.git

# 3. Adicionar arquivos iniciais
git add .gitignore README.md

# 4. Adicionar estrutura de diretórios
git add apps/.gitkeep ansible/.gitkeep helm/.gitkeep configs/.gitkeep \
      docs/.gitkeep monitoring/.gitkeep scripts/.gitkeep tests/.gitkeep

# 5. Commit inicial
git commit -m "chore: estrutura inicial do repositório TriSLA

- Adiciona .gitignore completo
- Cria estrutura de diretórios
- README inicial"

# 6. Push para GitHub
git branch -M main
git push -u origin main
```

---

## ⚠️ IMPORTANTE: VALIDAÇÃO CONTÍNUA

Sempre antes de fazer push:

1. ✅ Verificar `git status` - não deve listar `TriSLA_PROMPTS/`
2. ✅ Verificar `git diff` - não deve mostrar secrets
3. ✅ Verificar `.gitignore` está funcionando: `git check-ignore -v TriSLA_PROMPTS/`
4. ✅ Se `TriSLA_PROMPTS/` aparecer, adicionar ao `.gitignore` e fazer `git rm -r --cached TriSLA_PROMPTS/`

---

## 📝 NOTAS FINAIS

- **TriSLA_PROMPTS/** permanece apenas local, nunca será publicado
- Apenas código gerado pelos prompts será publicado
- Secrets e configurações sensíveis sempre ficam locais
- Use variáveis de ambiente ou GitHub Secrets para dados sensíveis

---

**Última atualização**: Guia de limpeza e preparação do repositório  
**Repositório**: https://github.com/abelisboa/TriSLA

