# Checklist de Pré-Deploy NASP Node1 — TriSLA

**Data:** 2025-11-22  
**Versão:** 1.0  
**objective:** Garantir que o TriSLA está pronto for deploy controlado no NASP Node1

---

## 1. Pré-requisitos no NASP Node1/Node2

### 1.1 Kubernetes Cluster

- [ ] **Versão Kubernetes:** ≥ 1.26
- [ ] **CNI:** Calico configured e funcional
- [ ] **StorageClass:** Configurada e funcional
- [ ] **Ingress Controller:** Nginx ou similar configured
- [ ] **RBAC:** Habilitado e configured

**Comandos de validation:**
```bash
kubectl cluster-info
kubectl get nodes
kubectl get storageclass
kubectl get ingressclass
```

### 1.2 Namespaces

- [ ] **Namespace `trisla`:** Criado e configured
- [ ] **Namespace for NASP services:** Identificado e acessível
- [ ] **Network Policies:** configured (se aplicável)

**Comandos:**
```bash
kubectl create namespace trisla
kubectl get namespaces
```

### 1.3 Acesso ao GHCR

- [ ] **Personal Access Token (PAT):** Criado no GitHub com permissões:
  - `read:packages` (para pull de imagens)
  - `write:packages` (se necessário fazer push)
- [ ] **Secret criado no Kubernetes:**
  ```bash
  kubectl create secret docker-registry ghcr-secret \
    --docker-server=ghcr.io \
    --docker-username=<GITHUB_USERNAME> \
    --docker-password=<GITHUB_PAT> \
    --namespace=trisla
  ```

### 1.4 Ferramentas no Operador

- [ ] **kubectl:** installed e configured (versão ≥ 1.26)
- [ ] **Helm:** installed (versão ≥ 3.12)
- [ ] **Acesso local:** Você já está dentro of node1 of NASP
- [ ] **Conectividade:** Testada entre operador e cluster

---

## 2. Descoberta de Endpoints NASP

### 2.1 Identificar Services NASP

Execute o script de descoberta (se disponível):
```bash
./scripts/discover-nasp-services.sh
```

Ou manualmente:
```bash
# Listar serviços RAN
kubectl get svc -n <ran-namespace> | grep -i ran

# Listar serviços Core (UPF, AMF, SMF)
kubectl get svc -n <core-namespace> | grep -E "upf|amf|smf"

# Listar serviços Transport
kubectl get svc -n <transport-namespace> | grep -i transport
```

### 2.2 Documentar Endpoints

Preencher in `helm/trisla/values-nasp.yaml`:

- [ ] **RAN Endpoint:** `http://<RAN_SERVICE>.<RAN_NAMESPACE>.svc.cluster.local:<RAN_PORT>`
- [ ] **RAN Metrics Endpoint:** `http://<RAN_SERVICE>.<RAN_NAMESPACE>.svc.cluster.local:<RAN_METRICS_PORT>`
- [ ] **Core UPF Endpoint:** `http://<UPF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<UPF_PORT>`
- [ ] **Core UPF Metrics Endpoint:** `http://<UPF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<UPF_METRICS_PORT>`
- [ ] **Core AMF Endpoint:** `http://<AMF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<AMF_PORT>`
- [ ] **Core SMF Endpoint:** `http://<SMF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<SMF_PORT>`
- [ ] **Transport Endpoint:** `http://<TRANSPORT_SERVICE>.<TRANSPORT_NAMESPACE>.svc.cluster.local:<TRANSPORT_PORT>`

### 2.3 Testar Conectividade

- [ ] **Testar endpoints NASP:**
  ```bash
  kubectl run -it --rm test-pod --image=curlimages/curl --restart=Never -- \
    curl -v http://<RAN_SERVICE>.<RAN_NAMESPACE>.svc.cluster.local:<RAN_PORT>/health
  ```

---

## 3. Helm Values Configuration

### 3.1 Revisar `values-nasp.yaml`

- [ ] **Substituir placeholders:**
  - `<INTERFACE_NAME>` → Interface real (ex: `my5g`)
  - `<NODE_IP>` → IP of Node1 (ex: `192.168.10.16`)
  - `<GATEWAY_IP>` → Gateway IP (ex: `192.168.10.1`)
  - `<RAN_SERVICE>`, `<RAN_NAMESPACE>`, `<RAN_PORT>` → Valores reais
  - `<UPF_SERVICE>`, `<CORE_NAMESPACE>`, `<UPF_PORT>` → Valores reais
  - `<TRANSPORT_SERVICE>`, `<TRANSPORT_NAMESPACE>`, `<TRANSPORT_PORT>` → Valores reais

