# Runbook de Deploy NASP — TriSLA

**Versão:** 1.0  
**Data:** 2025-11-22  
**Objetivo:** Guia operacional completo para deploy controlado do TriSLA no ambiente NASP (2 nodes)

---

## Visão Geral

Este runbook descreve como realizar um **deploy controlado** do TriSLA no ambiente NASP (cluster Kubernetes com 2 nodes), a partir de um repositório já sanitizado e validado localmente.

O processo é dividido em etapas sequenciais, cada uma com validações específicas, garantindo que o deploy seja realizado de forma segura e auditável.

**Pré-requisito:** Todas as Fases 1-6 concluídas, incluindo validação E2E local e auditoria técnica v2 aprovada.

---

## Pré-requisitos Absolutos

Antes de iniciar o deploy, certifique-se de que:

- ✅ Checklist de pré-deploy concluído: `docs/NASP_PREDEPLOY_CHECKLIST_v2.md`
- ✅ Cluster NASP operacional com 2 nodes
- ✅ `kubectl` configurado e conectado ao cluster
- ✅ `helm` instalado (versão ≥ 3.12)
- ✅ `ansible` instalado (versão ≥ 2.14)
- ✅ Acesso ao GHCR configurado (token e secret criado)
- ✅ Endpoints NASP descobertos e documentados

**Referência completa:** `docs/NASP_PREDEPLOY_CHECKLIST_v2.md`

---

## Fluxo de Execução Recomendado

### Passo 1: Descoberta de Endpoints NASP

**Objetivo:** Identificar serviços NASP relevantes sem expor IPs reais.

**Execução:**
```bash
# No node1 do NASP (executar localmente)
cd ~/gtp5g/trisla
./scripts/discover-nasp-endpoints.sh
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file

**Validação:**
- [ ] Arquivo `tmp/nasp_context_raw.txt` gerado
- [ ] Arquivo `docs/NASP_CONTEXT_REPORT.md` atualizado
- [ ] Serviços relevantes identificados (Prometheus, Grafana, Kafka, NASP Adapter, etc.)

**Próximo passo:** Revisar `docs/NASP_CONTEXT_REPORT.md` e identificar endpoints necessários.

---

### Passo 2: Revisar Relatório de Contexto

**Objetivo:** Entender o ambiente NASP antes de configurar o TriSLA.

**Execução:**
```bash
# Revisar relatório gerado
cat docs/NASP_CONTEXT_REPORT.md
cat tmp/nasp_context_raw.txt
```

**Validação:**
- [ ] Namespaces relevantes identificados
- [ ] Serviços NASP mapeados (RAN, Transport, Core)
- [ ] Problemas de saúde identificados (se houver)

**Próximo passo:** Preencher `values-nasp.yaml` com endpoints descobertos.

---

### Passo 3: Preencher values-nasp.yaml

**Objetivo:** Configurar valores de produção específicos do ambiente NASP.

**Execução (método guiado):**
```bash
cd ~/gtp5g/trisla
./scripts/fill_values_production.sh
```

**Ou manualmente:**
1. Editar `helm/trisla/values-nasp.yaml`
2. Seguir guia: `docs/deployment/VALUES_PRODUCTION_GUIDE.md`
3. Substituir todos os placeholders `<...>` por valores reais

**Validação:**
```bash
# Validar sintaxe e valores
helm template trisla ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

**Checklist:**
- [ ] Todos os placeholders substituídos
- [ ] Endpoints usando FQDNs Kubernetes (não IPs)
- [ ] Nenhum token hardcoded (usar Kubernetes Secrets)
- [ ] Validação `helm template` sem erros críticos

**Próximo passo:** Auditar imagens GHCR.

---

### Passo 4: Auditar Imagens GHCR

**Objetivo:** Verificar se todas as imagens necessárias estão disponíveis no GHCR.

**Execução:**
```bash
# Executar auditoria
python3 scripts/audit_ghcr_images.py
```

**Validação:**
- [ ] Relatório gerado em `docs/IMAGES_GHCR_MATRIX.md`
- [ ] Todas as imagens críticas marcadas como OK
- [ ] Nenhuma imagem crítica marcada como FALTANDO

**Se imagens faltando:**
1. Buildar imagens faltantes
2. Publicar no GHCR
3. Reexecutar auditoria

**Próximo passo:** Executar pre-flight checks via Ansible.

---

### Passo 5: Pre-Flight Checks (Ansible)

**Objetivo:** Validar que o cluster NASP está pronto para receber o TriSLA.

**Execução:**
```bash
cd ansible
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml
```

**Validação esperada:**
- ✅ Kubernetes versão ≥ 1.26
- ✅ Helm instalado e funcional
- ✅ Calico operacional
- ✅ StorageClass disponível
- ✅ Namespace `trisla` pode ser criado

