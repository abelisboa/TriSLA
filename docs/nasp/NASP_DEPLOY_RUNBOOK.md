# Runbook de Deploy NASP — TriSLA

**Versão:** 1.0  
**Data:** 2025-11-22  
**objective:** guide operacional completo for deploy controlado of TriSLA in the NASP environment (2 nodes)

---

## Visão Geral

This runbook descreve como realizar um **deploy controlado** of TriSLA in the NASP environment (cluster Kubernetes com 2 nodes), a partir de um repositório já sanitizado e validado localmente.

O processo is dividido in etapas sequenciais, cada uma com validações específicas, garantindo que o deploy seja realizado de forma segura e auditável.

**Pré-requisito:** Todas as Fases 1-6 concluídas, incluindo validation E2E local e audit técnica v2 aprovada.

---

## Pré-requisitos Absolutos

Antes de start o deploy, certifique-se de que:

- ✅ Checklist de pré-deploy concluído: `docs/NASP_PREDEPLOY_CHECKLIST_v2.md`
- ✅ Cluster NASP operacional com 2 nodes
- ✅ `kubectl` configured e conectado ao cluster
- ✅ `helm` instalado (versão ≥ 3.12)
- ✅ `ansible` instalado (versão ≥ 2.14)
- ✅ Acesso ao GHCR configured (token e secret criado)
- ✅ Endpoints NASP descobertos e documentados

**Referência completa:** `docs/NASP_PREDEPLOY_CHECKLIST_v2.md`

---

## Fluxo de Execução Recomendado

### Passo 1: Descoberta de Endpoints NASP

**objective:** Identificar serviços NASP relevantes sem expor IPs reais.

**Execução:**
```bash
# No node1 of NASP (executar localmente)
cd ~/gtp5g/trisla
./scripts/discover-nasp-endpoints.sh
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file

**validation:**
- [ ] Arquivo `tmp/nasp_context_raw.txt` gerado
- [ ] Arquivo `docs/NASP_CONTEXT_REPORT.md` atualizado
- [ ] Services relevantes identificados (Prometheus, Grafana, Kafka, NASP Adapter, etc.)

**Próximo passo:** Revisar `docs/NASP_CONTEXT_REPORT.md` e identificar endpoints necessários.

---

### Passo 2: Revisar Relatório de Contexto

**objective:** Entender o environment NASP antes de configure o TriSLA.

**Execução:**
```bash
# Revisar relatório gerado
cat docs/NASP_CONTEXT_REPORT.md
cat tmp/nasp_context_raw.txt
```

**validation:**
- [ ] Namespaces relevantes identificados
- [ ] Services NASP mapeados (RAN, Transport, Core)
- [ ] problems de saúde identificados (se houver)

**Próximo passo:** Preencher `values-nasp.yaml` com endpoints descobertos.

---

### Passo 3: Preencher values-nasp.yaml

**objective:** configure valores de production específicos of environment NASP.

**Execução (método guiado):**
```bash
cd ~/gtp5g/trisla
./scripts/fill_values_production.sh
```

**Ou manualmente:**
1. Editar `helm/trisla/values-nasp.yaml`
2. Seguir guide: `docs/deployment/VALUES_PRODUCTION_GUIDE.md`
3. Substituir todos os placeholders `<...>` por valores reais

**validation:**
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
- [ ] validation `helm template` sem erros críticos

**Próximo passo:** Auditar imagens GHCR.

---

### Passo 4: Auditar Imagens GHCR

**objective:** Verifiesr se todas as imagens necessárias estão disponíveis no GHCR.

**Execução:**
```bash
# Verifiesr imagens GHCR disponíveis
# Revisar: docs/ghcr/IMAGES_GHCR_MATRIX.md
# Testar pull de imagens críticas:
docker pull ghcr.io/abelisboa/trisla-sem-csmf:latest
docker pull ghcr.io/abelisboa/trisla-ml-nsmf:latest
docker pull ghcr.io/abelisboa/trisla-decision-engine:latest
docker pull ghcr.io/abelisboa/trisla-bc-nssmf:latest
docker pull ghcr.io/abelisboa/trisla-sla-agent-layer:latest
docker pull ghcr.io/abelisboa/trisla-nasp-adapter:latest
docker pull ghcr.io/abelisboa/trisla-ui-dashboard:latest
```

**validation:**
- [ ] Matriz de imagens revisada in `docs/ghcr/IMAGES_GHCR_MATRIX.md`
- [ ] Todas as imagens críticas podem ser puxadas of GHCR
- [ ] Nenhuma imagem crítica retorna error ao fazer pull

**Se imagens faltando:**
1. Buildar imagens faltantes usando Dockerfiles in `apps/<module>/`
2. Publicar no GHCR manualmente ou via CI/CD
3. Validar que imagens estão acessíveis

**Próximo passo:** Executar pre-flight checks via Ansible.

---

### Passo 5: Pre-Flight Checks (Ansible)

**objective:** Validar que o cluster NASP está pronto for receber o TriSLA.

**Execução:**
```bash
cd ansible
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml
```

**validation expected:**
- ✅ Kubernetes versão ≥ 1.26
- ✅ Helm instalado e funcional
- ✅ Calico operacional
- ✅ StorageClass disponível
- ✅ Namespace `trisla` pode ser criado

**Se falhas:**
- Revisar erros reportados
- Corrigir problems de infraestrutura
- Reexecutar pre-flight

**Próximo passo:** Criar namespace e secrets.

---

### Passo 6: Setup de Namespace e Secrets

**objective:** Criar namespace e configure secrets necessários.

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

**validation:**
```bash
# Verifiesr namespace
kubectl get namespace trisla

