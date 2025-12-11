# Checklist de Pré-Release — TriSLA v3.5.0

**Data:** 2025-01-27  
**Release:** TriSLA v3.5.0  
**Status:** ⏳ Aguardando Execução Manual

---

## 📋 Pré-requisitos

Antes de criar a release, certifique-se de que:

- ✅ Todas as mudanças foram commitadas
- ✅ Todos os testes passaram
- ✅ Helm chart validado
- ✅ Documentação atualizada
- ✅ CHANGELOG.md criado/atualizado

---

## ✅ Verificações Pré-Release

### 1. Verificar Estado do Repositório

```bash
cd ~/gtp5g/trisla

# Ver estado do repositório
git status

# Ver diferenças não commitadas
git diff

# Verificar se não há referências antigas
grep -R "trisla-portal" . || echo "✅ OK: sem 'trisla-portal'"
grep -R "values-production.yaml" . || echo "✅ OK: sem 'values-production.yaml'"
grep -R "ppgca.unisinos.br" . || echo "✅ OK: sem host externo"
```

### 2. Validar Helm Chart

```bash
cd ~/gtp5g/trisla

# Lint do chart
helm lint ./helm/trisla

# Template validation
helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug | head -n 60
```

**Resultado esperado:**
- ✅ Helm lint: sem erros
- ✅ Template: recursos Kubernetes válidos gerados

### 3. Validar Ansible (Sintaxe)

```bash
cd ~/gtp5g/trisla
cd ansible

# Verificar sintaxe dos playbooks
ansible-playbook --syntax-check playbooks/deploy-trisla-nasp.yml
ansible-playbook --syntax-check playbooks/pre-flight.yml
ansible-playbook --syntax-check playbooks/setup-namespace.yml
ansible-playbook --syntax-check playbooks/validate-cluster.yml

cd ..
```

**Resultado esperado:**
- ✅ Sintaxe válida em todos os playbooks

### 4. Validar Scripts

```bash
cd ~/gtp5g/trisla

# Verificar se scripts principais existem e são executáveis
ls -la scripts/deploy-trisla-nasp-auto.sh
ls -la scripts/deploy-trisla-nasp.sh
ls -la scripts/prepare-nasp-deploy.sh
ls -la scripts/validate-helm.sh

# Verificar help do script principal (se existir)
./scripts/deploy-trisla-nasp-auto.sh --help 2>/dev/null || echo "Script não tem flag --help"
```

### 5. Verificar Versões

```bash
cd ~/gtp5g/trisla

# Verificar versão no Chart.yaml
grep "version:" helm/trisla/Chart.yaml
# Esperado: version: 3.5.0

# Verificar versão no README
grep "version-3.5.0" README.md
# Esperado: badge com version-3.5.0

# Verificar CHANGELOG
head -n 20 CHANGELOG.md
# Esperado: ## [3.5.0] — 2025-01-27
```

---

## 🚀 Comandos para Criar a Release

### Passo 1: Commit das Mudanças

```bash
cd ~/gtp5g/trisla

# Adicionar todos os arquivos modificados
git add .

# Commit com mensagem de release
git commit -am "🚀 TriSLA v3.5.0 — Release estável NASP local

- Auditoria DevOps completa (scripts + Helm + Ansible)
- Consolidação de values-nasp.yaml como fonte canônica
- Execução local no NASP (127.0.0.1)
- Proteções GitHub (.gitignore, workflow de safety)
- Documentação premium (README, docs/)
- Versão atualizada para 3.5.0

Ver CHANGELOG.md para detalhes completos."
```

### Passo 2: Criar Tag

```bash
cd ~/gtp5g/trisla

# Criar tag anotada
git tag -a v3.5.0 -m "TriSLA v3.5.0 — NASP local, DevOps auditado

Esta release consolida todas as melhorias de DevOps e estabelece o repositório como solução pronta para produção.

Principais mudanças:
- Deploy 100% local no NASP (127.0.0.1)
- values-nasp.yaml como arquivo canônico
- Release name padronizado: trisla
- Proteções GitHub implementadas
- Documentação completa e sincronizada

Ver CHANGELOG.md para changelog completo."
```

### Passo 3: Push para GitHub

