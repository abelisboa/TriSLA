# Checklist de Pré-Deploy NASP — TriSLA (Versão 2)

**Data:** 2025-11-22  
**Versão:** 2.0  
**Objective:** Garantir que o TriSLA está pronto for deploy controlado no NASP (deploy local no node1)

---

## 1. Infraestrutura NASP

### 1.1 Cluster Kubernetes

- [ ] **Existe um cluster com 2 nodes operacionais**
  - verify: `kubectl get nodes`
  - Esperado: 2 nodes no status `Ready`

- [ ] **Nós visíveis via kubectl get nodes**
  - verify conectividade: `kubectl cluster-info`
  - verify versão: `kubectl version --short`

- [ ] **CNI configured e saudável**
  - verify Calico: `kubectl get pods -n kube-system -l k8s-app=calico-node`
  - Esperado: Todos os pods in `Running`

- [ ] **Namespaces padrão of NASP funcionando**
  - verify namespaces: `kubectl get namespaces`
  - Esperado: Namespaces como `monitoring`, `nasp`, etc. existem

**Comandos de validation:**
```bash
kubectl get nodes
kubectl get pods -n kube-system
kubectl get namespaces
```

---

## 2. TriSLA — Dependências Técnicas

### 2.1 SEM-CSMF

- [ ] **Ontologia `trisla.ttl` presente no container SEM-CSMF**
  - verify: `apps/sem-csmf/src/ontology/trisla.ttl` existe
  - verify Dockerfile: Ontologia copiada for container

- [ ] **PostgreSQL acessível**
  - verify: Configuration of `DATABASE_URL` in `values-nasp.yaml`
  - verify: Namespace e service PostgreSQL existem

### 2.2 ML-NSMF

- [ ] **Modelo ML (`viability_model.pkl`) presente no ML-NSMF**
  - verify: `apps/ml-nsmf/models/viability_model.pkl` existe
  - verify Dockerfile: Modelo copiado for container

- [ ] **Scaler (`scaler.pkl`) presente**
  - verify: `apps/ml-nsmf/models/scaler.pkl` existe (se aplicável)

### 2.3 BC-NSSMF

- [ ] **contract Solidity já deployado no GoQuorum/Besu**
  - verify: `apps/bc-nssmf/src/contracts/contract_address.json` existe
  - verify: contract deployado via `deploy_contracts.py`

- [ ] **Configuration of BC-NSSMF aponta for o RPC correto**
  - verify: `bcNssmf.besu.rpcUrl` in `values-nasp.yaml`
  - Formato esperado: `http://<BESU_SERVICE>.<BESU_NS>.svc.cluster.local:8545`
  - ⚠️ **NÃO expor IP real in documentação**

- [ ] **Chain ID configured corretamente**
  - verify: `bcNssmf.besu.chainId` in `values-nasp.yaml`

### 2.4 SLA-Agent Layer

- [ ] **Agentes SLA estão configureds for apontar for o NASP Adapter**
  - verify: `naspAdapter.naspEndpoints.*` in `values-nasp.yaml`
  - verify: Agentes não usam metrics hardcoded (according to FASE 5)

- [ ] **Configuration of SLOs por domínio**
  - verify: `apps/sla-agent-layer/src/config/slo_*.yaml` existem
  - verify: SLOs carregados corretamente pelos agentes

### 2.5 Decision Engine

- [ ] **Regras YAML presentes**
  - verify: `apps/decision-engine/config/decision_rules.yaml` existe
  - verify: Regras carregadas corretamente (sem `eval()`)

### 2.6 NASP Adapter

- [ ] **Endpoints NASP descobertos e configureds**
  - Executar: `scripts/discover-nasp-endpoints.sh`
  - Revisar: `docs/nasp/NASP_CONTEXT_REPORT.md`
  - Preencher: `naspAdapter.naspEndpoints.*` in `values-nasp.yaml`

---

## 3. Configuration of Helm

### 3.1 values-nasp.yaml

- [ ] **`helm/trisla/values-nasp.yaml` preenchido according to `docs/deployment/VALUES_PRODUCTION_GUIDE.md`**
  - Executar: `scripts/fill_values_production.sh` (ou preencher manualmente)
  - Revisar: Todos os placeholders substituídos por valores válidos

- [ ] **Todos os placeholders substituídos por valores válidos (apenas no YAML)**
  - ⚠️ **NÃO expor valores reais in documentação Markdown**
  - Usar FQDNs Kubernetes: `http://<SERVICE>.<NS>.svc.cluster.local:<PORT>`

- [ ] **Namespace alvo (`global.namespace`) definido corretamente**
  - Padrão: `trisla`
  - verify: Namespace existe ou será criado durante deploy

- [ ] **Registry de imagens configured**
  - verify: `global.imageRegistry` aponta for GHCR correto
  - Formato: `ghcr.io/<GHCR_USER>`

### 3.2 validation de Helm Chart

- [ ] **Helm chart validado**
  ```bash
  helm lint ./helm/trisla
  helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug
  ```

- [ ] **Nenhum error crítico no template**
  - verify: output of `helm template` não contém erros
  - verify: Todos os recursos Kubernetes gerados são válidos

---

## 4. Imagens e Registro

### 4.1 audit GHCR