# Verifiesr secret
kubectl get secret ghcr-secret -n trisla
```

**Próximo passo:** Deploy of TriSLA via Helm.

---

### Passo 7: Deploy TriSLA com Helm

**objective:** Instalar o TriSLA no cluster NASP usando Helm.

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

**validation:**
```bash
# Verifiesr pods
kubectl get pods -n trisla

# Verifiesr serviços
kubectl get svc -n trisla

# Verifiesr deployments
kubectl get deployments -n trisla
```

**Waitsr:**
- Todos os pods in status `Running`
- Readiness probes passando
- Liveness probes passando

**Próximo passo:** validation pós-deploy.

---

### Passo 8: validation Pós-Deploy

**objective:** Confirmar que o TriSLA está operacional após o deploy.

**Execução:**
```bash
# validation via Ansible
ansible-playbook -i inventory.yaml playbooks/validate-cluster.yml

# OU validation manual
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

**validation de Kafka Topics:**
```bash
# Listar tópicos (se Kafka estiver no cluster)
kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
  kafka-topics --list --bootstrap-server localhost:9092
```

**Próximo passo:** Verifiesr observabilidade.

---

### Passo 9: Verifiesr Observabilidade

**objective:** Confirmar que metrics e traces estão sendo coletados.

**Execução:**
```bash
# Prometheus
kubectl port-forward -n monitoring svc/<PROMETHEUS_SERVICE> 9090:9090
# Acessar http://localhost:9090

# Grafana
kubectl port-forward -n monitoring svc/<GRAFANA_SERVICE> 3000:3000
# Acessar http://localhost:3000 (admin/admin)
```

**validation:**
- [ ] metrics TriSLA visíveis no Prometheus
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

**Rollback for revisão anterior:**
```bash
helm rollback trisla <REVISION> -n <TRISLA_NAMESPACE>
```

**Rollback for versão específica:**
```bash
helm rollback trisla 1 -n <TRISLA_NAMESPACE>  # Volta for primeira instalação
```

**Desinstalar completamente (último recurso):**
```bash
helm uninstall trisla -n <TRISLA_NAMESPACE>
```

---

## validation Pós-Deploy

### Teste E2E no Cluster NASP

**Adaptar teste E2E local for environment NASP:**

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

2. **Verifiesr mensagens Kafka (I-02):**
   ```bash
   kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
     kafka-console-consumer \
       --bootstrap-server localhost:9092 \
       --topic I-02-intent-to-ml \
       --from-beginning \
       --max-messages 1
   ```

3. **Verifiesr mensagens Kafka (I-03):**
   ```bash
   kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
     kafka-console-consumer \
       --bootstrap-server localhost:9092 \
       --topic I-03-ml-predictions \
       --from-beginning \
       --max-messages 1
   ```

