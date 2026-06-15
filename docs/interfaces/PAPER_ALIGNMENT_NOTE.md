# Alinhamento paper — Interface Layer vs protótipo

Canonical interface reference: [`docs/modules/interfaces.md`](../modules/interfaces.md).

Este nota liga a **Interface Layer documental** (catálogo `RAN-I1` … `BC-I1`) ao **protótipo** descrito em evidências de repositório e em `docs/TRISLA_ARCHITECTURE_EVIDENCE_PATCHED.md` / `docs/TRISLA_FINAL_AUDIT_FOR_PAPER.md`, **sem** afirmar funcionalidades ainda não implementadas no código.

## O que o protótipo implementa hoje

- Comunicação **HTTP/REST** (e **Kafka** para eventos) entre microserviços.
- Pipeline de submissão: **Portal → SEM-CSMF → Decision Engine → ML-NSMF** no encadeamento real; **NASP Adapter** para orquestração; **BC-NSSMF** para registo; **SLA-Agent** opcional para ingest; **telemetria** via Prometheus e `telemetry_snapshot`.
- **Não** há camada de interfaces nomeadas no código; os nomes `RAN-I1`, etc. são **governança e documentação** (`docs/PROPOSED_INTERFACE_MODEL.md`).

## Como descrever a Interface Layer num artigo

1. **Camada lógica:** agrupar endpoints e canais existentes sob interfaces estáveis para discussão arquitetural e comparação com 3GPP/O-RAN/ETSI **conceitualmente** (`docs/interfaces/INTERFACE_STANDARDS_MAPPING.md`).
2. **Protótipo:** citar tabelas de módulos/endpoints factuais da auditoria; commits/deployments apenas como evidência de reprodutibilidade.
3. **Roadmap:** wrappers shadow/dual-run como **trabalho futuro** (`docs/INTERFACE_MIGRATION_PLAN.md`), não como estado atual.

## Frases seguras vs frases a evitar

| Seguro | Evitar sem prova adicional |
|--------|----------------------------|
| “The prototype exposes REST APIs between CSMF-like, NSMF-like, and NSSMF-like functions.” | “The system implements O-RAN O1/A1/E2 interfaces.” |
| “RAN metrics are consumed via Prometheus and embedded in `telemetry_snapshot`.” | “Native 3GPP FM/PM integration.” |
| “Blockchain governance is handled by a dedicated BC service (`register-sla`).” | “On-chain SLA standard compliance.” |

## Conexão com figuras de arquitetura

- **Bloco “Interface Layer”** num diagrama pode ser desenhado como **máscara documental** sobre os mesmos componentes já implantados (sem novo gateway).
- Setas permanecem iguais às do fluxo E2E canónico; apenas os **rótulos** mudam para `RAN-I1`/`OBS-I1`/etc. onde houver correspondência no catálogo.

## Referências

- `docs/interfaces/interface-catalog-v1.yaml`
- `docs/TRISLA_E2E_FLOW_CANONICAL.md`
- `docs/AUDIT_SUMMARY.md`
