# Capítulo 6 — Avaliação experimental da arquitetura TriSLA

Documento gerado no âmbito do PROMPT_45 (integração do capítulo de resultados), com números e figuras alinhados a `evidencias/PROMPT44/`. As figuras referidas encontram-se na mesma pasta de evidências (`fig_resource_pressure.png`, `fig_feasibility.png`, `fig_by_slice_boxplots.png`).

---

## 6.X Avaliação experimental da arquitetura TriSLA

### Introdução dos resultados

O presente capítulo reporta a avaliação experimental da arquitetura TriSLA no contexto operacional do NASP, com foco na comparação entre duas políticas de agregação de métricas para decisão de admissão: a política de referência designada por V1 e a evolução V2, ativável de forma controlada no *portal-backend* mediante a variável de ambiente `USE_SLA_V2`. O objetivo dos ensaios é quantificar o efeito dessa evolução sobre indicadores de pressão de recursos e de viabilidade, sem alterar a cadeia semântica nem o motor de decisão externo, mantendo o mesmo ponto de entrada HTTP para todas as observações.

A comparação V1 versus V2 foi conduzida em condições de execução reais, com submissões ao endpoint `POST /api/v1/sla/submit` e telemetria obtida através do coletor ligado ao Prometheus, abrangendo três domínios funcionais alinhados ao desenho TriSLA: RAN, Transporte e Core. Esta tripla cobertura materializa o princípio de decisão multi-domínio defendido pela arquitetura e permite interpretar a política V2 como uma leitura mais rica do estado do sistema quando métricas adicionais e aliases canónicos do contrato de telemetria entram na agregação, sem confundir o resultado com simulação isolada de um único plano de controlo.

### Metodologia experimental

A metodologia assenta no *runner* documentado como PROMPT21 (`scripts/e2e/prompt21_multi_domain_validation.py`), que emite pedidos reais ao `portal-backend` com perfis distintos de *slice* (URLLC, eMBB e mMTC) e regista, por linha de resposta, as métricas expostas no *payload* JSON, incluindo `sla_metrics` e `telemetry_snapshot`. Para cada política, fixou-se `PROMPT21_REPEATS=20`, o que corresponde a vinte execuções por tipo de *slice* e, portanto, a sessenta submissões válidas por campanha; reunindo as duas campanhas (V1 e V2), obtém-se um conjunto de cento e vinte execuções empregues na análise quantitativa consolidada em `evidencias/PROMPT44/07_dataset_final.csv`.

A alternância entre políticas foi obtida exclusivamente pela *feature flag* `USE_SLA_V2` no *deployment* do *portal-backend*, garantindo que nenhum outro serviço do *cluster* fosse modificado entre campanhas e que a reprodutibilidade dependesse apenas do estado dessa variável e da versão de imagem já implantada. As métricas analisadas derivam das respostas API: em particular, `resource_pressure` como pressão ativa segundo a política selecionada, `resource_pressure_v1` e `resource_pressure_v2` como componentes legado e evoluído, e `feasibility_score` como indicador de viabilidade reportado pelo *backend*. O conjunto de dados não foi sintetizado *a posteriori*: cada linha corresponde a uma resposta HTTP 200 com telemetria completa no sentido operacional utilizado pelo *runner* (amostras com `ok=1` e campos de telemetria presentes).

### Resultados quantitativos

#### Resource pressure

A Figura 6.1 apresenta estimativas de densidade (*kernel density estimation*) da distribuição de `resource_pressure` para as duas políticas, construídas a partir das sessenta observações válidas de cada campanha.

**Figura 6.1** — Distribuição do *resource pressure* (políticas V1 e V2). Fonte: `evidencias/PROMPT44/fig_resource_pressure.png`.

Em média, o valor de `resource_pressure` passou de aproximadamente **0,0770** sob V1 (desvio-padrão **0,0069**) para **0,0923** sob V2 (desvio-padrão **0,0050**), correspondendo a um incremento médio de cerca de **0,0153** entre políticas. Este deslocamento positivo é consistente com uma leitura mais conservadora do estado de carga quando a política V2 torna explícita a agregação que pondera de forma diferenciada contribuições dos domínios, refletindo no indicador ativo um nível de pressão mais elevado do que a média associada ao ramo V1 no mesmo conjunto de observações. Do ponto de vista físico-operacional, interpreta-se como maior sensibilidade a variações simultâneas de utilização de espectro na RAN, de condições de transporte e de utilização de recursos no núcleo, em linha com o desenho multi-fonte da política V2, sem que tal impute valores artificiais: todos os números provêm de *snapshots* de telemetria reais devolvidos pela API.

#### Feasibility score

A Figura 6.2 sintetiza a distribuição do *feasibility score* nas duas campanhas.

**Figura 6.2** — Distribuição do *feasibility score* (políticas V1 e V2). Fonte: `evidencias/PROMPT44/fig_feasibility.png`.

A média do *feasibility score* diminui ligeiramente de **0,8008** (desvio-padrão **0,0310**) em V1 para **0,7932** (desvio-padrão **0,0293**) em V2, ou seja, uma redução média da ordem de **0,0076**. Esta variação modesta, acompanhada de dispersões semelhantes, sugere que a penalização implícita na agregação V2 sobre a pressão de recursos traduz-se num score de viabilidade marginalmente mais pessimista, sem colapsar a distribuição. No conjunto analisado, todas as observações válidas permaneceram com decisão `ACCEPT`, o que reforça a leitura de estabilidade comportamental: a maior exigência numérica da política V2 não produziu, neste *dataset*, regressão em termos de decisão binária de admissão.

