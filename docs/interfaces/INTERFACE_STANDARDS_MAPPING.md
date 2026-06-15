# Mapeamento conceitual — 3GPP, O-RAN, ETSI ZSM

Canonical interface reference: [`docs/modules/interfaces.md`](../modules/interfaces.md).

Este documento alinha a **Interface Layer documental** TriSLA (`RAN-I1`, `TN-I1`, `CN-I1`, `OBS-I1`, `BC-I1`) a referências externas **sem afirmar** implementação nativa de **A1**, **E2** ou **O1** quando o código expõe apenas comportamento análogo (REST, PromQL, payloads JSON).

Fontes internas: `docs/AUDIT_INTERFACES_3GPP_MAPPING.md`, `docs/PROPOSED_INTERFACE_MODEL.md`, `docs/AUDIT_INTERFACES_GAPS.md`.

## 3GPP (visão funcional)

| Interface TriSLA | Relação 3GPP (conceitual) | Limite |
|-------------------|---------------------------|--------|
| **CN-I1** | CSMF entrada e função semântica (`/interpret`), handoff para orquestração de rede (`/intents`), decisão/admissão via SEM→Decision→ML, NSSMF para `nsi/instantiate` e gates | Contratos não são TS numerados; rotas são REST proprietárias |
| **RAN-I1** / **TN-I1** | Dados de desempenho por domínio alimentam decisão e assurance | Transporte de dados via métricas e snapshot, não F1/E1/etc. |
| **OBS-I1** | Funções auxiliares de gestão/assurance (telemetria para decisão) | Não FM/PM 3GPP como produto |
| **BC-I1** | Fora do núcleo 3GPP de gestão de rede clássica | Governança complementar |

## O-RAN

| Interface TriSLA | Analogia O-RAN | O que **não** está implementado |
|------------------|------------------|--------------------------------|
| **OBS-I1**, **RAN-I1** | Comportamento tipo **O1** (observabilidade) e operações de leitura/ação em agentes | **O1** como interface protocolar standard (XML/YANG, netconf gRPC per O-RAN specs) |
| **CN-I1** | Orquestração aproximada a **SMO** / fluxo de control apps | **A1** policy service, **E2** RIC service model como interfaces nativas |
| **TN-I1** | Dados de transporte para closed-loop | Sem Near-RT RIC / E2 formal |

**Declaração explícita:** o repositório, segundo a auditoria, oferece **HTTP/REST**, **Prometheus**, **Kafka** e **payloads JSON**. Qualquer alinhamento com A1/E2/O1 é **funcional e documental**, não certificação de conformidade O-RAN.

## ETSI ZSM

| Interface TriSLA | Papel ZSM (conceitual) |
|--------------------|-------------------------|
| **OBS-I1** | Management / closed-loop data para assurance |
| **CN-I1** | Encadeamento control plane entre funções de gestão |
| **BC-I1** | Camada de governança e evidência (complementar ao modelo ZSM clássico) |

Não há catálogo ETSI ZSM formalizado no código; o mapeamento é **arquitetónico** para papers e roadmap.

## Uso recomendado em publicações

- Preferir formulações do tipo: *“behaviour consistent with O1-like observability”* ou *“CSMF/NSMF-style handoff”*.
- Evitar: *“implements O-RAN O1”* ou *“implements 3GPP A1”* sem prova de stack protocolar.

## Referências cruzadas

- Detalhe por endpoint: `docs/AUDIT_INTERFACES_3GPP_MAPPING.md`
- Gaps de formalização: `docs/AUDIT_INTERFACES_GAPS.md`