- [ ] **Verifiesr imagens GHCR:**
  - Todas as imagens apontam for `ghcr.io/abelisboa/trisla-*:latest` ou versão específica
  - Secret `ghcr-secret` está configured corretamente

- [ ] **variables de environment:**
  - `KAFKA_BOOTSTRAP_SERVERS`: Endpoint Kafka of cluster
  - `OTEL_EXPORTER_OTLP_ENDPOINT`: Endpoint OTLP Collector
  - `BESU_RPC_URL`: Endpoint Besu (se aplicável)
  - `NASP_*_ENDPOINT`: Endpoints NASP descobertos

### 3.2 Validate configuration

```bash
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug
```

---

## 4. Deploy no NASP Node1

### 4.1 Pre-flight Check

- [ ] **Executar pre-flight:**
  ```bash
  ./scripts/pre-flight-check.sh
  ```

- [ ] **Verifiesr recursos disponíveis:**
  ```bash
  kubectl top nodes
  kubectl describe node <node1-name>
  ```

### 4.2 Deploy com Helm

- [ ] **Adicionar repositório Helm (se necessário):**
  ```bash
  helm repo add trisla ./helm/trisla
  helm repo update
  ```

- [ ] **Instalar/Update TriSLA:**
  ```bash
  helm upgrade --install trisla ./helm/trisla \
    --namespace trisla \
    --create-namespace \
    -f ./helm/trisla/values-nasp.yaml \
    --wait \
    --timeout 15m
  ```

### 4.3 Verifiesr Deploy

- [ ] **Verifiesr pods:**
  ```bash
  kubectl get pods -n trisla
  kubectl get pods -n trisla -w  # Watch mode
  ```

- [ ] **Verifiesr serviços:**
  ```bash
  kubectl get svc -n trisla
  ```

- [ ] **Verifiesr deployments:**
  ```bash
  kubectl get deployments -n trisla
  kubectl get statefulsets -n trisla
  ```

---

## 5. validation Pós-Deploy

### 5.1 Health Checks

- [ ] **SEM-CSMF:**
  ```bash
  kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080
  curl http://localhost:8080/health
  ```

- [ ] **ML-NSMF:**
  ```bash
  kubectl port-forward -n trisla svc/trisla-ml-nsmf 8081:8081
  curl http://localhost:8081/health
  ```

- [ ] **Decision Engine:**
  ```bash
  kubectl port-forward -n trisla svc/trisla-decision-engine 8082:8082
  curl http://localhost:8082/health
  ```

- [ ] **BC-NSSMF:**
  ```bash
  kubectl port-forward -n trisla svc/trisla-bc-nssmf 8083:8083
  curl http://localhost:8083/health
  ```

- [ ] **SLA-Agent Layer:**
  ```bash
  kubectl port-forward -n trisla svc/trisla-sla-agent-layer 8084:8084
  curl http://localhost:8084/health
  ```

- [ ] **NASP Adapter:**
  ```bash
  kubectl port-forward -n trisla svc/trisla-nasp-adapter 8085:8085
  curl http://localhost:8085/health
  ```

### 5.2 Kafka Topics

- [ ] **Verifiesr tópicos criados:**
  ```bash
  kubectl exec -n trisla <kafka-pod> -- kafka-topics --list --bootstrap-server localhost:9092
  ```

- [ ] **Tópicos esperados:**
  - `I-02-intent-to-ml`
  - `I-03-ml-predictions`
  - `trisla-i04-decisions`
  - `trisla-i05-actions`
  - `trisla-i06-agent-events`
  - `trisla-i07-agent-actions`

### 5.3 Conectividade com NASP

- [ ] **Testar coleta de metrics RAN:**
  ```bash
  kubectl exec -n trisla <nasp-adapter-pod> -- \
    curl -v http://<RAN_SERVICE>.<RAN_NAMESPACE>.svc.cluster.local:<RAN_PORT>/api/v1/metrics
  ```

- [ ] **Testar coleta de metrics Core:**
  ```bash
  kubectl exec -n trisla <nasp-adapter-pod> -- \
    curl -v http://<UPF_SERVICE>.<CORE_NAMESPACE>.svc.cluster.local:<UPF_METRICS_PORT>/metrics
  ```

### 5.4 Blockchain (Besu)

