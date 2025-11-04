# WU-004 — Testes e Observabilidade Multi‑Domínio TriSLA@NASP
## Validação de KPIs, Logs, Métricas e Comportamento SLA‑Aware

---

| Campo | Informação |
|--------|-------------|
| Data | 16/10/2025 |
| Responsável | Abel José Rodrigues Lisboa |
| Cluster | NASP – UNISINOS |
| Namespace | trisla-nsp |
| Objetivo | Executar testes funcionais, coleta de KPIs e observabilidade integrada da TriSLA sobre o NASP, validando desempenho, conformidade e comportamento SLA‑aware. |

---

## 🧩 1️⃣ Contexto

Após a integração com o NASP Core (WU‑003), esta unidade de trabalho valida o funcionamento global da TriSLA,  
avaliando desempenho, confiabilidade e visibilidade operacional dos módulos SEM‑NSMF, ML‑NSMF e BC‑NSSMF.  
Os resultados servirão como evidência empírica da proposta para a dissertação.

---

## ⚙️ 2️⃣ Pré‑Requisitos

| Item | Status |
|------|---------|
| WU‑002 — Deploy Core Modules | ✅ |
| WU‑003 — Integração NASP Core | ✅ |
| Módulos TriSLA em operação | ✅ |
| Monitoramento NASP ativo (Prometheus / Grafana / Jaeger / Loki) | ✅ |
| NWDAF subscrito | ✅ |

---

## 🧪 3️⃣ Tipos de Testes

| Categoria | Objetivo | Ferramentas |
|------------|-----------|--------------|
| **Funcional** | Verificar funcionamento e resposta dos módulos TriSLA. | `kubectl exec`, `curl`, `helm test` |
| **Desempenho (KPIs)** | Avaliar latência, throughput, uso de CPU/memória. | Prometheus / cAdvisor |
| **SLA‑Aware Validation** | Testar respostas semânticas e enforcement de contratos. | Logs TriSLA / Smart Contracts |
| **Observabilidade** | Validar visibilidade cross‑domínio (RAN, Core, Transporte). | Jaeger / Grafana / Loki |
| **Resiliência** | Simular falhas e medir tempo de recuperação. | `kubectl delete pod` + Prometheus alert rules |

---

## 📡 4️⃣ Testes Funcionais Básicos

### 🔹 Status geral dos módulos
```bash
kubectl get pods -n trisla-nsp -o wide
```

### 🔹 Comunicação interna entre módulos
```bash
kubectl exec -n trisla-nsp deploy/sem-nsmf -- curl http://ml-nsmf:8080/health
kubectl exec -n trisla-nsp deploy/ml-nsmf -- curl http://bc-nssmf:8080/health
```

### 🔹 Teste de resposta semântica
```bash
kubectl exec -n trisla-nsp deploy/sem-nsmf -- curl -X POST http://sem-nsmf:8080/intent -d '{"request":"cirurgia remota"}'
```

**Esperado:** mapeamento automático da intenção → slice URLLC.

---

## 📊 5️⃣ Métricas e KPIs

### 🔹 Latência e uso de recursos
```bash
kubectl top pods -n trisla-nsp
kubectl top nodes
```

### 🔹 Coleta Prometheus
```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```
Consultas sugeridas:
```
rate(container_cpu_usage_seconds_total{namespace="trisla-nsp"}[1m])
container_memory_usage_bytes{namespace="trisla-nsp"}
```

### 🔹 Métricas NWDAF
```bash
kubectl exec -n trisla-nsp deploy/ml-nsmf -- curl http://nwdaf-core:8081/api/v1/metrics
```

**Esperado:** métricas de latência, confiabilidade e eventos de predição.

---

## 🧾 6️⃣ Logs e Rastreamento

### 🔹 Logs estruturados
```bash
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sem-nsmf > docs/evidencias/WU-004_tests/sem-nsmf.log
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=ml-nsmf > docs/evidencias/WU-004_tests/ml-nsmf.log
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=bc-nssmf > docs/evidencias/WU-004_tests/bc-nssmf.log
```

### 🔹 Jaeger (tracing)
Acesse Jaeger:
```
http://<NASP_IP>:32000/search
```
Pesquise pelo serviço `trisla-*` e salve o gráfico de rastreamento em:
```
docs/evidencias/WU-004_tests/trace_jaeger.png
```

### 🔹 Loki / Grafana (logs unificados)
Consultas recomendadas:
```
{namespace="trisla-nsp"} |~ "error|timeout|latency"
{app="ml-nsmf"} | json | line_format "{{.message}}"
```

---

## 🧱 7️⃣ Estrutura de Evidências

```
docs/evidencias/WU-004_tests/
 ├── sem-nsmf.log
 ├── ml-nsmf.log
 ├── bc-nssmf.log
 ├── prometheus_metrics.txt
 ├── nwdaf_metrics.json
 ├── trace_jaeger.png
 ├── grafana_kpis.png
 └── observability_summary.txt
```

---

## ✅ 8️⃣ Critérios de Aceitação

| Critério | Resultado Esperado |
|-----------|--------------------|
| Módulos TriSLA respondem corretamente a requisições | ✅ |
| Métricas Prometheus e NWDAF acessíveis | ✅ |
| KPIs de latência e uso de recursos dentro dos limites | ✅ |
| Logs sem erros críticos | ✅ |
| Observabilidade integrada (Jaeger, Grafana, Loki) funcional | ✅ |
| Evidências armazenadas e documentadas | ✅ |

---

## 🧾 9️⃣ Conclusão

A WU‑004 comprova a operação estável e mensurável da TriSLA integrada ao NASP.  
Foram validados KPIs, métricas, logs e observabilidade multi‑domínio, confirmando o comportamento SLA‑aware da arquitetura.  
Os resultados obtidos constituem evidência empírica para análise no Capítulo de Avaliação Experimental da dissertação.

📅 **Data:** 16/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
