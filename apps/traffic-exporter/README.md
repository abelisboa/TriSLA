# TriSLA Traffic Exporter

**Versão:** v3.10.0  
**Module:** Passive observability — traffic metrics and event export.

## Formal Definition (SSOT)

The **traffic-exporter** is a first-class module in the TriSLA architecture, defined as:

> **Passive observability module** responsible for exporting traffic metrics and flow events to Prometheus/Kafka, **without interfering with the decision plane**.

### Functional Scope (Mandatory)

- Expor endpoint `/metrics` (formato Prometheus) na porta 9105.
- Optionally publish simple events to Kafka (if the cluster already provides Kafka).
- Do not make decisions, do not alter SLAs, do not operate in the control plane, and do not replace existing modules.

### Prohibitions

- Perform SLA admission or rejection decisions.
- Alter SLAs or system state.
- Operate in the control plane (NASP, SEM-CSMF, Decision Engine, etc.).
- Replace or duplicate functionality from other TriSLA modules.

## Usage

- **Porta:** 9105 (HTTP).
- **Endpoints:** `/metrics` (Prometheus), `/health` (opcional).
- **Deployment:** via Helm (trisla chart), namespace `trisla`.

## References

- PROMPT_S52 — Official incorporation of traffic-exporter as a TriSLA module (v3.10.0).
- PROMPT_S48 — Gate exige trisla-traffic-exporter:v3.10.0 para execução experimental.
