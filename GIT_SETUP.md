# Git Setup - TriSLA Dashboard v3.2.4

Este documento descreve o setup do repositório Git e comandos úteis para versionamento.

## 📋 Status do Repositório

- **Branch principal**: `main`
- **Commits**: 2 (atual)
- **Remote**: Não configurado (pronto para configurar)

## 🚀 Configuração Inicial Completa

### 1. Repositório Inicializado

```bash
git init
git branch -M main
```

### 2. Commits Criados

1. **Commit inicial** (`60af059`):
   - Estrutura completa do projeto
   - Backend e Frontend
   - Helm charts
   - CI/CD workflow
   - Documentação

2. **Scripts adicionados** (`3b7a5f7`):
   - build-local.sh
   - test-local.sh
   - deploy-helm.sh
   - start-dashboard.sh
   - connect-trisla-nasp-v3.2.4.sh

## 🔗 Conectar ao GitHub

### Opção 1: Repositório Novo

```bash
# Criar repositório no GitHub primeiro, depois:
git remote add origin https://github.com/abelisboa/trisla-public.git
git push -u origin main
```

### Opção 2: Repositório Existente

```bash
# Se o repositório já existe:
git remote add origin https://github.com/abelisboa/trisla-public.git
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 📝 Workflow Básico

### Adicionar Mudanças

```bash
# Ver status
git status

# Adicionar arquivos específicos
git add <arquivo>

# Adicionar tudo
git add .

# Commitar
git commit -m "tipo: descrição da mudança"
```

### Convenção de Commits

Seguindo [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas de manutenção

### Enviar para o Remote

```bash
# Primeira vez
git push -u origin main

# Próximas vezes
git push
```

## 🌿 Branches

### Criar Nova Branch

```bash
git checkout -b feature/nome-da-funcionalidade
# ou
git checkout -b fix/nome-do-bug
```

### Voltar para Main

```bash
git checkout main
```

### Mesclar Branch

```bash
git checkout main
git merge feature/nome-da-funcionalidade
```

## 📊 Comandos Úteis

### Ver Histórico

```bash
# Resumido
git log --oneline

# Detalhado
git log

# Com gráfico
git log --oneline --graph --all
```

### Ver Diferenças

```bash
# Arquivos modificados
git diff

# Arquivo específico
git diff <arquivo>

# Comparar commits
git diff <commit1> <commit2>
```

### Desfazer Mudanças

```bash
# Descartar mudanças não commitadas
git restore <arquivo>

# Desfazer último commit (mantendo mudanças)
git reset --soft HEAD~1

# Ver histórico e voltar
git reflog
git reset --hard <commit-hash>
```

## 🔐 Segurança

### Arquivos Sensíveis

Nunca commite:
- `.env` (usar `.env.example`)
- Senhas ou tokens
- Chaves privadas
- Arquivos de log grandes

### Verificar antes de Commit

```bash
# Ver o que será commitado
git status
git diff --staged
```

## 📦 Tags para Versões

```bash
# Criar tag
git tag -a v3.2.4 -m "TriSLA Dashboard v3.2.4"

# Enviar tags
git push origin v3.2.4
# ou todas
git push origin --tags
```

## 🎯 Próximos Passos

1. ✅ Repositório Git inicializado
2. ✅ Commits iniciais criados
3. ⏭️ Configurar remote do GitHub
4. ⏭️ Fazer push inicial
5. ⏭️ Configurar branch protection (se necessário)
6. ⏭️ Configurar GitHub Actions secrets (para CI/CD)

---

**Última atualização**: 2024



