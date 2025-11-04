# Contribuindo para o TriSLA Dashboard

Obrigado por considerar contribuir para o TriSLA Dashboard! Este documento fornece diretrizes para contribuir com o projeto.

## 🚀 Primeiro Passo

1. **Fork** o repositório
2. **Clone** seu fork:
   ```bash
   git clone https://github.com/seu-usuario/trisla-public.git
   cd trisla-public
   ```

## 📝 Workflow de Desenvolvimento

### Branches

- `main`: Branch principal (produção)
- `develop`: Branch de desenvolvimento
- `feature/*`: Novas funcionalidades
- `fix/*`: Correções de bugs
- `docs/*`: Atualizações de documentação

### Commits

Use mensagens de commit descritivas seguindo o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(escopo): descrição curta

Descrição detalhada (opcional)
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Tarefas de manutenção

**Exemplos:**
```
feat(backend): Add Prometheus metrics endpoint
fix(frontend): Resolve nginx proxy configuration
docs(readme): Update deployment instructions
```

## 🔧 Desenvolvimento Local

1. **Instalar dependências:**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Rodar localmente:**
   ```bash
   # Usando Docker Compose
   docker-compose up -d
   
   # Ou usando scripts
   bash scripts/start-dashboard.sh
   ```

3. **Testar:**
   ```bash
   bash scripts/test-local.sh
   ```

## 📦 Build e Deploy

### Build Local
```bash
bash scripts/build-local.sh
```

### Deploy via Helm
```bash
bash scripts/deploy-helm.sh
```

## ✅ Checklist antes de Pull Request

- [ ] Código segue os padrões do projeto
- [ ] Testes passam localmente
- [ ] Documentação atualizada (se necessário)
- [ ] Commits seguem o padrão Conventional Commits
- [ ] Branch atualizada com `main` (rebase ou merge)

## 🐛 Reportando Bugs

Ao reportar bugs, inclua:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. atual
- Ambiente (OS, versões, etc.)
- Logs relevantes

## 💡 Sugerindo Funcionalidades

Ao sugerir funcionalidades:
- Descreva o problema que resolve
- Explique a solução proposta
- Considere alternativas
- Inclua exemplos de uso

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

**Obrigado por contribuir!** 🎉



