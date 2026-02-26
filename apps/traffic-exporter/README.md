# TriSLA Traffic Exporter

**Versão:** v3.10.0  
**Módulo:** Observabilidade passiva — exportação de métricas e eventos de tráfego.

## Definição formal (SSOT)

O **traffic-exporter** é um módulo de primeira classe da arquitetura TriSLA, definido como:

> **Módulo de observabilidade passiva** responsável por exportar métricas de tráfego e eventos de fluxo para Prometheus/Kafka, **sem interferência no plano de decisão**.

### Escopo funcional (obrigatório)

- Expor endpoint `/metrics` (formato Prometheus) na porta 9105.
- Opcionalmente publicar eventos simples no Kafka (se o cluster já dispuser de Kafka).
- Não tomar decisões, não alterar SLAs, não atuar no plano de controle e não substituir módulos existentes.

### Proibições

- Tomar decisões de admissão ou rejeição de SLAs.
- Alterar SLAs ou estado do sistema.
- Atuar no plano de controle (NASP, SEM-CSMF, Decision Engine, etc.).
- Substituir ou duplicar funcionalidade de outros módulos TriSLA.

## Uso

- **Porta:** 9105 (HTTP).
- **Endpoints:** `/metrics` (Prometheus), `/health` (opcional).
- **Deploy:** via Helm (chart trisla), namespace `trisla`.

## Referências

- PROMPT_S52 — Incorporação Oficial do traffic-exporter como Módulo TriSLA (v3.10.0).
- PROMPT_S48 — Gate exige trisla-traffic-exporter:v3.10.0 para execução experimental.
