# Checklist de Pré-Deploy NASP — TriSLA (Versão 2)

**Data:** 2025-11-22  
**Versão:** 2.0  
**Objetivo:** Garantir que o TriSLA está pronto para deploy controlado no NASP (deploy local no node1)

---

## 1. Infraestrutura NASP

### 1.1 Cluster Kubernetes

- [ ] **Existe um cluster com 2 nodes operacionais**
  - Verificar: `kubectl get nodes`
  - Esperado: 2 nodes no status `Ready`

- [ ] **Nós visíveis via kubectl get nodes**
  - Verificar conectividade: `kubectl cluster-info`
  - Verificar versão: `kubectl version --short`

- [ ] **CNI configurado e saudável**
  - Verificar Calico: `kubectl get pods -n kube-system -l k8s-app=calico-node`
  - Esperado: Todos os pods em `Running`

- [ ] **Namespaces padrão do NASP funcionando**
  - Verificar namespaces: `kubectl get namespaces`
  - Esperado: Namespaces como `monitoring`, `nasp`, etc. existem

**Comandos de validação:**
```bash
kubectl get nodes
kubectl get pods -n kube-system
kubectl get namespaces
```

---

## 2. TriSLA — Dependências Técnicas

### 2.1 SEM-CSMF

- [ ] **Ontologia `trisla.owl` presente no container SEM-CSMF**
  - Verificar: `apps/sem-csmf/src/ontology/trisla.owl` existe
  - Verificar Dockerfile: Ontologia copiada para container

- [ ] **PostgreSQL acessível**
  - Verificar: Configuração de `DATABASE_URL` em `values-production.yaml`
  - Verificar: Namespace e serviço PostgreSQL existem

### 2.2 ML-NSMF

- [ ] **Modelo ML (`viability_model.pkl`) presente no ML-NSMF**
  - Verificar: `apps/ml-nsmf/models/viability_model.pkl` existe
  - Verificar Dockerfile: Modelo copiado para container

- [ ] **Scaler (`scaler.pkl`) presente**
  - Verificar: `apps/ml-nsmf/models/scaler.pkl` existe (se aplicável)

### 2.3 BC-NSSMF

- [ ] **Contrato Solidity já deployado no GoQuorum/Besu**
  - Verificar: `apps/bc-nssmf/src/contracts/contract_address.json` existe
  - Verificar: Contrato deployado via `deploy_contracts.py`

- [ ] **Configuração do BC-NSSMF aponta para o RPC correto**
  - Verificar: `bcNssmf.besu.rpcUrl` em `values-production.yaml`
  - Formato esperado: `http://<BESU_SERVICE>.<BESU_NS>.svc.cluster.local:8545`
  - ⚠️ **NÃO expor IP real em documentação**

- [ ] **Chain ID configurado corretamente**
  - Verificar: `bcNssmf.besu.chainId` em `values-production.yaml`

### 2.4 SLA-Agent Layer

- [ ] **Agentes SLA estão configurados para apontar para o NASP Adapter**
  - Verificar: `naspAdapter.naspEndpoints.*` em `values-production.yaml`
  - Verificar: Agentes não usam métricas hardcoded (conforme FASE 5)

- [ ] **Configuração de SLOs por domínio**
  - Verificar: `apps/sla-agent-layer/src/config/slo_*.yaml` existem
  - Verificar: SLOs carregados corretamente pelos agentes

### 2.5 Decision Engine

- [ ] **Regras YAML presentes**
  - Verificar: `apps/decision-engine/config/decision_rules.yaml` existe
  - Verificar: Regras carregadas corretamente (sem `eval()`)

### 2.6 NASP Adapter

- [ ] **Endpoints NASP descobertos e configurados**
  - Executar: `scripts/discover_nasp_endpoints.sh`
  - Revisar: `docs/NASP_CONTEXT_REPORT.md`
  - Preencher: `naspAdapter.naspEndpoints.*` em `values-production.yaml`

---

## 3. Configuração de Helm

### 3.1 values-production.yaml

- [ ] **`helm/trisla/values-production.yaml` preenchido conforme `docs/VALUES_PRODUCTION_GUIDE.md`**
  - Executar: `scripts/fill_values_production.sh` (ou preencher manualmente)
  - Revisar: Todos os placeholders substituídos por valores válidos

- [ ] **Todos os placeholders substituídos por valores válidos (apenas no YAML)**
  - ⚠️ **NÃO expor valores reais em documentação Markdown**
  - Usar FQDNs Kubernetes: `http://<SERVICE>.<NS>.svc.cluster.local:<PORT>`

- [ ] **Namespace alvo (`global.namespace`) definido corretamente**
  - Padrão: `trisla`
  - Verificar: Namespace existe ou será criado durante deploy

- [ ] **Registry de imagens configurado**
  - Verificar: `global.imageRegistry` aponta para GHCR correto
  - Formato: `ghcr.io/<GHCR_USER>`

### 3.2 Validação de Helm Chart

- [ ] **Helm chart validado**
  ```bash
  helm lint ./helm/trisla
  helm template trisla ./helm/trisla -f ./helm/trisla/values-production.yaml --debug
  ```

