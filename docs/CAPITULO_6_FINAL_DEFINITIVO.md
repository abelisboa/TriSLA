# Capítulo 6 — Avaliação experimental (versão para defesa)

**PROMPT_59 / PROMPT_60.** Este capítulo consolida evidência empírica sobre a arquitetura TriSLA em *runtime* NASP, articulando explicitamente a **pergunta de investigação** com os ensaios **PROMPT_48** (política SLA V1 vs V2) e **PROMPT_58** (*pipeline* admissional com latências reais por módulo em `metadata.module_latencies_ms`). As figuras citadas seguem o *pipeline* IEEE em `evidencias/PROMPT50_PIPELINE_COMPLETO/scripts/generate_figures.py` (300 dpi, tipografia *serif*). Para reprodução: definir `TRISLA_FIGURES_CSV` para o CSV desejado; por omissão, o gerador pode priorizar o export PROMPT_58 quando presente no repositório.

**Resumo para o júri (≤ 150 palavras).** Demonstra-se que (i) uma política de agregação multi-domínio **V2** aumenta a pressão de recursos média face à **V1** sem alterar a decisão de admissão nas amostras HTTP válidas analisadas; (ii) o *endpoint* `POST /api/v1/sla/submit` exporta **decomposição temporal** coerente (SEM→decisão, ML-NSMF, NASP, blockchain, SLA-Agent), com *gates* de positividade cumpridos em sessenta pedidos consecutivos; (iii) o *gargalo* operacional associado ao **NASP** (integração e *gates* 3GPP) distingue-se do *gargalo* temporal dominado por SEM→decisão e blockchain. As conclusões restringem-se ao perímetro experimental e às limitações da Secção 6.6.

---

## 6.0 Seleção de figuras (PROMPT_59)

### Grupo A — política (V1 vs V2 e métricas derivadas)

| ID | Ficheiro | Papel na narrativa |
|----|----------|-------------------|
| Fig. 6.A.1 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig01_resource_pressure_kde_v1_v2.png` | Distribuição de `resource_pressure` por política |
| Fig. 6.A.2 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig02_feasibility_kde_v1_v2.png` | Distribuição de *feasibility score* por política |
| Fig. 6.A.3 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig03_boxplots_by_slice_pressure_feasibility.png` | Pressão e viabilidade por tipo de *slice* |
| Fig. 6.A.4 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig12_delta_v2_minus_v1_per_slice.png` | Deslocamento V2−V1 por *slice* |
| Fig. 6.A.5 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig18_cdf_resource_pressure.png` | CDF de pressão de recursos |
| Fig. 6.A.6 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig19_cdf_feasibility_score.png` | CDF do *feasibility score* |

**Nota metodológica:** os gráficos comparativos V1 vs V2 utilizam predominantemente o dataset **PROMPT_48** (`evidencias/PROMPT48/07_dataset_final.csv`), onde ambas as políticas foram exercidas em campanhas separadas (alternância da *flag* `USE_SLA_V2` no *portal-backend*). Se o gerador for executado apenas sobre o export PROMPT_58, a coluna `policy` pode refletir uma única política efectiva na janela de recolha — o texto quantitativo V1 vs V2 mantém-se ancorado ao PROMPT_48.

### Grupo B — *pipeline* completo (latência por módulo)

