# Capítulo 6 — Protótipo da Arquitetura TriSLA

> Documento de redação definitiva — PPGCA/UNISINOS  
> Modo: descrição acadêmica da implementação congelada (sem proposta arquitetural nova)

---

## Validação pré-redação

### 1. Estrutura proposta

| Seção | Conteúdo previsto | Aderência à auditoria |
|-------|-------------------|------------------------|
| 6.1 Visão Geral | Objetivo, NASP, integração | OK — escopo descritivo |
| 6.2 SEM-CSMF | NLP, ontologia, GST, NEST, resolver | OK — excluir Entity Linker |
| 6.3 ML-NSMF | RF, SHAP, LIME, inferência | OK — excluir LSTM, FL, retraining online |
| 6.4 Decision Engine | Fluxo, fórmulas TriSLA, gates | OK — formalização em subseção; cautela com `g_transport` live |
| 6.5 NASP Adapter | Core, RAN, transporte, telemetria | OK — excluir NWDAF |
| 6.6 BC-NSSMF | Besu, Solidity, eventos | OK — lineage API não wired: mencionar persistência on-chain, não API lineage |
| 6.7 SLA-Agent | Assurance, compliance, correlation | OK — H5/H7 PARTIAL; sem closed-loop autônomo |
| 6.8 Fluxo integrado | Pipeline E2E | OK — alinhado ao artigo §III.E |

### 2. Aderência à auditoria técnica

Restrições obrigatórias incorporadas ao plano de redação:

- Descrever apenas funcionalidades com evidência em `apps/` e packs congelados.
- Não afirmar Entity Linker, LSTM, NWDAF, closed-loop autônomo completo, retraining online.
- Fórmulas do Decision Engine e ML classificadas como contribuição TriSLA (origem C).
- Transporte: descrever como telemetria e pressão multidomínio; na §6.4 tratar `g_transport` conforme estado do código (SSOT documenta; integração live requer verificação na redação de 6.4).
- Governança blockchain: descrever registro em submissão (O9C); supervisão longitudinal como parcial.

### 3. Referências necessárias por subseção

| Subseção | Referências previstas |
|----------|----------------------|
| 6.1 | Grings et al. (NASP); O-RAN Alliance (arquitetura); ETSI ZSM (alinhamento conceitual, sem conformidade) |
| 6.2 | 3GPP TS 28.541; GSMA NG.116 (alinhamento parcial GST/canonical SLA) |
| 6.3 | Breiman (Random Forest); Lundberg & Lee (SHAP); Ribeiro et al. (LIME) |
| 6.4 | Contribuição TriSLA (fórmulas); 3GPP apenas se citar métricas de rede |
| 6.5 | 3GPP (gate NGAP); O-RAN (observabilidade RAN) |
| 6.6 | Hyperledger Besu; literatura blockchain-SLA (Zhang et al., Bao et al.) |
| 6.7 | ETSI ZSM (supervisão de ciclo de vida, conceitual) |
| 6.8 | Nenhuma normativa adicional — fluxo interno |

### 4. Fórmulas a formalizar (§6.4)

| Fórmula | Classificação | Onde no código |
|---------|---------------|----------------|
| `decision_score = Σ(wᵢ·gᵢ)/Σwᵢ` | TriSLA (C) | `decision_score_mode.py` |
| `g_prb = clamp01(1 − PRB/100)` | TriSLA (C) | `decision_score_mode.py` |
| `risk_v7 = min(1, 0.5·P(RENEG)+P(REJECT))` | TriSLA (C) | `ml-nsmf` |
| `pressure` ponderado (0.4/0.3/0.3) | TriSLA (C) | `feasibility_runtime.py` |
| `feasibility = 1 − (risk+pressure)/2` | TriSLA (C) | `feasibility_runtime.py` |
| `adjusted_risk` (α=0.42) | TriSLA (C) | `slice_risk_adjustment.py` |
| SHAP / LIME | Literatura (B) | `predictor.py` |

---

## 6.1 Visão Geral do Protótipo

O protótipo da TriSLA materializa, em ambiente operacional controlado, a arquitetura SLA-aware definida nos capítulos anteriores desta dissertação. Seu propósito é demonstrar, de forma reprodutível e rastreável, a cadeia completa que conduz um requisito de SLA — expresso em linguagem natural ou em formulário estruturado — até a decisão preventiva de admissão, a eventual orquestração de recursos de rede, o registro imutável de governança e a supervisão de conformidade em tempo de execução. A implementação não constitui uma redefinição da arquitetura proposta; corresponde ao estado congelado do sistema validado experimentalmente nas campanhas documentadas nos pacotes de evidência do repositório, com imagens de contêiner referenciadas por digest e sem alteração de fórmulas, limiares ou semântica decisória após o congelamento científico.