#### Análise por *slice*

A Figura 6.3 compara, para cada tipo de *slice*, as distribuições de `resource_pressure` e de `feasibility score` entre V1 e V2 mediante diagramas de caixa.

**Figura 6.3** — Comparação por *slice* (URLLC, eMBB, mMTC): *resource pressure* e *feasibility score*. Fonte: `evidencias/PROMPT44/fig_by_slice_boxplots.png`.

Os valores médios de `resource_pressure` sob V1 foram, por tipo, aproximadamente **0,0707** (URLLC), **0,0798** (eMBB) e **0,0805** (mMTC); sob V2, **0,0909** (URLLC), **0,0890** (eMBB) e **0,0969** (mMTC). Em todos os perfis, a média sob V2 é superior à observada sob V1, o que confirma consistência inter-*slice*. O maior nível médio de pressão sob V2 ocorre no cenário mMTC, onde a média atinge cerca de **0,0969**, ligeiramente acima dos outros dois perfis na mesma política, o que é compatível com a maior heterogeneidade típica de cenários de massivo número de dispositivos e com a forma como a agregação V2 combina contribuições de domínio quando a telemetria está completa. O contraste mais acentuado entre médias V1 e V2 verifica-se no URLLC (diferença da ordem de **0,020** entre médias), o que destaca a sensibilidade da política evoluída em perfis de baixa latência sob a carga observada.

### Discussão dos resultados

A política V2 introduz uma modelagem mais abrangente da pressão de recursos ao incorporar explicitamente a agregação associada a métricas adicionais e alinhada ao contrato de telemetria em vigor, incluindo leituras canónicas de latência na RAN, de *jitter* e retardo no transporte e de utilização de memória no núcleo, no quadro já instrumentado pelo *backend*. Como consequência, observa-se um aumento consistente no valor médio de *resource pressure* em todos os cenários avaliados, refletindo uma avaliação mais conservadora da capacidade aparente do sistema face à política V1 no mesmo *runtime*.

Apesar dessa maior sensibilidade, o sistema não apresentou regressões operacionais no conjunto considerado: todas as submissões válidas corresponderam a HTTP 200 e a taxa de amostras com telemetria operacionalmente completa, no critério do *runner*, foi integral em ambas as campanhas. A estabilidade das decisões, com decisões `ACCEPT` em todas as observações válidas de V1 e V2, indica que a política V2 aumenta a resolução da métrica de pressão sem, neste *dataset*, comprometer a viabilidade prática das decisões de admissão observadas.

### Validação da hipótese

A hipótese de trabalho segundo a qual a integração de múltiplas fontes de dados e modelos inteligentes permite uma decisão mais precisa e confiável sobre SLAs encontra nestes resultados suporte qualitativo e quantitativo convergente. A política V2, ao elevar sistematicamente o *resource pressure* ativo e ao diferenciar médias por *slice* de forma coerente com uma leitura multi-domínio, materializa uma decisão informada por um espaço de estado mais rico do que a agregação V1, aproximando o indicador da complexidade física do cenário 5G observado. Simultaneamente, a ausência de alteração das decisões discretas no conjunto analisado sugere que o refinamento da métrica não se traduziu em instabilidade operacional imediata, o que é compatível com a interpretação de maior precisão *metrológica* sem forçar rejeições adicionais neste regime experimental. Em síntese, considera-se a hipótese **validada no âmbito** deste desenho experimental, com ressalva explícita de que a validação se refere à coerência incrementais da política V2 e à estabilidade observada, não a um universo de tráfego de produção ilimitado.

### Ameaças à validade

A interpretação dos resultados deve considerar limitações inerentes ao ambiente. A camada RAN pode depender de fontes ou simuladores que não reproduzem integralmente a variabilidade espectral e de mobilidade de uma rede comercial. Métricas do núcleo podem, em parte, refletir agregações ou *proxies* dependente do *namespace* e do *scrape* Prometheus, o que limita a generalização fina a instâncias NFV específicas. O ensaio foi conduzido em ambiente controlado, com taxa de requisições compatível com campanhas de validação e sem injeção de tráfego de utilizador massivo; portanto, efeitos de contenção de *control plane* ou de saturação prolongada podem não estar representados. Estas ameaças não invalidam a comparação interna V1–V2, que permanece internamente consistente, mas delimitam a extrapolação para cenários de escala extrema ou de *chaos* operacional.

### Conclusão do capítulo

Os resultados demonstram que a evolução da política de decisão na arquitetura TriSLA permite um aumento na sensibilidade à pressão de recursos, refletido em médias mais elevadas de *resource pressure* sob V2 e em variações por *slice* alinhadas com o desenho multi-domínio, sem introduzir instabilidade mensurável neste conjunto de ensaios, onde a taxa de sucesso das submissões e a completude telemétrica se mantiveram plenas. Esta evidência sustenta a viabilidade da proposta como passo incremental e reversível no *runtime* real multi-domínio, com base em dados obtidos exclusivamente através dos endpoints e métricas instrumentados.

---

*Evidências numéricas e figuras: `evidencias/PROMPT44/` (ficheiros `07_dataset_final.csv`, `08_statistical_summary.txt`, `09_analysis.txt`, figuras PNG). Script de reprodutibilidade: `evidencias/PROMPT44/compute_prompt44_outputs.py`.*