```bash
cd ~/gtp5g/trisla

# Push do commit
git push origin main

# Push da tag
git push origin v3.5.0
```

---

## 📝 Texto da Release do GitHub

### Título

```
TriSLA v3.5.0 — Release Estável NASP Local
```

### Corpo (Markdown)

```markdown
# 🚀 TriSLA v3.5.0 — Release Estável NASP Local

Esta release representa uma **consolidação completa** do repositório TriSLA para operação em produção no ambiente NASP, com deploy totalmente automatizado e local.

## ✨ Principais Mudanças

### 🔧 Auditoria DevOps Completa
- Scripts padronizados (release `trisla`, values `values-nasp.yaml`)
- Ordem lógica validada: Pré-checks → Preparação → Validação → Deploy → Healthcheck
- Scripts principais documentados no README

### 📦 Consolidação de values-nasp.yaml
- Arquivo canônico estabelecido: `helm/trisla/values-nasp.yaml`
- Remoção de `values-production.yaml`
- Placeholders documentados

### 🚀 Execução Local no NASP (127.0.0.1)
- Deploy 100% local (sem SSH/SCP)
- Ansible local configurado
- Scripts assumem operador no node1

### 🔒 Proteções GitHub
- `.gitignore` completo
- GitHub Actions workflow de validação
- Script de limpeza de histórico

### 📚 Documentação Premium
- README completamente reconstruído
- Seção "Fluxo de Automação DevOps"
- Interfaces I-01 a I-07 documentadas
- Troubleshooting básico incluído

## 📋 Upgrade da Versão Anterior

```bash
cd ~/gtp5g/trisla
git pull origin main
git checkout v3.5.0

# Revisar values-nasp.yaml
cp helm/trisla/values-nasp.yaml helm/trisla/values-nasp.yaml.backup
vim helm/trisla/values-nasp.yaml

# Validar
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml

# Deploy
./scripts/deploy-trisla-nasp-auto.sh
```

## 🔗 Links Úteis

- **Changelog Completo**: [CHANGELOG.md](CHANGELOG.md)
- **Validação Completa**: [VALIDATION_REPORT_FINAL.md](VALIDATION_REPORT_FINAL.md)
- **Auditoria DevOps**: [DEVOPS_AUDIT_REPORT.md](DEVOPS_AUDIT_REPORT.md)
- **Proteções GitHub**: [GITHUB_SAFETY_REPORT.md](GITHUB_SAFETY_REPORT.md)

## 📊 Estatísticas

- **Arquivos auditados**: 50+
- **Scripts verificados**: 9 principais
- **Playbooks verificados**: 4
- **Templates verificados**: 7
- **Documentos verificados**: 8
- **Taxa de conformidade**: 100%

---

**Data de Release**: 2025-01-27  
**Versão**: 3.5.0  
**Compatibilidade**: NASP local (127.0.0.1)
```

---

## ✅ Checklist Final

Antes de criar a release, confirme:

- [ ] Todas as verificações pré-release passaram
- [ ] Helm chart validado sem erros
- [ ] Ansible playbooks com sintaxe válida
- [ ] Versões atualizadas (Chart.yaml, README.md)
- [ ] CHANGELOG.md criado/atualizado
- [ ] Nenhuma referência a `trisla-portal` ou `values-production.yaml`
- [ ] Documentação sincronizada
- [ ] Commit das mudanças realizado
- [ ] Tag criada
- [ ] Push para GitHub realizado
- [ ] Release criada no GitHub com o texto acima

---

## 🎯 Após a Release

Após criar a release no GitHub:

1. **Verificar que a tag foi criada**:
   ```bash
   git tag -l "v3.5.0"
   ```

2. **Verificar que o push foi bem-sucedido**:
   ```bash
   git ls-remote --tags origin | grep v3.5.0
   ```

3. **Monitorar GitHub Actions**:
   - Verificar que o workflow `push-safety-check.yml` passou
   - Verificar que não há erros

4. **Documentar a release**:
   - Criar release no GitHub usando o texto fornecido acima
   - Adicionar assets se necessário (Helm chart package, etc.)

---

**Status:** ⏳ Aguardando execução manual pelo operador