A execução do protótipo ocorre sobre a plataforma NASP (*Network Slice as a Service Platform*), ambiente experimental que integra componentes de core 5G, emulação de RAN e instrumentação de transporte em cluster Kubernetes, permitindo a correlação de telemetria multidomínio no momento da submissão de um SLA \cite{grings2025nasp}. O namespace operacional concentra os microserviços da TriSLA — portal de submissão, SEM-CSMF, ML-NSMF, Decision Engine, NASP Adapter, BC-NSSMF e SLA-Agent Layer — além dos exportadores Prometheus, do coletor OpenTelemetry e dos serviços de core e RAN necessários à validação ponta a ponta. O core experimental emprega free5GC na versão documentada no baseline de infraestrutura; a camada de acesso radio utiliza emulação com UERANSIM, e os experimentos de transporte recorrem, quando configurados, a caminhos ONOS/Mininet para observação de latência e jitter. A arquitetura de referência O-RAN fornece o enquadramento conceitual para a separação entre inteligência, execução e observabilidade em redes abertas \cite{oran_architecture}, sem que o protótipo reivindique conformidade normativa com especificações da aliança ou dos organismos de padronização.

Do ponto de vista funcional, o protótipo organiza-se em três planos complementares, reproduzindo a decomposição adotada no artigo consolidado e no documento mestre de baseline em tempo de execução. O plano de inteligência reúne o SEM-CSMF, responsável pela interpretação semântica e pela materialização de objetos GST e NEST; o ML-NSMF, que produz estimativas de risco e metadados de explicabilidade por meio de modelos Random Forest com técnicas SHAP e LIME; e o Decision Engine, autoridade de admissão preventiva que combina score composto, pressão de recursos, viabilidade e *hard gates* sobre utilização de PRB. O plano de execução ancora-se no portal backend e no NASP Adapter: após decisão de aceitação, a orquestração de instâncias de slice e reservas de capacidade ocorre de forma desacoplada da recomputação decisória, com reconciliação assíncrona de objetos Kubernetes sem retroalimentação ao motor de decisão. O plano de governança e observabilidade compreende o BC-NSSMF, com registro de contratos inteligentes em rede permissionada Hyperledger Besu, e o SLA-Agent Layer, que expõe endpoints HTTP para ingestão de eventos de pipeline, revalidação de telemetria e avaliação determinística de conformidade. A telemetria multidomínio — RAN, transporte e core — é coletada por meio de snapshots Prometheus no instante da submissão, alimentando os termos de pressão e viabilidade do processo decisório.

A integração entre os componentes segue um fluxo canônico invariante: interpretação e persistência semântica; admissão preventiva com base em snapshot de telemetria e predição de risco; acionamento condicional de orquestração; persistência de objetos de orquestração em CRDs; reconciliação de estado de cluster; registro de governança em submissão; e validação sob demanda pelo SLA-Agent. As etapas de orquestração e reconciliação não recomputam a admissão já emitida, preservando a natureza preventiva do controle SLA-aware. O protótipo emprega interfaces REST documentadas no catálogo de serviços — interpretação de intenção, avaliação decisória, instanciação NSI, registro on-chain e revalidação de telemetria — sem implementar callbacks de orquestração ou de reconciliação em direção ao Decision Engine. A abordagem de gestão de serviços de rede com intervenção mínima do operador, associada ao paradigma ETSI Zero-touch Network and Service Management, informa conceitualmente a organização dos módulos de supervisão e correlação, embora a implementação se limite aos mecanismos efetivamente desenvolvidos e validados \cite{ETSI2021ZSM}.

O escopo implementado abrange admissão preventiva com *decision_score_mode*, orquestração NASP acionada pelo portal, contabilização de capacidade com reconciliador, observação NSI, registro de SLA via BC-NSSMF, revalidação HTTP pelo SLA-Agent e exportação multidomínio de métricas. Permanecem fora do escopo desta implementação congelada: retroalimentação autônoma contínua do motor de decisão a partir de eventos de orquestração; consumidor Kafka permanente no SLA-Agent para reavaliação sem solicitação explícita; registro unificado de SLAs em API de listagem do portal; e retreinamento online de modelos de aprendizado de máquina. A caracterização explícita desses limites assegura coerência entre a descrição do protótipo, os resultados experimentais dos capítulos subsequentes e as afirmações do artigo científico, nas quais a supervisão de ciclo de fechado e a continuidade plena de governança são tratadas como evidências parciais, dependentes de campanhas específicas e de instrumentação complementar.

As seções seguintes detalham, módulo a módulo, a implementação congelada: arquitetura semântica e geração de NEST (§6.2); pipeline de inferência e explicabilidade (§6.3); mecanismos decisórios e formalização matemática (§6.4); integração multidomínio e telemetria (§6.5); governança por contratos inteligentes (§6.6); camada de assurance e correlação (§6.7); e o fluxo operacional integrado (§6.8).