4. **Verifiesr mensagens Kafka (I-04):**
   ```bash
   kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
     kafka-console-consumer \
       --bootstrap-server localhost:9092 \
       --topic trisla-i04-decisions \
       --from-beginning \
       --max-messages 1
   ```

5. **Verifiesr mensagens Kafka (I-06):**
   ```bash
   kubectl exec -n <KAFKA_NS> <kafka-pod> -- \
     kafka-console-consumer \
       --bootstrap-server localhost:9092 \
       --topic trisla-i06-agent-events \
       --from-beginning \
       --max-messages 1
   ```

3. **Verifiesr registro na blockchain:**
   ```bash
   kubectl logs -n trisla <bc-nssmf-pod> | grep "SLA registrado"
   ```

### Comandos de Diagnóstico

**Ver logs de todos os módulos:**
```bash
# Logs de um Module específico
kubectl logs -n trisla -l app.kubernetes.io/name=trisla-sem-csmf --tail=100

# Logs de todos os pods TriSLA
kubectl logs -n trisla -l app.kubernetes.io/part-of=trisla --tail=50
```

**Ver eventos of namespace:**
```bash
kubectl get events -n trisla --sort-by='.lastTimestamp'
```

**Ver recursos criados:**
```bash
kubectl get all -n trisla
```

---

## Troubleshooting

### problems Comuns

#### 1. Pods in ImagePullBackOff

**Causa:** Imagem não encontrada ou secret GHCR incorreto.

**solution:**
```bash
# Verifiesr secret
kubectl get secret ghcr-secret -n trisla

# Verifiesr se imagem existe
docker pull ghcr.io/<GHCR_USER>/trisla-sem-csmf:latest

# Recriar secret se necessário
kubectl delete secret ghcr-secret -n trisla
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GHCR_USER> \
  --docker-password=<GHCR_TOKEN> \
  --namespace=trisla
```

#### 2. Pods in CrashLoopBackOff

**Causa:** error in application or configuration incorreta.

**solution:**
```bash
# Ver logs
kubectl logs -n trisla <pod-name> --previous

# Ver eventos
kubectl describe pod -n trisla <pod-name>
```

#### 3. Services não acessíveis

**Causa:** Network Policies or configuration de rede incorreta.

**solution:**
```bash
# Verifiesr Network Policies
kubectl get networkpolicies -n trisla

# Testar conectividade entre pods
kubectl exec -n trisla <pod-1> -- ping <pod-2-ip>
```

#### 4. Kafka topics não criados

**Causa:** Kafka not configured ou tópicos não criados automaticamente.

**solution:**
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
   - Executar `scripts/discover-nasp-endpoints.sh`
   - Revisar `docs/nasp/NASP_CONTEXT_REPORT.md`
   - Preencher `values-nasp.yaml` com `scripts/fill_values_production.sh`

2. **validation:**
   - Revisar `docs/ghcr/IMAGES_GHCR_MATRIX.md` e validar que imagens podem ser puxadas
   - Revisar `docs/IMAGES_GHCR_MATRIX.md`
   - Validar `values-nasp.yaml` com `helm template`

3. **Deploy:**
   - Executar `ansible-playbook -i inventory.yaml playbooks/pre-flight.yml`
   - Executar `ansible-playbook -i inventory.yaml playbooks/setup-namespace.yml`
   - Executar `ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml`

4. **validation Pós-Deploy:**
   - Executar `ansible-playbook -i inventory.yaml playbooks/validate-cluster.yml`
   - Verifiesr health checks de todos os módulos
   - Verifiesr observabilidade (Prometheus/Grafana)

---

## Referências

- **Checklist de Pré-Deploy:** `docs/NASP_PREDEPLOY_CHECKLIST_v2.md`
- **guide de Valores:** `docs/VALUES_PRODUCTION_GUIDE.md`
- **Matriz de Imagens:** `docs/IMAGES_GHCR_MATRIX.md`
- **Relatório de Contexto:** `docs/NASP_CONTEXT_REPORT.md`
- **Operações in production:** `README_OPERATIONS_PROD.md`

---

**Versão:** 1.0  
**Data:** 2025-11-22  
**ENGINE MASTER:** Sistema de Deploy NASP TriSLA


