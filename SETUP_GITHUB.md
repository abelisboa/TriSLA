# 🔧 Setup GitHub - Passo a Passo

## ❌ Problema

O erro indica que o repositório `https://github.com/abelisboa/trisla-public.git` não existe ainda.

## ✅ Solução em 3 Passos

### Passo 1: Criar Repositório no GitHub

1. **Acesse**: https://github.com/new
2. **Preencha**:
   - **Repository name**: `trisla-public`
   - **Description**: `TriSLA Dashboard v3.2.4 - Monitoring and Observability Dashboard`
   - **Visibility**: Escolha `Public` ou `Private`
   - ⚠️ **IMPORTANTE**: NÃO marque nenhuma opção (sem README, .gitignore ou license)
3. **Clique**: "Create repository"

### Passo 2: Push do Repositório Local

Após criar o repositório, execute no WSL:

```bash
cd /mnt/c/Users/USER/Documents/trisla-deploy/trisla-public
git push -u origin main
```

### Passo 3: Verificar

- ✅ Push bem-sucedido
- ✅ Commits visíveis no GitHub
- ✅ CI/CD executando: https://github.com/abelisboa/trisla-public/actions

## 🔐 Se Pedir Autenticação

Se o GitHub pedir credenciais:

### Opção A: Personal Access Token (HTTPS)

1. Criar token: https://github.com/settings/tokens
2. Selecionar escopo: `repo` (todas as permissões)
3. Usar o token como senha quando pedir

### Opção B: SSH (Recomendado)

```bash
# Gerar chave SSH (se ainda não tiver)
ssh-keygen -t ed25519 -C "seu-email@example.com"

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub

# Adicionar em: https://github.com/settings/keys

# Mudar remote para SSH
git remote set-url origin git@github.com:abelisboa/trisla-public.git

# Tentar push novamente
git push -u origin main
```

## 📋 Comandos Rápidos (WSL)

```bash
# Navegar para o diretório
cd /mnt/c/Users/USER/Documents/trisla-deploy/trisla-public

# Verificar status
git status
git remote -v

# Se necessário, reconfigurar remote
git remote set-url origin https://github.com/abelisboa/trisla-public.git

# Push
git push -u origin main
```

## 🎯 Após Push Bem-Sucedido

1. **Criar tag**:
   ```bash
   git tag -a v3.2.4 -m "TriSLA Dashboard v3.2.4 - Production Release"
   git push origin v3.2.4
   ```

2. **Verificar GitHub Actions**:
   - Acesse: https://github.com/abelisboa/trisla-public/actions
   - Workflow deve executar automaticamente

3. **Verificar imagens no GHCR**:
   - Acesse: https://github.com/abelisboa/trisla-public/pkgs
   - Imagens devem aparecer após ~5 minutos

---

**Ação Imediata**: Criar o repositório em https://github.com/new



