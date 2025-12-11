# Checklist de Verificação - Módulo BESU

## ✅ Estrutura de Arquivos

- [x] `Dockerfile` criado e otimizado
- [x] `genesis.json` configurado (Chain ID: 1337, IBFT2)
- [x] `docker-compose-besu.yaml` para testes locais
- [x] Scripts: `start_besu.sh`, `check_besu.sh`, `validate_besu.sh`
- [x] `README.md` com documentação completa
- [x] `DEPLOY_NASP.md` com instruções de deploy
- [x] `.dockerignore` configurado

## ✅ Helm Chart

- [x] `deployment-besu.yaml` criado com healthcheck
- [x] `service-besu.yaml` criado (ClusterIP, portas 8545/8546/30303)
- [x] `configmap-besu.yaml` criado (genesis.json)
- [x] `pvc-besu.yaml` criado (se persistence habilitado)
- [x] `values.yaml` atualizado com configuração BESU completa
- [x] `values-nasp.yaml` atualizado com configuração BESU
- [x] `Chart.yaml` versionado (3.7.10)

## ✅ Integração BC-NSSMF

- [x] Deployment BC-NSSMF atualizado com variáveis de ambiente
- [x] `TRISLA_RPC_URL` apontando para serviço BESU (`http://trisla-besu:8545`)
- [x] `BESU_RPC_URL` apontando para serviço BESU (`http://trisla-besu:8545`)
- [x] `BC_ENABLED=true` configurado quando BESU habilitado
- [x] `TRISLA_CHAIN_ID=1337` configurado
- [x] Removida duplicação de variáveis de ambiente no deployment

## ✅ GitHub Actions

- [x] Workflow `besu-ci.yml` criado
- [x] Build e push da imagem para GHCR (`ghcr.io/abelisboa/trisla-besu`)
- [x] Validação do Helm chart (`helm lint`, `helm template`)
- [x] Tags automáticas (branch, sha, semver, latest)
- [x] Cache de build habilitado

## ✅ Testes Locais

- [ ] BESU inicia via Docker Compose (`./scripts/start_besu.sh`)
- [ ] RPC responde na porta 8545
- [ ] Chain ID correto (1337 / 0x539)
- [ ] Conta padrão pré-financiada
- [ ] BC-NSSMF conecta ao BESU local
- [ ] Registro de SLA funciona (`POST /bc/register`)

## ✅ Deploy NASP

- [ ] Helm chart validado (`helm lint ./helm/trisla`)
- [ ] Template gerado sem erros (`helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml`)
- [ ] Pod BESU sobe no cluster (`kubectl -n trisla get pods -l app.kubernetes.io/component=besu`)
- [ ] Serviço BESU exposto corretamente (`kubectl -n trisla get svc trisla-besu`)
- [ ] PVC criado (se persistence habilitado)
- [ ] BC-NSSMF conecta ao BESU no cluster
- [ ] Healthcheck do BC-NSSMF mostra `rpc_connected: true`
- [ ] Registro de SLA funciona no cluster (`POST /bc/register` retorna `tx`)

## ✅ Documentação

- [x] `README.md` com instruções de uso
- [x] `DEPLOY_NASP.md` com passo a passo completo de deploy
- [x] `CHECKLIST.md` (este arquivo)
- [x] Comentários no código explicando configurações
- [x] Troubleshooting documentado

## 🔄 Próximos Passos

1. **Testar localmente:**
   ```bash
   cd besu
   ./scripts/start_besu.sh
   ./scripts/check_besu.sh
   ./scripts/validate_besu.sh
   ```

2. **Fazer commit e push para GitHub:**
   ```bash
   git checkout -b feature/besu-module
   git add besu/
   git add helm/trisla/templates/deployment-besu.yaml
   git add helm/trisla/templates/service-besu.yaml
   git add helm/trisla/templates/configmap-besu.yaml
   git add helm/trisla/templates/pvc-besu.yaml
   git add helm/trisla/values.yaml
   git add helm/trisla/values-nasp.yaml
   git add helm/trisla/templates/deployment-bc-nssmf.yaml
   git add .github/workflows/besu-ci.yml
   git commit -m "feat: adicionar módulo BESU integrado ao BC-NSSMF

   - Dockerfile otimizado para BESU com healthcheck
   - Helm chart completo (deployment, service, configmap, PVC)
   - Scripts de inicialização e validação
   - Integração com BC-NSSMF via RPC (TRISLA_RPC_URL, BESU_RPC_URL)
   - Workflow GitHub Actions para build e push automático
   - Documentação completa (README, DEPLOY_NASP, CHECKLIST)
   - Genesis.json configurado com IBFT2 (Chain ID: 1337)

   Versão: 3.7.10"
   git push origin feature/besu-module
   ```

3. **Workflow GitHub Actions vai buildar e publicar imagem automaticamente**

4. **Deploy no NASP usando Helm:**
   ```bash
   ssh porvir5g@node1
   cd /path/to/trisla-repo
   helm upgrade --install trisla ./helm/trisla \
     -n trisla \
     -f ./helm/trisla/values-nasp.yaml \
     --cleanup-on-fail \
     --debug
   ```

5. **Validar deploy:**
   ```bash
   kubectl -n trisla get pods -l app.kubernetes.io/component=besu
   kubectl -n trisla logs -l app.kubernetes.io/component=besu
   kubectl -n trisla port-forward svc/trisla-besu 8545:8545
   curl -X POST http://localhost:8545 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
   ```

## 📝 Comandos de Validação

### Local
```bash
# Iniciar BESU
cd besu && ./scripts/start_besu.sh

# Verificar status
./scripts/check_besu.sh

# Validar integração
./scripts/validate_besu.sh
```

### Kubernetes/NASP
```bash
# Verificar pods
kubectl -n trisla get pods -l app.kubernetes.io/component=besu

# Verificar serviços
kubectl -n trisla get svc -l app.kubernetes.io/component=besu

# Verificar logs
kubectl -n trisla logs -f -l app.kubernetes.io/component=besu

# Testar RPC
kubectl -n trisla port-forward svc/trisla-besu 8545:8545 &
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'

# Verificar integração BC-NSSMF
kubectl -n trisla exec deploy/trisla-bc-nssmf -- \
  curl -s http://localhost:8083/health | jq
```

## ✅ Checklist Final de Validação

- [ ] BESU inicia sem erros (local e cluster)
- [ ] RPC HTTP responde corretamente (porta 8545)
- [ ] Chain ID correto (1337 / 0x539)
- [ ] Healthcheck funcionando
- [ ] BC-NSSMF conecta ao BESU
- [ ] Variáveis de ambiente corretas no BC-NSSMF
- [ ] Registro de SLA funciona (retorna tx_hash)
- [ ] Transações aparecem no blockchain
- [ ] Logs sem erros críticos
- [ ] Recursos (CPU/Memória) dentro dos limites
- [ ] PVC montado corretamente (se habilitado)
- [ ] Service expondo portas corretas
- [ ] ConfigMap do genesis.json válido

---

*Última atualização: 2025-01-15*