**Se falhas:**
- Revisar erros reportados
- Corrigir problemas de infraestrutura
- Reexecutar pre-flight

**Próximo passo:** Criar namespace e secrets.

---

### Passo 6: Setup de Namespace e Secrets

**Objetivo:** Criar namespace e configurar secrets necessários.

**Execução:**
```bash
# Criar namespace
ansible-playbook -i inventory.yaml playbooks/setup-namespace.yml

# Criar secret GHCR (se ainda não criado)
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GHCR_USER> \
  --docker-password=<GHCR_TOKEN> \
  --namespace=trisla
```

**Validação:**
```bash
# Verificar namespace
kubectl get namespace trisla

# Verificar secret
kubectl get secret ghcr-secret -n trisla
```

**Próximo passo:** Deploy do TriSLA via Helm.

---

### Passo 7: Deploy TriSLA com Helm

**Objetivo:** Instalar o TriSLA no cluster NASP usando Helm.

**Execução:**
```bash
# Deploy via Ansible (recomendado)
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml

# OU manualmente
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  -f ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

**Validação:**
```bash
# Verificar pods
kubectl get pods -n trisla

# Verificar serviços
kubectl get svc -n trisla

# Verificar deployments
kubectl get deployments -n trisla
```

**Aguardar:**
- Todos os pods em status `Running`
- Readiness probes passando
- Liveness probes passando

**Próximo passo:** Validação pós-deploy.

---

### Passo 8: Validação Pós-Deploy

**Objetivo:** Confirmar que o TriSLA está operacional após o deploy.

**Execução:**
```bash
# Validação via Ansible
ansible-playbook -i inventory.yaml playbooks/validate-cluster.yml

# OU validação manual
kubectl get pods -n trisla
kubectl get svc -n trisla
```

**Health Checks:**
```bash
# SEM-CSMF
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080 &
curl http://localhost:8080/health

# ML-NSMF
kubectl port-forward -n trisla svc/trisla-ml-nsmf 8081:8081 &
curl http://localhost:8081/health

# Decision Engine
kubectl port-forward -n trisla svc/trisla-decision-engine 8082:8082 &
curl http://localhost:8082/health

# BC-NSSMF
kubectl port-forward -n trisla svc/trisla-bc-nssmf 8083:8083 &
curl http://localhost:8083/health

# SLA-Agent Layer
kubectl port-forward -n trisla svc/trisla-sla-agent-layer 8084:8084 &
curl http://localhost:8084/health

# NASP Adapter
kubectl port-forward -n trisla svc/trisla-nasp-adapter 8085:8085 &
curl http://localhost:8085/health
```

**Validação de Kafka Topics:**
```bash
# Listar tópicos (se Kafka estiver no cluster)
kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
  kafka-topics --list --bootstrap-server localhost:9092
```

**Próximo passo:** Verificar observabilidade.

---

### Passo 9: Verificar Observabilidade

**Objetivo:** Confirmar que métricas e traces estão sendo coletados.

**Execução:**
```bash
# Prometheus
kubectl port-forward -n monitoring svc/<PROMETHEUS_SERVICE> 9090:9090
# Acessar http://localhost:9090

# Grafana
kubectl port-forward -n monitoring svc/<GRAFANA_SERVICE> 3000:3000
# Acessar http://localhost:3000 (admin/admin)
```

**Validação:**
- [ ] Métricas TriSLA visíveis no Prometheus
  - `trisla_intents_total`
  - `trisla_decisions_total`
  - `trisla_sla_registrations_total`
- [ ] Dashboards Grafana carregados (se configurados)
- [ ] Traces OTLP sendo coletados

---

## Rollback

### Comandos de Rollback

**Ver histórico de releases:**
```bash
helm history trisla -n <TRISLA_NAMESPACE>
```

**Rollback para revisão anterior:**
```bash
helm rollback trisla <REVISION> -n <TRISLA_NAMESPACE>
```

**Rollback para versão específica:**
```bash
helm rollback trisla 1 -n <TRISLA_NAMESPACE>  # Volta para primeira instalação
```

**Desinstalar completamente (último recurso):**
```bash
helm uninstall trisla -n <TRISLA_NAMESPACE>
```

---

## Validação Pós-Deploy

### Teste E2E no Cluster NASP

**Adaptar teste E2E local para ambiente NASP:**

1. **Criar intent de teste:**
   ```bash
   kubectl run -it --rm test-client --image=curlimages/curl --restart=Never -- \
     curl -X POST http://trisla-sem-csmf.trisla.svc.cluster.local:8080/api/v1/intents \
       -H "Content-Type: application/json" \
       -d '{
         "intent_id": "test-urllc-001",
         "tenant_id": "test-tenant",
         "service_type": "URLLC",
         "sla_requirements": {
           "latency": "5ms",
           "throughput": "10Mbps",
           "reliability": 0.99999
         }
       }'
   ```

2. **Verificar mensagens Kafka (I-02):**
   ```bash
   kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
     kafka-console-consumer \
       --bootstrap-server localhost:9092 \
       --topic I-02-intent-to-ml \
       --from-beginning \
       --max-messages 1
   ```

3. **Verificar mensagens Kafka (I-03):**
   ```bash
   kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
     kafka-console-consumer \
       --bootstrap-server localhost:9092 \
       --topic I-03-ml-predictions \
       --from-beginning \
       --max-messages 1
   ```

4. **Verificar mensagens Kafka (I-04):**
   ```bash
   kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
     kafka-console-consumer \
       --bootstrap-server localhost:9092 \
       --topic trisla-i04-decisions \
       --from-beginning \
       --max-messages 1
   ```

5. **Verificar mensagens Kafka (I-06):**
   ```bash
   kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
     kafka-console-consumer \
       --bootstrap-server localhost:9092 \
       --topic trisla-i06-agent-events \
       --from-beginning \
       --max-messages 1
   ```

3. **Verificar registro na blockchain:**
   ```bash
   kubectl logs -n trisla <bc-nssmf-pod> | grep "SLA registrado"
   ```

### Comandos de Diagnóstico

**Ver logs de todos os módulos:**
```bash
# Logs de um módulo específico
kubectl logs -n trisla -l app.kubernetes.io/name=trisla-sem-csmf --tail=100

