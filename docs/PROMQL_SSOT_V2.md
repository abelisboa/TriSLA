# PromQL SSOT — TriSLA v2 (especificação)

**Estado:** referência oficial para implementação — **não aplicado** automaticamente pelo repositório nesta fase.  
** Overrides:** `TELEMETRY_PROMQL_*` no ambiente pode sobrepor; este documento é a **fonte normativa** desejada.

---

## Legenda

| Tag | Significado |
|-----|-------------|
| **nativa** | Medida diretamente do sistema do domínio (ou componente dedicado ao domínio). |
| **proxy** | Mede fenómeno correlato (ex.: probe TCP, simulador). |
| **derivada** | Derivada por agregação estatística sobre séries reais. |
| **escopada** | Filtro explícito (namespace/pod) — não global. |

---

## RAN

### PRB

**Query:** `avg(trisla_ran_prb_utilization)`  
**Em produção (lab):** `avg(trisla_ran_prb_utilization{job="trisla-prb-simulator"})` opcional.  
**Tipo:** **proxy** (simulador) ou **nativa** (exporter + srsRAN) conforme deploy.  
**Unidade:** coincide com gauge (0–100 %).

### Latência RAN

**Query:** `avg(trisla_ran_latency_ms)`  
**Com filtro de job:** `avg(trisla_ran_latency_ms{job="trisla-prb-simulator"})` quando aplicável.  
**Tipo:** **proxy** (simulador — modelo interno) até existir métrica de campo UE–gNB.  
**Unidade:** ms.

### Throughput (opcional)

**Query:** *a definir por ambiente* — exemplo: taxa de rede agregada RANTester com namespace/pod SSOT.  
**Tipo:** tipicamente **proxy** até O-RAN/throughput de ar nativo.  
**Unidade:** Mbps (requer conversão explícita na query ou no consumidor).

---

## TRANSPORT

### RTT

**Query:**  
`max(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}) * 1000`

**Tipo:** **proxy** (duração do probe blackbox em ms).  
**Unidade:** ms.

### Jitter

**Query:**  
`avg(stddev_over_time(probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}[1m]) * 1000)`

**Tipo:** **derivada** sobre série do probe — **proxy** para “jitter de fluxo” fim-a-fim.  
**Unidade:** ms.

### ONOS (futuro — não v1 do SSOT)

- Intents, path id: métricas ou anotações REST → **nativas** do domínio transporte SDN quando integradas.

---

## CORE (proposta escopada v2)

Substui o **anti-padrão** `sum(process_cpu_seconds_total)` / `sum(process_resident_memory_bytes)` sem filtro.

### CPU

**Query:**  
`sum(rate(container_cpu_usage_seconds_total{namespace="free5gc"}[1m]))`

**Normalização sugerida para [0,1] ou %:** dividir pela capacidade do cluster **ou** por `sum(kube_pod_container_resource_limits{...})` — **decisão de implementação** a documentar no PR de Core.

**Tipo:** **escopada** — depende do namespace `free5gc` existir e refletir o Core desejado; validar em ambiente real.

### Memória

**Query:**  
`sum(container_memory_working_set_bytes{namespace="free5gc"})`

**Tipo:** **escopada** (cAdvisor/kubelet).  
**Unidade:** bytes.

### Sessão (opcional)

**Query:** *a definir* — histogramas HTTP dos NFs ou métricas expostas pelo stack 5GC.

---

## Matriz proxy vs nativa (resumo)

| Métrica lógica | Query v2 (base) | Tag |
|----------------|-------------------|-----|
| PRB | `avg(trisla_ran_prb_utilization)` | proxy (sim) / nativa (exporter) |
| Latência RAN | `avg(trisla_ran_latency_ms)` | proxy até campo |
| RTT | `max(probe_duration_seconds{...})*1000` | proxy |
| Jitter | `avg(stddev_over_time(probe_duration_seconds{...}[1m])*1000)` | derivada + proxy |
| CPU Core | `sum(rate(container_cpu_usage_seconds_total{namespace="free5gc"}[1m]))` | escopada |
| Mem Core | `sum(container_memory_working_set_bytes{namespace="free5gc"})` | escopada |

---

*PROMPT_35 — PromQL SSOT v2 (documentação apenas).*