- [ ] **`docs/ghcr/IMAGES_GHCR_MATRIX.md` revisado**
  - Revisar: Status de cada imagem according to matriz documentada
  - verify: Todas as 7 imagens principais estão listadas e marcadas como OK

- [ ] **Imagens GHCR validadas localmente**
  - verify: Imagens podem ser puxadas of GHCR
  - Comando de teste: `docker pull ghcr.io/abelisboa/trisla-<module-name>:latest`
  - Imagens críticas: SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer, NASP Adapter
  - Imagem opcional: UI Dashboard

- [ ] **Nenhuma imagem crítica marcada como FALTANDO**
  - Todas as imagens devem estar disponíveis no GHCR antes of deploy

### 4.2 Secret GHCR

- [ ] **Secret GHCR criado no namespace alvo**
  ```bash
  kubectl create secret docker-registry ghcr-secret \
    --docker-server=ghcr.io \
    --docker-username=<GHCR_USER> \
    --docker-password=<GHCR_TOKEN> \
    --namespace=<TRISLA_NAMESPACE>
  ```

- [ ] **Secret configured no Helm chart**
  - verify: `imagePullSecrets` configured nos Deployments
  - verify: Secret referenciado corretamente

---

## 5. Segurança e Conformidade

### 5.1 Sem Tokens ou Segredos in Arquivos Públicos

- [ ] **Sem tokens ou segredos in arquivos `.md` públicos**
  - verify: Nenhum token hardcoded in `docs/`
  - verify: Nenhum token hardcoded in `README*.md`

- [ ] **`TriSLA_PROMPTS/` continua ignorado pelo Git**
  - verify: `.gitignore` contém `TriSLA_PROMPTS/`
  - verify: Nenhum arquivo de `TriSLA_PROMPTS/` foi commitado

### 5.2 Scripts Internos

- [ ] **Scripts internos de limpeza e backup revisados**
  - verify: Scripts não expõem informações sensíveis
  - verify: Scripts são executáveis e bem documentados

### 5.3 Network Policies (Opcional)

- [ ] **Network Policies configured (se aplicável)**
  - verify: Políticas de rede definidas no Helm chart
  - verify: Comunicação entre módulos permitida

---

## 6. Ansible e Automação

### 6.1 Inventory

- [ ] **`ansible/inventory.yaml` configured**
  - verify: Nodes NASP definidos (usando placeholders in docs)
  - verify: variables de grupo configured

### 6.2 Playbooks

- [ ] **Playbooks revisados e atualizados**
  - `ansible/playbooks/pre-flight.yml` — Validações pré-deploy
  - `ansible/playbooks/setup-namespace.yml` — Criação de namespace
  - `ansible/playbooks/deploy-trisla-nasp.yml` — Deploy Helm
  - `ansible/playbooks/validate-cluster.yml` — validation pós-deploy

### 6.3 Teste de Playbooks

- [ ] **Playbooks testados (dry-run)**
  ```bash
  ansible-playbook -i ansible/inventory.yaml ansible/playbooks/pre-flight.yml --check
  ```

---

## 7. Documentação

### 7.1 Documentos Criados

- [ ] **`docs/nasp/NASP_CONTEXT_REPORT.md` gerado**
  - Executar: `scripts/discover-nasp-endpoints.sh`
  - Revisar: Relatório não contém IPs reais

- [ ] **`docs/deployment/VALUES_PRODUCTION_GUIDE.md` revisado**
  - verify: guide completo e claro
  - verify: Exemplos usam placeholders

- [ ] **`docs/ghcr/IMAGES_GHCR_MATRIX.md` revisado**
  - Revisar: Status de imagens according to documentação
  - verify: Todas as imagens necessárias estão listadas

- [ ] **`docs/NASP_DEPLOY_RUNBOOK.md` revisado**
  - verify: Runbook completo e seguível
  - verify: Comandos não expõem IPs reais

### 7.2 READMEs Atualizados

- [ ] **`README_OPERATIONS_PROD.md` atualizado**
  - verify: Section sobre NASP adicionada
  - verify: Links for documentos in `docs/`

- [ ] **`DEVELOPER_GUIDE.md` atualizado**
  - verify: Section sobre integração NASP adicionada
  - verify: Diferenças entre local e NASP documentadas

---

## 8. Checklist Final

- [ ] Todos os itens acima marcados como concluídos
- [ ] Nenhum IP real in documentação Markdown
- [ ] `values-nasp.yaml` preenchido e validado
- [ ] Todas as imagens críticas disponíveis no GHCR
- [ ] Playbooks Ansible testados
- [ ] Documentação completa e auditável

---

## 9. Próximos Passos Após Checklist

1. **Executar Runbook de Deploy:**
   - Seguir `docs/NASP_DEPLOY_RUNBOOK.md`

2. **Deploy Controlado:**
   - Executar playbooks Ansible na ordem recomendada
   - Monitorar logs durante deploy

3. **validation Pós-Deploy:**
   - Executar `ansible/playbooks/validate-cluster.yml`
   - verify health checks de todos os módulos

---

**Status of Checklist:** ⬜ Não iniciado | 🟡 Em progresso | ✅ Concluído

**Data de Conclusão:** _______________

**Operador Responsável:** _______________

---

**Versão:** 2.0  
**Data:** 2025-11-22  
**ENGINE MASTER:** Sistema de Pré-Deploy TriSLA


