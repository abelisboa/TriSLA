# 🎯 Próximos Passos - TriSLA Dashboard v3.2.4

Este documento lista os próximos passos recomendados para finalizar o setup e colocar o projeto em produção.

## ✅ Status Atual

- ✅ Repositório Git inicializado
- ✅ Commits iniciais criados (2 commits)
- ✅ Remote configurado: `https://github.com/abelisboa/trisla-public.git`
- ✅ Scripts utilitários criados
- ✅ Documentação completa
- ✅ Helm charts configurados
- ✅ CI/CD workflow pronto

## 🚀 Próximos Passos (Prioridade)

### 1️⃣ Push para GitHub ⚠️ **IMPORTANTE**

O repositório local está pronto, mas precisa ser enviado para o GitHub:

```bash
# Verificar status
git status

# Fazer push inicial
git push -u origin main

# Se houver conflitos, verificar primeiro
git fetch origin
git log HEAD..origin/main  # Ver commits remotos
```

**⚠️ Nota**: Se o repositório GitHub ainda não existe ou está vazio, este comando pode falhar. Neste caso:
1. Criar o repositório no GitHub primeiro
2. Ou usar `git push -u origin main --force` (cuidado!)

### 2️⃣ Criar Tag de Versão

Após o push bem-sucedido:

```bash
# Criar tag anotada
git tag -a v3.2.4 -m "TriSLA Dashboard v3.2.4 - Production Release"

# Enviar tag
git push origin v3.2.4
```

### 3️⃣ Testar Build Local

Antes de confiar no CI/CD, teste localmente:

```bash
# Build das imagens
bash scripts/build-local.sh

# Ou manualmente
docker build -t trisla-dashboard-backend:latest ./backend
docker build -t trisla-dashboard-frontend:latest ./frontend
```

### 4️⃣ Testar Docker Compose

Verificar se tudo funciona localmente:

```bash
# Iniciar serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Testar endpoints
curl http://localhost:5000/health
curl http://localhost:5000/metrics
curl http://localhost:5174/health

# Parar serviços
docker-compose down
```

### 5️⃣ Testar Scripts Utilitários

```bash
# Testar script de build
bash scripts/build-local.sh

# Testar script de teste (após docker-compose up)
bash scripts/test-local.sh

# Testar script de deploy (requer Kubernetes)
bash scripts/deploy-helm.sh
```

### 6️⃣ Configurar GitHub Actions Secrets (se necessário)

Se as imagens forem privadas no GHCR, configure secrets:

1. Acesse: `https://github.com/abelisboa/trisla-public/settings/secrets/actions`
2. Adicione secrets se necessário:
   - `GHCR_TOKEN` (se necessário para push)
   - Outras variáveis de ambiente sensíveis

**Nota**: O `GITHUB_TOKEN` já está disponível automaticamente nas GitHub Actions.

### 7️⃣ Validar Helm Chart

Antes de fazer deploy em produção:

```bash
# Validar sintaxe
helm lint ./helm/trisla-dashboard

# Template dry-run
helm template trisla-dashboard ./helm/trisla-dashboard

# Testar instalação (se tiver Kubernetes local)
helm install trisla-dashboard ./helm/trisla-dashboard --namespace trisla --create-namespace --dry-run
```

### 8️⃣ Deploy no Kubernetes (Produção)

Quando estiver pronto para produção:

```bash
# Deploy via Helm
bash scripts/deploy-helm.sh

# Ou manualmente
helm install trisla-dashboard ./helm/trisla-dashboard \
  --namespace trisla \
  --create-namespace \
  --wait

# Verificar status
kubectl get pods -n trisla
kubectl get services -n trisla
kubectl get servicemonitors -n trisla
```

### 9️⃣ Verificar Integração com Prometheus

Após o deploy:

```bash
# Verificar se o ServiceMonitor foi descoberto
kubectl get servicemonitor -n trisla trisla-dashboard-monitor

# Verificar métricas no Prometheus
# Acesse Prometheus UI e verifique targets
```

### 🔟 Configurar Grafana Dashboard

O ConfigMap do Grafana será descoberto automaticamente. Verificar:

```bash
# Verificar ConfigMap
kubectl get configmap -n trisla trisla-grafana-dashboard

# No Grafana, o dashboard deve aparecer automaticamente
# Acesse Grafana UI e verifique se o dashboard está disponível
```

## 📋 Checklist de Validação

Antes de considerar pronto para produção:

- [ ] Código commitado e push feito para GitHub
- [ ] Tag de versão criada
- [ ] Build local testado com sucesso
- [ ] Docker Compose testado localmente
- [ ] Scripts utilitários testados
- [ ] Helm chart validado
- [ ] CI/CD pipeline executado com sucesso (após push)
- [ ] Imagens Docker disponíveis no GHCR
- [ ] Deploy no Kubernetes testado (se aplicável)
- [ ] Métricas aparecendo no Prometheus
- [ ] Dashboard visível no Grafana

## 🐛 Troubleshooting

### Problema: Push falha

```bash
# Verificar conexão
git remote -v

# Verificar autenticação GitHub
# Configure token via: git config --global credential.helper store
```

### Problema: Build falha

```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar Dockerfiles
docker build --no-cache -t test-backend ./backend
docker build --no-cache -t test-frontend ./frontend
```

### Problema: Helm deploy falha

```bash
# Verificar conexão Kubernetes
kubectl cluster-info

# Verificar namespace
kubectl get namespace trisla

# Ver logs detalhados
helm install trisla-dashboard ./helm/trisla-dashboard \
  --namespace trisla \
  --create-namespace \
  --debug \
  --dry-run
```

## 📚 Documentação Adicional

- [README.md](README.md) - Visão geral do projeto
- [README_OPERATIONS_PROD.md](README_OPERATIONS_PROD.md) - Guia de operações
- [Helm Chart](./helm/trisla-dashboard/) - Documentação do Helm

## 🔗 Links Úteis

- **GitHub Repository**: https://github.com/abelisboa/trisla-public
- **GHCR Images**: https://github.com/abelisboa/trisla-public/pkgs
- **Actions**: https://github.com/abelisboa/trisla-public/actions

---

**Próxima ação recomendada**: Fazer push para GitHub e criar tag v3.2.4