| ID | Ficheiro | Papel na narrativa |
|----|----------|-------------------|
| Fig. 6.B.1 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig13_pipeline_module_latency_boxplots.png` | Boxplots de latências de estágio (dataset em uso) |
| Fig. 6.B.2 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig14_pipeline_module_share.png` | Partilha relativa entre módulos |
| Fig. 6.B.3 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig15_pipeline_cumulative_latency.png` | Visão cumulativa do *pipeline* |
| Fig. 6.B.4 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig23_pipeline_modules_mean_by_slice.png` | Médias por módulo e por *slice* (PROMPT_58) |
| Fig. 6.B.5 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig24_pipeline_stacked_mean_by_slice.png` | Barras empilhadas (ms) por *slice* |
| Fig. 6.B.6 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig25_pipeline_module_share_pie.png` | Partilha percentual média global |
| Fig. 6.B.7 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig26_partial_vs_full_pipeline_latency.png` | SEM+Decisão vs soma síncrona completa |
| Fig. 6.B.8 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig27_pressure_vs_client_e2e_latency.png` | Pressão vs latência observada no cliente |
| Fig. 6.B.9 | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/fig28_nasp_vs_full_pipeline.png` | Latência NASP vs *pipeline* total |

**Nota:** as Figuras **6.B.4–6.B.9** assumem colunas planas de latência (`sem_pipeline_to_decision_ms`, `ml_nsmf_predict_ms`, `nasp_orchestration_ms`, `blockchain_register_ms`, `sla_agent_ingest_http_ms`) como no **PROMPT_58**; as Figuras **6.B.1–6.B.3** devem ser lidas em conjunto com `evidencias/PROMPT50_PIPELINE_COMPLETO/validation/00_dataset_columns.txt` do mesmo *run*.

---

## 6.1 Pergunta de investigação e operacionalização (PROMPT_60 — Fase 1)

### 6.1.1 Pergunta de pesquisa principal

**É possível, em ambiente NASP real, integrar interpretação semântica, decisão *SLA-aware* alimentada por telemetria multi-domínio (RAN, Transporte, Core) e encadeamento pós-decisão (orquestração NASP, registo blockchain, *ingest* no SLA-Agent), de modo que o comportamento do sistema seja simultaneamente (a) **comparável sob variantes de política de agregação** (V1 vs V2) e (b) **mensurável em latência por módulo**, preservando rastreabilidade experimental?**

Esta formulação alinha o capítulo à contribuição central da dissertação: não se alega apenas uma arquitetura, mas a **existência de um corpo de evidência reprodutível** sobre decisões e tempos de estágio em *runtime* operacional.

### 6.1.2 Sub-perguntas e como foram respondidas

| Sub-pergunta | Operationalização (métricas / artefactos) | Resposta resumida (onde está no capítulo) |
|--------------|--------------------------------------------|-------------------------------------------|
| **SQ1.** A política V2 altera a caracterização da pressão de recursos face à V1, à custa da estabilidade decisória? | `resource_pressure`, `resource_pressure_v1`, `resource_pressure_v2`, *feasibility score*; N válido por campanha; Figuras Grupo A | V2 aumenta pressão média (Δ ≈ +0,0188) e reduz ligeiramente o *feasibility* (Δ ≈ −0,0055); decisões nas amostras válidas: ACCEPT (Secção 6.3.1) |
| **SQ2.** O *pipeline* admissional expõe latências **positivas e discrimináveis** por módulo? | `module_latencies_ms` planos; *gates* PROMPT_58; Figuras Grupo B | Quatro *gates* (ML, NASP, SLA-Agent, BC) > 0 em 60/60; decomposição temporal quantificada (Secção 6.3.2) |
| **SQ3.** Onde reside o *gargalo* dominante — temporal vs integração? | Partilhas % de \(T_{\mathrm{full}}\); `nasp_orchestration_status` / HTTP 422 | Temporal: SEM→decisão e blockchain; integração: NASP como risco *gate* (Secção 6.3.3) |
| **SQ4.** O sistema mantém-se estável sob o protocolo experimental? | Taxa HTTP 200; `telemetry_complete`; cardinalidade de falhas V1 | Instrumentação robusta no PROMPT_58; ressalva de falhas HTTP na campanha V1 do PROMPT_48 (Secção 6.3.4, 6.6) |

### 6.1.3 Critérios de aceitação empírica (defesa)

Para o âmbito deste capítulo, consideram-se **satisfeitos** os seguintes critérios:

1. **Rastreabilidade:** todas as métricas numéricas citadas em 6.3 derivam de CSVs versionados (`07_dataset_final.csv`, `dataset_final_completo.csv`) ou de `summary.json`, sem valores *inventados*.
2. **Comparabilidade política:** V1 e V2 são contrastados sobre o mesmo *runner* e perfis de *slice*, reconhecendo diferenças de N quando há erros HTTP.
3. **Completude do *pipeline* medido:** o PROMPT_58 demonstra que a API pode reportar, em produção de laboratório, tempos por estágio além do par SEM+Decisão.
4. **Honestidade limitativa:** conclusões não extrapolam para caos operacional, carga massiva ou cenários não instrumentados.

---

## 6.2 Enquadramento experimental

A avaliação combina dois eixos complementares:

1. **Política de agregação SLA (V1 vs V2)** — *runner* determinístico (`scripts/e2e/prompt21_multi_domain_validation.py`), três perfis de *slice* (URLLC, eMBB, mMTC), telemetria multi-domínio no contrato V2, e métricas exportadas no JSON de resposta, sem *backfill* sintético.
2. **Decomposição temporal do *pipeline* admissional** — campanha PROMPT_58 (sessenta pedidos HTTP 200, vinte repetições por *slice*) com validação de que `ml_nsmf_predict_ms`, `nasp_orchestration_ms`, `sla_agent_ingest_http_ms` e `blockchain_register_ms` são **estritamente positivos** em todas as amostras (`evidencias/PROMPT58_PIPELINE_FULL/summary.json`, `all_four_all_gt0: true`).

Esta separação evita confundir “sensibilidade da política” (eixo sobre *snapshots* agregados) com “custo por estágio” (eixo sobre temporizações de serviço).

---

## 6.3 Resultados quantitativos principais

### 6.3.1 Impacto da política (V1 vs V2) — dataset PROMPT_48

Sobre as amostras com `http_status = 200` em `07_dataset_final.csv` (N = 108 no agregado analisado):

| Política (rótulo experimental) | N válido | Média `resource_pressure` | Média *feasibility score* |
|----------------------------------|---------|---------------------------|---------------------------|
| v1 | 48 | ≈ 0,0740 (σ ≈ 0,0082) | ≈ 0,7984 |
| v2 | 60 | ≈ 0,0928 (σ ≈ 0,0052) | ≈ 0,7929 |

- O valor activo de pressão sob V2 é superior ao observado sob V1 (Δ médio ≈ **+0,0188**), coerente com o modelo V2 (jitter, memória normalizada em `resource_pressure_v2` quando aplicável).
- O *feasibility score* diminui ligeiramente (Δ ≈ **−0,0055**).
- Em todas as linhas válidas deste agregado, a decisão foi **ACCEPT**: a V2 aumenta a métrica de pressão sem, nas condições testadas, cruzar limiares que alterem a decisão — **estabilidade decisória** no regime observado.

As **Figuras 6.A.1–6.A.6** apoiam esta leitura.

**Limitação:** na campanha V1 do PROMPT_48 ocorreram falhas HTTP adicionais; as médias utilizam apenas linhas válidas (cardinalidades 48 vs 60), como já documentado em `docs/CAPITULO_6_AVALIACAO_EXPERIMENTAL_DEFINITIVO_PROMPT49.md`.

### 6.3.2 Custo computacional por módulo — dataset PROMPT_58

Define-se, por pedido:

\[
T_{\mathrm{full}} = \tau_{\mathrm{SEM\to Dec}} + \tau_{\mathrm{ML}} + \tau_{\mathrm{NASP}} + \tau_{\mathrm{BC}} + \tau_{\mathrm{SLA\text{-}Agent}}
\]

Sobre **60** amostras HTTP 200:

| Estágio | Média (ms) | Mediana (ms) | Partilha média em % de \(T_{\mathrm{full}}\) |
|---------|------------|--------------|-----------------------------------------------|
| SEM → decisão | ≈ 769,8 | ≈ 774,0 | ≈ **44,7** % |
| ML-NSMF (*predict*) | ≈ 2,4 | ≈ 2,5 | ≈ **0,14** % |
| NASP (orquestração HTTP) | ≈ 176,6 | ≈ 174,8 | ≈ **10,3** % |
| Blockchain (*register*) | ≈ 742,7 | ≈ 739,8 | ≈ **42,8** % |
| SLA-Agent (*ingest* HTTP) | ≈ 36,8 | ≈ 23,7 | ≈ **2,1** % |
| **Total** | ≈ **1728,3** | ≈ **1735** | 100 % |

A média de `elapsed_client_ms` foi ≈ **1842 ms**, superior a \(T_{\mathrm{full}}\) (*overhead* de rede e trabalho não capturado pela soma dos cinco temporizadores).

As **Figuras 6.B.4–6.B.7** materializam a decomposição.

### 6.3.3 Gargalo do sistema — interpretação (NASP *esperado*)

**Temporalmente**, predominam **SEM→decisão** e **blockchain** na partilha média de \(T_{\mathrm{full}}\). **Operacionalmente**, o **NASP** permanece o foco de *gargalo* **esperado**: *gates* 3GPP, disponibilidade de *pods*, respostas **HTTP 422** com *gate FAIL* mesmo quando o fluxo SLA continua — o *bottleneck* manifesta-se como **risco de orquestração**, não necessariamente como o maior termo médio isolado. A **Figura 6.B.9** ancora a relação entre duração NASP e \(T_{\mathrm{full}}\).

### 6.3.4 Estabilidade do sistema

- **PROMPT_48:** interpretação condicionada às falhas HTTP na campanha V1; nas amostras válidas, decisões estáveis.
- **PROMPT_58:** 60/60 HTTP 200; telemetria completa nas amostras válidas; *gates* de latência cumpridos — **robustez de instrumentação**.

A **Figura 6.B.8** relaciona pressão do *snapshot* com latência no cliente.

---

## 6.4 Discussão: pergunta de pesquisa, hipótese e evidência

A **pergunta principal (Secção 6.1.1)** é respondida **afirmativamente no perímetro experimental**: o sistema integra os estágios referidos, permite comparar V1 vs V2 sobre métricas derivadas da mesma API, e o PROMPT_58 prova a **mensurabilidade por módulo** com *gates* explícitos.

Relativamente à **hipótese** de que telemetria multi-fonte e políticas mais ricas aumentam a **fidelidade** da caracterização do estado do sistema, a evidência é **parcial e qualificada**: V2 desloca `resource_pressure` para médias superiores (maior sensibilidade às leituras disponíveis), sem alterar a decisão de admissão nas amostras válidas analisadas. O PROMPT_58 **reforça a credibilidade científica** ao fechar a lacuna em que só SEM+Decisão aparecia desagregado no CSV principal.

**Síntese oral sugerida para o júri:** “Mostrámos *o quê* muda na métrica quando se activa V2; mostrámos *onde* o tempo é gasto no *submit*; e separamos *tempo médio* de *risco de integração* no NASP.”

---

## 6.5 Limitações (síntese)

- Comparabilidade V1 vs V2 sujeita a **cardinalidades diferentes** na presença de erros HTTP só numa campanha.
- \(T_{\mathrm{full}}\) não esgota o tempo cliente-servidor.
- Estados **NASP ERROR** com latência positiva medem **tentativa**, não sucesso de instanciação.
- Ambiente **controlado**; extrapolações para *chaos* ou escala massiva são trabalho futuro.

---

## 6.6 Conclusão do capítulo

O capítulo integra dois corpos de evidência alinhados com a pergunta de investigação: (i) **comparativo de política** (PROMPT_48 + Grupo A); (ii) ***pipeline* instrumentado** (PROMPT_58 + Grupo B). Conclui-se que a TriSLA, nas condições reportadas, é **mensurável end-to-end**, **auditável por *flag* de política**, e **estável** no protocolo experimental, com o NASP como principal vetor de **risco operacional**, mesmo quando outros estágios dominam a média temporal.

---

## Referências de artefactos

| Artefacto | Caminho |
|-----------|---------|
| Dataset política V1/V2 | `evidencias/PROMPT48/07_dataset_final.csv` |
| Dataset *pipeline* completo | `evidencias/PROMPT58_PIPELINE_FULL/dataset_final_completo.csv` |
| Resumo *gates* PROMPT_58 | `evidencias/PROMPT58_PIPELINE_FULL/summary.json` |
| Figuras IEEE | `evidencias/PROMPT50_PIPELINE_COMPLETO/figures/` |
| Validação por figura | `evidencias/PROMPT50_PIPELINE_COMPLETO/validation/` |
| *Runner* E2E | `scripts/e2e/prompt21_multi_domain_validation.py` |

*Última revisão estrutural: PROMPT_60 (pergunta de pesquisa e preparação para defesa). Valores numéricos: médias sobre os CSVs indicados no repositório.*
