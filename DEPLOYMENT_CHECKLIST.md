# ✅ Checklist de Deploy - TriSLA Dashboard v3.2.4

Use este checklist para garantir que todos os passos necessários foram executados antes do deploy em produção.

## 📋 Pré-Deploy (Local)

### Repositório Git
- [x] Repositório inicializado
- [x] Commits criados
- [x] Remote configurado
- [ ] **Push para GitHub** ← PRÓXIMO PASSO
- [ ] Tag v3.2.4 criada e enviada

### Build e Testes Locais
- [ ] Docker instalado e funcionando
- [ ] Build local testado (`bash scripts/build-local.sh`)
- [ ] Docker Compose testado (`docker-compose up -d`)
- [ ] Scripts testados localmente
- [ ] Endpoints respondendo corretamente

### Validação Helm
- [ ] Helm instalado (`helm version`)
- [ ] Chart validado (`helm lint ./helm/trisla-dashboard`)
- [ ] Template gerado com sucesso (`helm template`)
- [ ] Values.yaml revisado

## 🚀 Deploy (Produção)

### CI/CD
- [ ] Push feito para GitHub
- [ ] GitHub Actions executado com sucesso
- [ ] Imagens disponíveis no GHCR
- [ ] Imagens acessíveis pelo cluster Kubernetes

### Kubernetes
- [ ] Acesso ao cluster configurado (`kubectl cluster-info`)
- [ ] Namespace `trisla` criado ou verificado
- [ ] Helm chart instalado/atualizado
- [ ] Pods em estado `Running`
- [ ] Services criados e expostos
- [ ] Port-forward testado (se necessário)

### Monitoramento
- [ ] ServiceMonitor criado
- [ ] ConfigMap do Grafana aplicado
- [ ] Prometheus descobrindo o target
- [ ] Métricas aparecendo no Prometheus
- [ ] Dashboard visível no Grafana

## 🔍 Verificação Pós-Deploy

### Saúde dos Pods
```bash
kubectl get pods -n trisla -l app=trisla-dashboard
kubectl describe pod -n trisla -l app=trisla-dashboard
```

### Logs
```bash
kubectl logs -n trisla -l app=trisla-dashboard -c backend --tail=50
kubectl logs -n trisla -l app=trisla-dashboard -c frontend --tail=50
```

### Endpoints
- [ ] Backend health: `http://localhost:5000/health` (via port-forward)
- [ ] Backend metrics: `http://localhost:5000/metrics`
- [ ] Frontend: `http://localhost:5174` (via port-forward)

### Integração
- [ ] Prometheus coletando métricas
- [ ] Grafana dashboard funcionando
- [ ] ServiceMonitor ativo

## 📊 Status Final Esperado

```bash
# Pods
NAME                                  READY   STATUS    RESTARTS   AGE
trisla-dashboard-xxxxx-yyyyy          2/2     Running   0          5m

# Services
NAME                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
trisla-dashboard     ClusterIP   10.xxx.xxx.xxx  <none>        5000/TCP,5174/TCP

# ServiceMonitor
NAME                          AGE
trisla-dashboard-monitor      5m

# ConfigMap
NAME                       DATA   AGE
trisla-grafana-dashboard   1      5m
```

---

**Status Atual**: Preparado para deploy  
**Próxima Ação**: Push para GitHub ou teste local