- [ ] **Nenhum erro crítico no template**
  - Verificar: Saída do `helm template` não contém erros
  - Verificar: Todos os recursos Kubernetes gerados são válidos

---

## 4. Imagens e Registro

### 4.1 Auditoria GHCR

- [ ] **`docs/IMAGES_GHCR_MATRIX.md` revisado**
  - Executar: `python3 scripts/audit_ghcr_images.py`
  - Revisar: Status de cada imagem

- [ ] **`scripts/audit_ghcr_images.py` executado sem falhas críticas**
  - Verificar: Script executa sem erros
  - Verificar: Relatório gerado em `docs/IMAGES_GHCR_MATRIX.md`

- [ ] **Nenhuma imagem crítica marcada como FALTANDO**
  - Imagens críticas: SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer, NASP Adapter
  - Imagem opcional: UI Dashboard

### 4.2 Secret GHCR

- [ ] **Secret GHCR criado no namespace alvo**
  ```bash
  kubectl create secret docker-registry ghcr-secret \
    --docker-server=ghcr.io \
    --docker-username=<GHCR_USER> \
    --docker-password=<GHCR_TOKEN> \
    --namespace=<TRISLA_NAMESPACE>
  ```

- [ ] **Secret configurado no Helm chart**
  - Verificar: `imagePullSecrets` configurado nos Deployments
  - Verificar: Secret referenciado corretamente

---

## 5. Segurança e Conformidade

### 5.1 Sem Tokens ou Segredos em Arquivos Públicos

- [ ] **Sem tokens ou segredos em arquivos `.md` públicos**
  - Verificar: Nenhum token hardcoded em `docs/`
  - Verificar: Nenhum token hardcoded em `README*.md`

- [ ] **`TriSLA_PROMPTS/` continua ignorado pelo Git**
  - Verificar: `.gitignore` contém `TriSLA_PROMPTS/`
  - Verificar: Nenhum arquivo de `TriSLA_PROMPTS/` foi commitado

### 5.2 Scripts Internos

- [ ] **Scripts internos de limpeza e backup revisados**
  - Verificar: Scripts não expõem informações sensíveis
  - Verificar: Scripts são executáveis e bem documentados

### 5.3 Network Policies (Opcional)

- [ ] **Network Policies configuradas (se aplicável)**
  - Verificar: Políticas de rede definidas no Helm chart
  - Verificar: Comunicação entre módulos permitida

---

## 6. Ansible e Automação

### 6.1 Inventory

- [ ] **`ansible/inventory.yaml` configurado**
  - Verificar: Nodes NASP definidos (usando placeholders em docs)
  - Verificar: Variáveis de grupo configuradas

### 6.2 Playbooks

- [ ] **Playbooks revisados e atualizados**
  - `ansible/playbooks/pre-flight.yml` — Validações pré-deploy
  - `ansible/playbooks/setup-namespace.yml` — Criação de namespace
  - `ansible/playbooks/deploy-trisla-nasp.yml` — Deploy Helm
  - `ansible/playbooks/validate-cluster.yml` — Validação pós-deploy

### 6.3 Teste de Playbooks

- [ ] **Playbooks testados (dry-run)**
  ```bash
  ansible-playbook -i ansible/inventory.yaml ansible/playbooks/pre-flight.yml --check
  ```

---

## 7. Documentação

### 7.1 Documentos Criados

- [ ] **`docs/NASP_CONTEXT_REPORT.md` gerado**
  - Executar: `scripts/discover_nasp_endpoints.sh`
  - Revisar: Relatório não contém IPs reais

- [ ] **`docs/VALUES_PRODUCTION_GUIDE.md` revisado**
  - Verificar: Guia completo e claro
  - Verificar: Exemplos usam placeholders

- [ ] **`docs/IMAGES_GHCR_MATRIX.md` atualizado**
  - Executar: `python3 scripts/audit_ghcr_images.py`
  - Revisar: Status de imagens atualizado

- [ ] **`docs/NASP_DEPLOY_RUNBOOK.md` revisado**
  - Verificar: Runbook completo e seguível
  - Verificar: Comandos não expõem IPs reais

### 7.2 READMEs Atualizados

- [ ] **`README_OPERATIONS_PROD.md` atualizado**
  - Verificar: Seção sobre NASP adicionada
  - Verificar: Links para documentos em `docs/`

- [ ] **`DEVELOPER_GUIDE.md` atualizado**
  - Verificar: Seção sobre integração NASP adicionada
  - Verificar: Diferenças entre local e NASP documentadas

---

## 8. Checklist Final

- [ ] Todos os itens acima marcados como concluídos
- [ ] Nenhum IP real em documentação Markdown
- [ ] `values-production.yaml` preenchido e validado
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

3. **Validação Pós-Deploy:**
   - Executar `ansible/playbooks/validate-cluster.yml`
   - Verificar health checks de todos os módulos

---

**Status do Checklist:** ⬜ Não iniciado | 🟡 Em progresso | ✅ Concluído

**Data de Conclusão:** _______________

**Operador Responsável:** _______________

---

**Versão:** 2.0  
**Data:** 2025-11-22  
**ENGINE MASTER:** Sistema de Pré-Deploy TriSLA


