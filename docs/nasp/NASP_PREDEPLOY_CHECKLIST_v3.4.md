# TriSLA v3.4.0 - NASP Pre-Deploy Checklist

**Versão:** 3.4.0  
**Data:** 2025-01-22  
**Ambiente:** NASP Cluster

---

## 📋 Checklist Completo de Pré-Deploy

Use este checklist antes de iniciar o deploy do TriSLA v3.4.0 no ambiente NASP.

---

## 1. Infraestrutura NASP

### 1.1 Cluster Kubernetes

- [ ] Cluster com mínimo 2 nodes operacionais
- [ ] Nodes visíveis via `kubectl get nodes`
- [ ] CNI configurado e saudável (Calico recomendado)
- [ ] StorageClass disponível
- [ ] Ingress Controller instalado (Nginx recomendado)

### 1.2 Acesso e Permissões

- [ ] Acesso SSH aos nodes configurado
- [ ] `kubectl` configurado e funcionando
- [ ] Permissões de deploy no namespace `trisla`
- [ ] Acesso ao GHCR configurado

---

## 2. TriSLA - Dependências Técnicas

### 2.1 Módulos e Artefatos

- [ ] Ontologia `trisla.owl` presente no container SEM-CSMF
- [ ] Modelo ML (`viability_model.pkl` + `scaler`) presente no ML-NSMF
- [ ] Contrato Solidity deployado no GoQuorum/Besu
- [ ] Configuração do BC-NSSMF aponta para RPC correto
- [ ] Agentes SLA configurados para NASP Adapter

### 2.2 Imagens Docker

- [ ] Todas as 7 imagens GHCR validadas:
  - [ ] `ghcr.io/abelisboa/trisla-sem-csmf:3.4.0`
  - [ ] `ghcr.io/abelisboa/trisla-ml-nsmf:3.4.0`
  - [ ] `ghcr.io/abelisboa/trisla-decision-engine:3.4.0`
  - [ ] `ghcr.io/abelisboa/trisla-bc-nssmf:3.4.0`
  - [ ] `ghcr.io/abelisboa/trisla-sla-agent-layer:3.4.0`
  - [ ] `ghcr.io/abelisboa/trisla-nasp-adapter:3.4.0`
  - [ ] `ghcr.io/abelisboa/trisla-ui-dashboard:3.4.0`

### 2.3 Dependências Externas

- [ ] Kafka disponível no cluster (ou namespace configurado)
- [ ] PostgreSQL disponível (ou namespace configurado)
- [ ] Besu/GoQuorum disponível (se BC-NSSMF usar blockchain)
- [ ] Prometheus disponível para métricas
- [ ] Grafana disponível para dashboards

---

## 3. Configuração de Helm

### 3.1 Values File

- [ ] `nasp/values-nasp.yaml` preenchido conforme guia
- [ ] Todos os placeholders substituídos por valores válidos
- [ ] Namespace alvo (`global.namespace`) definido corretamente
- [ ] Tags de imagens definidas como `3.4.0`

### 3.2 Validação

- [ ] `helm lint helm/trisla -f nasp/values-nasp.yaml` sem erros
- [ ] `helm template helm/trisla -f nasp/values-nasp.yaml` gera YAML válido
- [ ] Valores de recursos (CPU/Memory) adequados ao cluster

---

## 4. Imagens e Registro

### 4.1 GHCR

- [ ] `docs/ghcr/IMAGES_GHCR_MATRIX.md` revisado
- [ ] `scripts/audit_ghcr_images.py` executado sem falhas críticas
- [ ] Nenhuma imagem crítica marcada como FALTANDO
- [ ] SHA256 das imagens documentadas em `docs/ghcr/IMAGES_V3.4.0_SHA256.json`

### 4.2 Secrets

- [ ] Secret do GHCR criado no namespace `trisla`
- [ ] Secret do PostgreSQL configurado (se necessário)
- [ ] Secret JWT configurado para autenticação

---

## 5. NASP Endpoints

### 5.1 Descoberta de Endpoints

- [ ] Script `scripts/discover_nasp_endpoints.sh` executado
- [ ] `docs/NASP_CONTEXT_REPORT.md` revisado
- [ ] Endpoints RAN identificados e configurados
- [ ] Endpoints Transport identificados e configurados
- [ ] Endpoints Core (UPF, AMF, SMF) identificados e configurados

### 5.2 Configuração

- [ ] `naspAdapter.naspEndpoints.*` preenchidos em `values-nasp.yaml`
- [ ] Endpoints testados e acessíveis
- [ ] Autenticação NASP configurada (se necessário)

---

## 6. Segurança e Conformidade

### 6.1 Segredos

- [ ] Sem tokens ou segredos em arquivos `.md` públicos
- [ ] `TriSLA_PROMPTS/` continua ignorado pelo Git
- [ ] Scripts internos de limpeza revisados

### 6.2 Network Policies

- [ ] NetworkPolicies definidas (se necessário)
- [ ] Regras de firewall verificadas
- [ ] Portas necessárias abertas

---

## 7. Ansible e Automação

### 7.1 Inventory

- [ ] `ansible/inventory-nasp.yaml` configurado
- [ ] IPs e credenciais SSH configurados (não versionados)
- [ ] Variáveis de ambiente definidas

### 7.2 Playbooks

- [ ] `ansible/playbooks/pre-flight.yml` revisado
- [ ] `ansible/playbooks/setup-namespace.yml` revisado
- [ ] `ansible/playbooks/deploy-trisla-nasp.yml` revisado
- [ ] `ansible/playbooks/validate-cluster.yml` revisado

---

## 8. Documentação

### 8.1 Runbooks

- [ ] `NASP_DEPLOY_RUNBOOK_v3.4.md` revisado
- [ ] Procedimentos operacionais documentados
- [ ] Comandos de rollback documentados

### 8.2 Guias

- [ ] `docs/deployment/VALUES_PRODUCTION_GUIDE.md` consultado
- [ ] `docs/nasp/NASP_DEPLOY_GUIDE.md` consultado
- [ ] Troubleshooting guides disponíveis

---

## 9. Testes e Validação

### 9.1 Testes Locais

- [ ] Testes E2E locais executados com sucesso
- [ ] Validação de interfaces I-01 a I-07 concluída
- [ ] Testes de integração passando

### 9.2 Validação de Ambiente

- [ ] Pre-flight checks executados
- [ ] Recursos do cluster suficientes
- [ ] Compatibilidade de versões verificada

---

## 10. Comunicação e Notificações

### 10.1 Stakeholders

- [ ] Equipe de operações notificada
- [ ] Janela de manutenção agendada (se necessário)
- [ ] Plano de rollback comunicado

### 10.2 Monitoramento

- [ ] Alertas configurados
- [ ] Dashboards preparados
- [ ] Logs centralizados configurados

---

## ✅ Validação Final

Antes de prosseguir com o deploy, confirme:

- [ ] Todos os itens acima marcados como concluídos
- [ ] Nenhum bloqueador identificado
- [ ] Equipe preparada para o deploy
- [ ] Plano de rollback testado

---

## 🚀 Próximos Passos

Após completar este checklist:

1. Executar `NASP_DEPLOY_RUNBOOK_v3.4.md`
2. Monitorar deploy em tempo real
3. Validar pós-deploy conforme runbook
4. Documentar quaisquer problemas encontrados

---

**Versão do Checklist:** 3.4.0  
**Última Atualização:** 2025-01-22