# Logs de todos os pods TriSLA
kubectl logs -n trisla -l app.kubernetes.io/part-of=trisla --tail=50
```

**Ver eventos do namespace:**
```bash
kubectl get events -n trisla --sort-by='.lastTimestamp'
```

**Ver recursos criados:**
```bash
kubectl get all -n trisla
```

---

## Troubleshooting

### Problemas Comuns

#### 1. Pods em ImagePullBackOff

**Causa:** Imagem não encontrada ou secret GHCR incorreto.

**Solução:**
```bash
# Verificar secret
kubectl get secret ghcr-secret -n trisla

# Verificar se imagem existe
docker pull ghcr.io/<GHCR_USER>/trisla-sem-csmf:latest

# Recriar secret se necessário
kubectl delete secret ghcr-secret -n trisla
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GHCR_USER> \
  --docker-password=<GHCR_TOKEN> \
  --namespace=trisla
```

#### 2. Pods em CrashLoopBackOff

**Causa:** Erro na aplicação ou configuração incorreta.

**Solução:**
```bash
# Ver logs
kubectl logs -n trisla <pod-name> --previous

# Ver eventos
kubectl describe pod -n trisla <pod-name>
```

#### 3. Serviços não acessíveis

**Causa:** Network Policies ou configuração de rede incorreta.

**Solução:**
```bash
# Verificar Network Policies
kubectl get networkpolicies -n trisla

# Testar conectividade entre pods
kubectl exec -n trisla <pod-1> -- ping <pod-2-ip>
```

#### 4. Kafka topics não criados

**Causa:** Kafka não configurado ou tópicos não criados automaticamente.

**Solução:**
```bash
# Criar tópicos manualmente
kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
  kafka-topics --create \
    --topic I-02-intent-to-ml \
    --bootstrap-server localhost:9092 \
    --if-not-exists \
    --partitions 1 \
    --replication-factor 1
```

---

## Sequência Recomendada de Uso

1. **Preparação:**
   - Executar `scripts/discover_nasp_endpoints.sh`
   - Revisar `docs/NASP_CONTEXT_REPORT.md`
   - Preencher `values-nasp.yaml` com `scripts/fill_values_production.sh`

2. **Validação:**
   - Executar `python3 scripts/audit_ghcr_images.py`
   - Revisar `docs/IMAGES_GHCR_MATRIX.md`
   - Validar `values-nasp.yaml` com `helm template`

3. **Deploy:**
   - Executar `ansible-playbook -i inventory.yaml playbooks/pre-flight.yml`
   - Executar `ansible-playbook -i inventory.yaml playbooks/setup-namespace.yml`
   - Executar `ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml`

4. **Validação Pós-Deploy:**
   - Executar `ansible-playbook -i inventory.yaml playbooks/validate-cluster.yml`
   - Verificar health checks de todos os módulos
   - Verificar observabilidade (Prometheus/Grafana)

---

## Referências

- **Checklist de Pré-Deploy:** `docs/NASP_PREDEPLOY_CHECKLIST_v2.md`
- **Guia de Valores:** `docs/VALUES_PRODUCTION_GUIDE.md`
- **Matriz de Imagens:** `docs/IMAGES_GHCR_MATRIX.md`
- **Relatório de Contexto:** `docs/NASP_CONTEXT_REPORT.md`
- **Operações em Produção:** `README_OPERATIONS_PROD.md`

---

**Versão:** 1.0  
**Data:** 2025-11-22  
**ENGINE MASTER:** Sistema de Deploy NASP TriSLA


