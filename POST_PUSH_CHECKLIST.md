# ✅ Checklist Pós-Push - TriSLA Dashboard v3.2.4

## 🎉 Push Realizado com Sucesso!

O código foi enviado para o GitHub. Agora siga estes passos:

## 📋 Verificações Imediatas

### 1. Verificar GitHub Actions

Acesse: https://github.com/abelisboa/trisla-public/actions

**O que verificar:**
- [ ] Workflow `Build & Push TriSLA Dashboard` executou
- [ ] Status: ✅ verde (sucesso)
- [ ] Build do backend completado
- [ ] Build do frontend completado
- [ ] Push das imagens para GHCR bem-sucedido

**Tempo esperado**: 3-5 minutos após o push

### 2. Verificar Imagens no GHCR

Acesse: https://github.com/abelisboa/trisla-public/pkgs

**Imagens esperadas:**
- [ ] `trisla-dashboard-backend:latest`
- [ ] `trisla-dashboard-frontend:latest`

**Como verificar:**
- Imagens devem aparecer após o workflow completar
- Verificar data de criação (deve ser recente)
- Status deve estar como "Ready"

### 3. Verificar Tag de Versão

```bash
# Verificar tag local
git tag -l

# Verificar tag no GitHub
# Acesse: https://github.com/abelisboa/trisla-public/releases
# Deve aparecer: v3.2.4
```

## 🚀 Próximos Passos

### Opção A: Deploy Imediato no Kubernetes

Quando as imagens estiverem prontas no GHCR:

```bash
# Deploy via Helm
bash scripts/deploy-helm.sh

# Ou manualmente
helm install trisla-dashboard ./helm/trisla-dashboard \
  --namespace trisla \
  --create-namespace \
  --wait
```

### Opção B: Testar Localmente Primeiro

```bash
# Build local (opcional, para testar)
bash scripts/build-local.sh

# Ou usar Docker Compose
docker-compose up -d

# Testar
bash scripts/test-local.sh

# Parar
docker-compose down
```

## 🔍 Verificações Pós-Deploy (se fizer deploy)

### Kubernetes

```bash
# Verificar pods
kubectl get pods -n trisla -l app=trisla-dashboard

# Verificar services
kubectl get services -n trisla -l app=trisla-dashboard

# Verificar ServiceMonitor
kubectl get servicemonitors -n trisla

# Ver logs
kubectl logs -n trisla -l app=trisla-dashboard -c backend --tail=50
kubectl logs -n trisla -l app=trisla-dashboard -c frontend --tail=50
```

### Monitoramento

- [ ] Prometheus descobrindo o target
- [ ] Métricas aparecendo em `/metrics`
- [ ] Grafana dashboard visível
- [ ] ServiceMonitor funcionando

## 🐛 Troubleshooting

### GitHub Actions Falhou

1. Verificar logs do workflow
2. Verificar se Dockerfiles estão corretos
3. Verificar se paths estão corretos no workflow
4. Tentar re-executar o workflow

### Imagens Não Aparecem no GHCR

1. Aguardar alguns minutos (pode demorar)
2. Verificar logs do workflow para erros
3. Verificar permissões do token

### Deploy Falha

1. Verificar se imagens estão acessíveis
2. Verificar configuração do Helm chart
3. Verificar logs dos pods
4. Verificar recursos do cluster

## 📊 Status Esperado

Após todos os passos:

```
✅ Código no GitHub
✅ CI/CD executado
✅ Imagens no GHCR
✅ Tag v3.2.4 criada
✅ Deploy no Kubernetes (se aplicável)
✅ Monitoramento funcionando
```

---

**Próxima ação recomendada**: Verificar GitHub Actions e aguardar imagens no GHCR



