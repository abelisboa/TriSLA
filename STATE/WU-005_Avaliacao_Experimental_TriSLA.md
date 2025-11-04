# WU-005 — Avaliação Experimental da TriSLA@NASP
## Cenários, KPIs, Coleta de Métricas e Relato de Resultados

---

| Campo | Informação |
|------|------------|
| Data | 16/10/2025 |
| Responsável | Abel José Rodrigues Lisboa |
| Cluster | NASP – UNISINOS |
| Namespace | trisla-nsp |
| Objetivo | Conduzir a avaliação experimental da TriSLA integrada ao NASP, medindo KPIs em cenários URLLC, eMBB e mMTC, e consolidando evidências quantitativas para a dissertação. |

---

## 1) Contexto e Hipóteses
Após WU‑003 (integração NASP Core) e WU‑004 (testes/observabilidade), esta WU mede desempenho sob cargas representativas de serviços 5G.
**Hipóteses:** (H1) A TriSLA mantém latência e confiabilidade dentro de SLO por cenário; (H2) Os módulos SEM‑NSMF/ML‑NSMF/BC‑NSSMF escalam de forma estável sem erros críticos.

---

## 2) Cenários Experimentais
| Cenário | Descrição | Perfil Esperado |
|--------|-----------|------------------|
| **URLLC** | baixa latência, alta confiabilidade (telemedicina/controle) | p99 < 10–20ms, erro < 0.1% |
| **eMBB** | alta vazão (vídeo 4K/AR) | throughput alto, latência moderada |
| **mMTC** | muitos dispositivos, tráfego esparso | alta taxa de conexões, baixa carga por sessão |

**Topologia:** RAN/SMO/RIC/NWDAF do NASP, TriSLA nos pods `sem-nsmf`, `ml-nsmf`, `bc-nssmf` no namespace `trisla-nsp`.

---

## 3) KPIs e Métricas
- **Latência** (p50, p90, p99), **Jitter**, **Taxa de erro** (HTTP/gRPC), **Throughput**.
- **Uso de recursos**: CPU, memória por pod/nó.
- **Estabilidade**: reinícios de pods, falhas de readiness/liveness.
- **SLA-aware**: cumprimento de SLO por cenário (aprovado/reprovado).

Consultas Prometheus sugeridas (exportar resultado):
```
rate(container_cpu_usage_seconds_total{namespace="trisla-nsp"}[1m])
container_memory_usage_bytes{namespace="trisla-nsp"}
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{namespace="trisla-nsp"}[5m])) by (le, pod))
rate(http_requests_total{namespace="trisla-nsp",status=~"5.."}[5m])
```
Salvar em: `docs/evidencias/WU-005_avaliacao/prometheus_metrics.txt`

---

## 4) Procedimento de Execução
1. **Preparar carga por cenário** (gerador trafego/intent):
   ```bash
   # URLLC
   kubectl exec -n trisla-nsp deploy/sem-nsmf -- curl -X POST http://sem-nsmf:8080/intent -d '{"request":"cirurgia remota"}'
   # eMBB
   kubectl exec -n trisla-nsp deploy/sem-nsmf -- curl -X POST http://sem-nsmf:8080/intent -d '{"request":"streaming 4k"}'
   # mMTC
   kubectl exec -n trisla-nsp deploy/sem-nsmf -- curl -X POST http://sem-nsmf:8080/intent -d '{"request":"iot massivo"}'
   ```
2. **Rodar por janela T (ex.: 15–30 min) por cenário** e coletar métricas Prometheus/NWDAF.
3. **Exportar logs dos módulos**:
   ```bash
   kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sem-nsmf > docs/evidencias/WU-005_avaliacao/sem-nsmf.log
   kubectl logs -n trisla-nsp -l app.kubernetes.io/name=ml-nsmf  > docs/evidencias/WU-005_avaliacao/ml-nsmf.log
   kubectl logs -n trisla-nsp -l app.kubernetes.io/name=bc-nssmf > docs/evidencias/WU-005_avaliacao/bc-nssmf.log
   ```
4. **Coletar NWDAF**:
   ```bash
   kubectl exec -n trisla-nsp deploy/ml-nsmf -- curl http://nwdaf-core:8081/api/v1/metrics > /tmp/nwdaf_metrics.json
   kubectl cp -n trisla-nsp $(kubectl get pod -n trisla-nsp -l app.kubernetes.io/name=ml-nsmf -o jsonpath='{.items[0].metadata.name}'):tmp/nwdaf_metrics.json docs/evidencias/WU-005_avaliacao/nwdaf_metrics.json
   ```
5. **Capturar observabilidade** (prints): Grafana dashboards, Jaeger traces. Salvar PNGs em `docs/evidencias/WU-005_avaliacao/`.

---

## 5) Tabelas de Resultados
Preencher após execução (exemplo de estrutura).

### 5.1 KPIs por Cenário (p99, erro)
| Cenário | p99 Latência (ms) | Erro (%) | Throughput (Gbps) | SLO |
|--------|--------------------|----------|-------------------|-----|
| URLLC | — | — | — | Aprov/Reprov |
| eMBB  | — | — | — | Aprov/Reprov |
| mMTC  | — | — | — | Aprov/Reprov |

### 5.2 Estabilidade de Pods
| Pod | Restarts | Ready (%) | Observações |
|-----|----------|-----------|------------|
| sem-nsmf | — | — | — |
| ml-nsmf  | — | — | — |
| bc-nssmf | — | — | — |

---

## 6) Evidências e Artefatos
```
docs/evidencias/WU-005_avaliacao/
 ├── sem-nsmf.log
 ├── ml-nsmf.log
 ├── bc-nssmf.log
 ├── prometheus_metrics.txt
 ├── nwdaf_metrics.json
 ├── grafana_urlcc.png
 ├── grafana_embb.png
 ├── grafana_mmtc.png
 ├── jaeger_trace_urlcc.png
 └── resumo_resultados.txt
```

---

## 7) Critérios de Aceitação
- Coleta completa de KPIs e logs por cenário.  
- p99 e taxa de erro dentro de SLO definidos por cenário.  
- Evidências salvas e tabelas preenchidas.  
- Ausência de erros críticos nos logs.

---

## 8) Conclusão (a preencher)
Resumo dos resultados, interpretação, e implicações para a dissertação.

📅 **Data:** 16/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