- [ ] **Verifiesr conexão Besu:**
  ```bash
  kubectl exec -n trisla <bc-nssmf-pod> -- \
    curl -X POST http://<BESU_RPC_URL> \
      -H "Content-Type: application/json" \
      -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
  ```

- [ ] **Verifiesr contract deployado:**
  ```bash
  kubectl exec -n trisla <bc-nssmf-pod> -- cat /app/src/contracts/contract_address.json
  ```

### 5.5 Observabilidade

- [ ] **Prometheus:**
  ```bash
  kubectl port-forward -n trisla svc/trisla-prometheus 9090:9090
  # Acessar http://localhost:9090
  ```

- [ ] **Grafana:**
  ```bash
  kubectl port-forward -n trisla svc/trisla-grafana 3000:3000
  # Acessar http://localhost:3000 (admin/admin)
  ```

- [ ] **Verifiesr metrics:**
  - `trisla_intents_total`
  - `trisla_decisions_total`
  - `trisla_sla_registrations_total`
  - `trisla_agent_events_total`

---

## 6. Teste E2E no NASP

### 6.1 Executar Teste E2E

- [ ] **Criar intent de teste:**
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

### 6.2 Validar Fluxo Completo

- [ ] **Verifiesr mensagem I-02 (Kafka):**
  ```bash
  kubectl exec -n trisla <kafka-pod> -- kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic I-02-intent-to-ml \
    --from-beginning \
    --max-messages 1
  ```

- [ ] **Verifiesr mensagem I-03 (Kafka):**
  ```bash
  kubectl exec -n trisla <kafka-pod> -- kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic I-03-ml-predictions \
    --from-beginning \
    --max-messages 1
  ```

- [ ] **Verifiesr mensagem I-04 (Kafka):**
  ```bash
  kubectl exec -n trisla <kafka-pod> -- kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic trisla-i04-decisions \
    --from-beginning \
    --max-messages 1
  ```

- [ ] **Verifiesr registro na blockchain:**
  ```bash
  kubectl logs -n trisla <bc-nssmf-pod> | grep "SLA registrado"
  ```

---

## 7. Troubleshooting

### 7.1 Pods in CrashLoopBackOff

- [ ] **Verifiesr logs:**
  ```bash
  kubectl logs -n trisla <pod-name> --previous
  ```

- [ ] **Verifiesr eventos:**
  ```bash
  kubectl describe pod -n trisla <pod-name>
  ```

### 7.2 problems de Conectividade

- [ ] **Verifiesr Network Policies:**
  ```bash
  kubectl get networkpolicies -n trisla
  ```

- [ ] **Testar conectividade entre pods:**
  ```bash
  kubectl exec -n trisla <pod-1> -- ping <pod-2-ip>
  ```

### 7.3 problems com Kafka

- [ ] **Verifiesr estado of Kafka:**
  ```bash
  kubectl exec -n trisla <kafka-pod> -- kafka-broker-api-versions --bootstrap-server localhost:9092
  ```

- [ ] **Verifiesr tópicos:**
  ```bash
  kubectl exec -n trisla <kafka-pod> -- kafka-topics --list --bootstrap-server localhost:9092
  ```

---

## 8. Checklist Final

- [ ] Todos os pods estão rodando (`kubectl get pods -n trisla`)
- [ ] Todos os health checks passam
- [ ] Kafka topics criados e acessíveis
- [ ] Conectividade com NASP testada e funcional
- [ ] Blockchain (Besu) conectado e funcional
- [ ] Observabilidade (Prometheus/Grafana) funcionando
- [ ] Teste E2E executado com sucesso
- [ ] Logs não mostram erros críticos

---

## 9. Próximos Passos Após Deploy

1. **Monitoramento Contínuo:**
   - configure alertas no Prometheus
   - configure dashboards no Grafana
   - Monitorar logs via `kubectl logs -f`

2. **Operação Diária:**
   - Seguir `README_OPERATIONS_PROD.md`
   - Executar health checks periódicos
   - Monitorar SLOs e compliance

3. **Manutenção:**
   - Update imagens quando necessário
   - Aplicar patches de segurança
   - Fazer backup de Data críticos

---

**Status of Checklist:** ⬜ Não iniciado | 🟡 Em progresso | ✅ Concluído

**Data de Conclusão:** _______________

**Operador Responsável:** _______________

---

**Versão:** 1.0  
**Data:** 2025-11-22  
**ENGINE MASTER:** Sistema de Pré-Deploy TriSLA


