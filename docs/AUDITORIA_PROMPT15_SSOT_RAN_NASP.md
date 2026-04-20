# AUDITORIA PROMPT_15 — SSOT PILHA RAN NASP (RANTester + Free5GC)

## 1) Decisao SSOT formal

A partir desta execucao, a referencia operacional foi consolidada como:

- **PILHA RAN OFICIAL (SSOT): `RANTester + Free5GC`**

Escopo excluido da campanha final:

- `srsRAN/srsenb`
- `UERANSIM`
- `PRB simulator`
- componentes legados de telemetria vinculados ao caminho srsRAN

## 2) Componentes removidos/desativados (fora da SSOT)

Acoes executadas:

- `kubectl -n srsran scale deployment srsenb --replicas=0`
- `kubectl -n ueransim scale deployment ueransim-singlepod --replicas=0`
- `kubectl -n srsran scale deployment ran-prb-exporter --replicas=0`

Evidencia:

- snapshots em `evidencias/prompt15_20260401T152956Z/non_ssot_candidates_*`
- no momento final, pods legados aparecem em estado `Terminating` (sem nova atividade de workload SSOT).

## 3) Componentes mantidos (SSOT)

Core Free5GC (namespace `ns-1274485`) mantido ativo:

- `amf`, `ausf`, `nrf`, `nssf`, `pcf`, `smf`, `udm`, `udr`, `upf`, `webui`

RAN/Traffic SSOT mantido ativo:

- `rantester-0` (`ns-1274485`) Running
- `ran-rantester-grafana-*` (`ran-test`) Running

## 4) Estado do cluster e consistencia

Fluxo alvo consolidado:

- `RANTester -> Free5GC -> trafego -> metricas -> Prometheus -> TriSLA`

Estado observado:

- Free5GC: consistente e ativo
- RANTester: ativo
- legado `srs/ueransim`: escalado para 0, em processo de finalizacao de pods antigos

## 5) Evidencias coletadas

Diretorio:

- `evidencias/prompt15_20260401T152956Z`

Arquivos principais:

- `pods_before.txt`
- `deployments_before.txt`
- `services_before.txt`
- `non_ssot_candidates_before.txt`
- `non_ssot_candidates_after.txt`
- `non_ssot_candidates_final*.txt`
- `free5gc_pods_after.txt`
- `ran_related_pods_after.txt`
- `rantester_logs_after.txt`
- `prometheus_summary_after.json`
- `prom_metric_candidates_ssot.txt`
- `ssot_stack_after.txt`

## 6) Nova definicao de RAN operacional

- RAN operacional da campanha final passa a ser definida por:
  - `My5G-RANTester` (geracao de carga/trafego no dominio RAN)
  - `Free5GC` (core)

Interpretacao:

- elimina-se o ambiente hibrido `srsenb + ueransim + rantester`.

## 7) Impacto na telemetria

- O caminho anterior baseado em PRB de `srsenb` deixa de ser referencia.
- Metricas candidatas observadas no Prometheus (estado atual):
  - `trisla_kpi_ran_health`
  - `trisla_kpi_transport_health`
  - `trisla_transport_jitter_ms`
  - latencias SEM (`trisla_sem_*_latency_*`)
- `prometheus/summary` atual mostra alvos ativos, mas ainda existem jobs `trisla-nasp-adapter*` com `up=0`, indicando que a telemetria final da nova SSOT ainda precisa de ajuste dedicado no proximo passo.

## 8) Validacao final (criterio PROMPT_15)

- **AMBIENTE ALINHADO COM SSOT?**  
  **SIM (com limpeza em finalizacao)** — stack ativa consolidada em `RANTester + Free5GC`; pods legados foram escalados para 0 e estao terminando.

- **PILHA RAN FINAL DEFINIDA?**  
  **SIM** — SSOT formalizada como `RANTester + Free5GC`.

- **PRONTO PARA NOVA TELEMETRIA?**  
  **NAO (ainda)** — requer etapa dedicada para fechar baseline de metricas RAN via SSOT e corrigir alvos de scrape pendentes (`nasp-adapter`).
