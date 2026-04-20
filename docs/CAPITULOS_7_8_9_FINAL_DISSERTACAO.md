# Capítulo 7 — Resultados, Análise e Discussão Experimental da TriSLA

## 7.1 Contextualização dos Resultados e Estratégia de Leitura

Os resultados desta pesquisa devem ser compreendidos como evidência empírica de uma arquitetura orientada a requisitos de SLA por tipo de slice, e não apenas como um conjunto de gráficos isolados.
A campanha V6.2 foi conduzida em ambiente realista de execução, com telemetria de múltiplos domínios e consolidação metodológica em pipeline reprodutível, garantindo rastreabilidade entre coleta, limpeza, análise e interpretação.
Esse cuidado metodológico é central para evitar uma leitura superficial dos números, sobretudo em um contexto no qual pequenas variações de carga e medição podem alterar o comportamento aparente de decisões automatizadas.
O foco analítico adotado neste capítulo combina três camadas complementares: sensibilidade quantitativa (slope), estrutura relativa de influência (importância por domínio) e consistência semântica do processo decisório.
Essa integração permite observar não apenas “se” o sistema muda suas decisões, mas “como” e “por que” essas mudanças emergem quando determinados domínios operacionais são perturbados.
Do ponto de vista científico, isso reduz o risco de inferências frágeis baseadas apenas em correlação pontual, pois incorpora relações de tendência, ponderações e alinhamento com o comportamento esperado para cada slice.
Além disso, os resultados são discutidos com uma postura interpretativa equilibrada, reconhecendo os achados fortes sem ocultar zonas de ambiguidade, especialmente em cenários onde a dinâmica de infraestrutura produz sinais menos lineares.
Assim, a narrativa deste capítulo busca refletir uma prática acadêmica madura, em que os ganhos da proposta são explicitados junto às suas limitações e implicações de uso em contexto de operação.
As figuras apresentadas a seguir foram selecionadas como núcleo da argumentação visual, por sintetizarem de forma convergente os fenômenos observados na campanha e seus desdobramentos para a tese.
A leitura recomendada é progressiva: primeiro sensibilidade por slice, depois síntese interdomínio, e por fim métricas agregadas de importância e coerência semântica.

## 7.2 Sensibilidade da TriSLA por Tipo de Slice

No caso URLLC, a expectativa teórica é que o processo decisório seja altamente sensível à latência e à variabilidade temporal de transporte, dado o caráter estrito desse perfil de serviço.
A observação dos resultados confirma uma queda de score associada ao agravamento das condições de transporte, ainda que em intensidade variável conforme o bloco de cenário e a qualidade de validação da amostra.
Esse comportamento é relevante porque indica que a arquitetura não está apenas reagindo de modo binário, mas modulando a decisão segundo um gradiente de condição operacional percebida.
Em termos práticos, isso significa maior capacidade de discriminação entre estados “aceitáveis”, “limítrofes” e “não recomendados”, o que fortalece a qualidade do controle SLA-aware.
Também se observa que a combinação entre RTT e jitter refina o diagnóstico de criticidade, evitando supervalorização de um único indicador quando o outro sugere estabilidade relativa.
Tal evidência dialoga com a literatura sobre slices críticos, na qual robustez de decisão depende da leitura contextual de múltiplos sinais de transporte e não de um único limiar estático.
No recorte eMBB, a variável PRB permanece estruturalmente dominante, refletindo a centralidade do domínio RAN para serviços com exigência de throughput e eficiência radio.
Mesmo quando o slope global se aproxima de neutralidade em alguns subconjuntos limpos, a hierarquia relativa de influência mantém o RAN na posição principal, preservando coerência arquitetural.
Para mMTC, os resultados reforçam o papel do domínio Core como eixo de contextualização de carga agregada, especialmente em regimes de pressão sobre memória e processamento.
Essa leitura por slice, portanto, sustenta a tese de que a TriSLA opera de forma multi-domínio com especialização funcional por perfil de serviço, e não por regra uniforme.

Antes da Figura 7.1, destaca-se que o gráfico de URLLC foi mantido como referência primária de sensibilidade de transporte, pois ele captura com clareza o comportamento do score frente à degradação de latência e jitter.
Essa figura permite observar a tendência média por bins e a dispersão das amostras, oferecendo uma visão simultânea de robustez e variabilidade.
Do ponto de vista argumentativo, sua posição inicial no capítulo serve para ancorar a interpretação de que requisitos estritos de tempo de resposta precisam de resposta decisória proporcional.
Também é nessa figura que se evidencia a utilidade de trabalhar com bandas de referência, pois elas facilitam a leitura do quanto o score se aproxima de regiões de aceitação ou rejeição.
A escolha desta visualização, portanto, não é estética, mas metodológica, por conectar comportamento estatístico e significado operacional.
Ao introduzi-la neste ponto, busca-se conduzir o leitor de um entendimento local (URLLC) para uma síntese posterior entre domínios.
Adicionalmente, a presença de duas projeções (RTT e jitter) evita interpretações simplistas baseadas em um único eixo temporal.
Isso ajuda a compreender por que uma mesma classe de serviço pode apresentar trajetórias distintas de score em função da natureza da perturbação.
Com isso, a figura cumpre papel didático e analítico simultaneamente.
A seguir, apresenta-se a evidência correspondente.

![Figura 7.1 — Sensibilidade URLLC a latência e jitter](../evidencias_resultados_trisla_baseline_v13_2/figures_ieee_v62_enhanced/v62_urllc_latency_sensitivity.png)

Antes da Figura 7.2, ressalta-se que o cenário eMBB exige leitura centrada em utilização de recursos radio, uma vez que o domínio RAN tende a concentrar o impacto sobre a qualidade percebida.
O gráfico selecionado evidencia tanto a relação entre score e PRB quanto a distribuição ordinal de decisões ao longo da carga.
Essa combinação é importante porque mostra não apenas tendência contínua, mas também a transição entre categorias de resposta do sistema.
Em termos de dissertação, essa figura apoia a argumentação de que a TriSLA preserva sensibilidade ao principal recurso de eMBB sem depender de gatilhos artificiais.
Mesmo quando há suavização de slope em parte do conjunto limpo, a estrutura visual mantém a leitura de dominância funcional do RAN.
Isso é compatível com a noção de controle semântico contextual: nem toda variação precisa gerar resposta abrupta, mas deve ser absorvida de forma coerente com o perfil do serviço.
A introdução desta figura neste ponto também prepara a transição para métricas de importância relativa, apresentadas mais adiante.
Assim, o leitor consegue ligar fenômeno local, medida quantitativa e síntese entre slices.
A visualização ainda contribui para discutir estabilidade de decisão em faixas intermediárias de carga.
Segue a figura correspondente.

![Figura 7.2 — Sensibilidade eMBB ao uso de PRB](../evidencias_resultados_trisla_baseline_v13_2/figures_ieee_v62_enhanced/v62_embb_ran_resource_sensitivity.png)

Antes da Figura 7.3, convém destacar que o slice mMTC, por sua natureza massiva, tende a refletir efeitos de acumulação de contexto no domínio Core, sobretudo sob pressão de memória e CPU.
A figura apresentada permite analisar se o score mantém trajetória coerente quando os recursos de backend sofrem incremento de consumo.
Do ponto de vista científico, esse recorte é crucial para evitar conclusões indevidas de que o comportamento em URLLC ou eMBB se generaliza automaticamente para mMTC.
Os resultados mostram uma dinâmica mais heterogênea, o que é esperado em cenários de agregação e concorrência de múltiplas demandas.
Essa heterogeneidade não invalida a proposta; ao contrário, sugere que a arquitetura está respondendo a um espaço de estados mais complexo.
Ao introduzir a figura, reforça-se que a interpretação deve considerar a topologia de validação das amostras e a interação entre controle de cenário e telemetria observada.
Em especial, o comportamento de memória aparece como sinal forte de influência relativa, o que será confirmado nas métricas de importância.
A visualização também contribui para discutir limites de linearidade do score frente a recursos de Core.
Por essa razão, sua leitura deve ser integrada às métricas híbridas e semânticas mostradas nas próximas seções.
Apresenta-se, então, a figura correspondente.

![Figura 7.3 — Sensibilidade mMTC a recursos de Core](../evidencias_resultados_trisla_baseline_v13_2/figures_ieee_v62_enhanced/v62_mmtc_core_resource_sensitivity.png)

## 7.3 Síntese Interdomínio: Correlação, Hibridização e Dominância

A análise interdomínio representa o ponto de convergência do capítulo, pois permite comparar, no mesmo espaço visual, a força relativa de cada domínio em cada tipo de slice.
Ao combinar correlação com slope normalizado, o heatmap híbrido reduz o risco de decisões analíticas baseadas somente em associação linear simples.
Essa estratégia é particularmente útil quando um domínio apresenta alta correlação, mas baixa variação efetiva de tendência, ou vice-versa.
O escore híbrido, portanto, atua como métrica de compromisso entre proximidade estatística e intensidade de resposta.
Em termos de contribuição, isso qualifica a inferência de “influência”, tornando-a menos sensível a ruídos localizados.
Além disso, a comparação entre slices na mesma matriz favorece uma leitura sistêmica da arquitetura, evidenciando especialização por contexto de serviço.
Ao longo da campanha V6.2, essa síntese reforçou a interpretação de que não existe um único domínio universalmente dominante, mas sim domínios prioritários por perfil.
Essa conclusão é coerente com o objetivo central da TriSLA de operar de forma semanticamente condicionada.
A leitura da matriz também ajuda a identificar regiões de baixa influência, úteis para decisões futuras de simplificação de monitoramento.
Com isso, a dissertação avança de descrição para explicação, apoiada em métrica composta e visualização comparativa.

Antes da Figura 7.4, destaca-se que o heatmap híbrido foi escolhido como visual central da seção por integrar duas dimensões analíticas que, isoladamente, poderiam levar a interpretações incompletas.
A introdução desta figura neste momento busca consolidar tudo o que foi discutido sobre sensibilidade local em uma visão de arquitetura completa.
Ela permite reconhecer, de forma imediata, quais domínios concentram influência por slice e onde há participação secundária.
No contexto acadêmico, essa representação fortalece o rigor da análise ao explicitar os critérios de composição do score híbrido.
Também contribui para transparência metodológica, pois a construção do mapa está vinculada a artefatos de métricas exportáveis.
A presença de um título explícito de influência normalizada ajuda a evitar leituras absolutistas de causalidade.
Do ponto de vista didático, a figura funciona como ponte entre resultados quantitativos e implicações de projeto de observabilidade.
Ela ainda facilita a discussão de prioridades para evolução futura de policy e instrumentação.
Assim, sua inclusão é decisiva para a narrativa de consolidação experimental.
A seguir, apresenta-se a figura.

![Figura 7.4 — Influência híbrida normalizada por domínio e slice](../evidencias_resultados_trisla_baseline_v13_2/figures_ieee_v62_enhanced/v62_slice_domain_influence_heatmap.png)

Antes da Figura 7.5, cabe introduzir a visualização de importância relativa como um complemento interpretativo ao heatmap, agora em escala intra-slice.
Enquanto a matriz híbrida prioriza comparação global, este gráfico evidencia o peso proporcional de cada domínio dentro do próprio slice.
Esse deslocamento de perspectiva é importante para evitar que magnitudes de um slice sobreponham a leitura dos demais.
No caso de URLLC, por exemplo, a partilha entre RTT e jitter torna visível que o transporte não é monolítico.
Para eMBB, a concentração em PRB confirma a centralidade esperada do domínio RAN.
Em mMTC, a predominância de memória explicita um padrão de carga no Core que merece atenção específica de engenharia.
A introdução desta figura neste ponto fortalece a consistência entre achados de slope, híbrido e dominância.
Além disso, oferece um indicador intuitivo para comunicação dos resultados a públicos não especialistas em estatística.
Com isso, a dissertação ganha clareza sem perder rigor.
Segue a figura correspondente.

![Figura 7.5 — Importância relativa por domínio em cada slice](../evidencias_resultados_trisla_baseline_v13_2/figures_ieee_v62_enhanced/v62_relative_domain_importance.png)

Antes da Figura 7.6, ressalta-se que o gráfico de domínio dominante serve como resumo executivo da análise de sensibilidade, destacando o principal vetor de decisão por perfil.
Essa figura não substitui a granularidade dos gráficos anteriores, mas sintetiza o resultado de forma objetiva para apoiar conclusões de alto nível.
Sua utilidade acadêmica está em facilitar a conexão entre evidência estatística e interpretação arquitetural.
Ao identificar um domínio dominante por slice, ela reafirma a hipótese de especialização semântica da TriSLA.
No entanto, é importante interpretar essa dominância como tendência principal e não como exclusividade causal.
A presença de domínios secundários continua relevante para robustez e refinamento de resposta.
Ao inserir esta figura após importância relativa, o texto mantém coerência de escala: do detalhamento para a síntese.
Essa ordem também favorece a compreensão do leitor sobre como diferentes métricas convergem.
Portanto, trata-se de uma figura de fechamento da análise interdomínio.
Apresenta-se, então, a evidência visual.

![Figura 7.6 — Domínio dominante por tipo de slice](../evidencias_resultados_trisla_baseline_v13_2/figures_ieee_v62_enhanced/v62_slice_dominant_domain.png)

## 7.4 Coerência Semântica do Processo Decisório

A coerência semântica foi avaliada para responder uma questão central da tese: as decisões do sistema acompanham, em direção e intensidade, o significado operacional das métricas observadas?
Para isso, utilizou-se uma formulação ponderada que atribui maior peso a amostras com variação simultaneamente relevante de métrica e score.
Esse desenho evita que pequenos ruídos tenham o mesmo impacto de mudanças estruturalmente importantes.
Em comparação com métricas puramente não ponderadas, a abordagem adotada melhora a aderência entre interpretação estatística e significado de negócio.
Os resultados mostram níveis mais altos para URLLC, intermediários para eMBB e moderados para mMTC, quadro coerente com a complexidade relativa dos cenários.
No caso mMTC, a redução da consistência ponderada não deve ser lida como falha isolada, mas como indício de dinâmica operacional mais multifatorial.
Isso abre espaço para evolução metodológica futura com modelos não lineares e critérios semânticos mais ricos.
Ainda assim, mesmo com variação entre slices, o conjunto evidencia que a TriSLA preserva alinhamento semântico em parte substancial das decisões.
Tal resultado fortalece a contribuição da arquitetura ao demonstrar governança decisória orientada por contexto.
Assim, a consistência semântica emerge como eixo de validação tão importante quanto a própria sensibilidade métrica.

Antes da Figura 7.7, é importante esclarecer que o gráfico apresentado não mede apenas frequência de acerto direcional, mas acoplamento semântico ponderado entre desvio de métrica e resposta do sistema.
Essa distinção é fundamental para uma leitura acadêmica correta, pois evita equiparar “consistência” a mera concordância ordinal.
A visualização permite comparar rapidamente os três slices sob um critério homogêneo de ponderação.
No contexto desta pesquisa, ela funciona como verificação final de que os comportamentos observados nos gráficos de sensibilidade não são artefatos isolados.
Ao posicioná-la no fechamento do capítulo, reforça-se seu papel de síntese qualitativa da coerência do processo.
Além disso, a figura contribui para explicitar onde há maior oportunidade de calibração futura, especialmente no domínio Core para mMTC.
Essa abordagem transparente é alinhada à prática científica responsável, que reconhece avanços e lacunas com a mesma objetividade.
A inclusão da figura, portanto, consolida a narrativa de validação multidimensional da TriSLA.
Com ela, conclui-se a apresentação dos resultados centrais da campanha V6.2.
A seguir, a figura correspondente.

![Figura 7.7 — Consistência semântica ponderada por slice](../evidencias_resultados_trisla_baseline_v13_2/figures_ieee_v62_enhanced/v62_semantic_consistency_weighted.png)

## 7.5 Síntese do Capítulo

Este capítulo demonstrou, por meio de evidências quantitativas e visuais convergentes, que a arquitetura TriSLA opera com comportamento sensível ao contexto de slice e ao domínio operacional predominante.
A análise por URLLC, eMBB e mMTC mostrou padrões distintos, mas coerentes com a expectativa teórica de especialização semântica em ambientes 5G multi-domínio.
A introdução de métricas de importância relativa e consistência ponderada ampliou o poder explicativo dos resultados para além de correlação simples.
Com isso, foi possível sustentar uma interpretação mais robusta da lógica decisória, reduzindo risco de conclusões baseadas em sinais estatísticos frágeis.
O heatmap híbrido consolidou essa leitura ao integrar associação e tendência em uma matriz comparável entre slices.
As figuras apresentadas, introduzidas de forma contextualizada, funcionaram como suporte argumentativo estruturante para a narrativa experimental.
Ao mesmo tempo, os achados evidenciaram limites relevantes, principalmente em cenários de maior complexidade dinâmica, como parte do comportamento observado em mMTC.
Longe de enfraquecer a proposta, tais limites indicam fronteiras legítimas para evolução de modelagem, instrumentação e política de controle.
Portanto, os resultados deste capítulo não apenas validam a hipótese principal da pesquisa, mas também delineiam uma agenda objetiva de amadurecimento técnico-científico.
Com essa base, o capítulo seguinte discute implicações, contribuições e restrições da abordagem no contexto mais amplo da área.

---

# Capítulo 8 — Implicações, Contribuições e Limitações da Proposta

## 8.1 Contribuições Científicas e Tecnológicas

A principal contribuição desta dissertação reside na demonstração de uma arquitetura de decisão SLA-aware que integra observabilidade multi-domínio, semântica de slices e governança operacional em fluxo reprodutível.
Essa integração supera abordagens fragmentadas nas quais métricas são tratadas como sinais independentes, sem vínculo explícito com o significado do serviço solicitado.
Do ponto de vista científico, a proposta avança ao combinar evidências de sensibilidade, importância relativa e coerência semântica ponderada em uma moldura analítica unificada.
Isso permite discutir comportamento do sistema em termos de adequação contextual, e não apenas de desempenho médio.
No plano tecnológico, a pesquisa também entrega artefatos práticos de campanha, análise e empacotamento final que facilitam auditoria e replicação em ambientes correlatos.
A adoção de pipeline estruturado desde coleta até visualização reduz dependência de ajustes manuais e aumenta confiabilidade do processo experimental.
Outro ganho é a explicabilidade operacional: a arquitetura não apenas decide, mas oferece sinais interpretáveis sobre quais domínios influenciam cada resposta.
Essa característica é valiosa para cenários de produção, onde decisões automáticas precisam ser justificáveis perante equipes de engenharia e governança.
Portanto, a contribuição não se limita ao resultado numérico, abrangendo método, instrumentação e capacidade de interpretação aplicada.
Em síntese, a TriSLA se apresenta como proposta tecnicamente viável e cientificamente relevante para gestão de SLA em redes 5G com múltiplos contextos de serviço.

## 8.2 Implicações para Operação em Ambientes 5G

Os achados desta dissertação têm implicações diretas para operação de redes 5G orientadas por qualidade de serviço, especialmente em ambientes onde coexistem perfis heterogêneos de tráfego.
Primeiramente, a evidência de dominância contextual por slice sugere que políticas de controle devem ser adaptativas e sensíveis ao domínio prioritário de cada cenário.
Em termos práticos, isso implica priorizar telemetria e intervenção de transporte em URLLC, radio em eMBB e recursos de Core em mMTC, sem perder visão sistêmica.
A segunda implicação é metodológica: avaliações de SLA-aware precisam combinar métricas de associação e tendência para evitar diagnósticos simplificados.
A terceira é de governança: decisões automáticas devem ser auditáveis por meio de artefatos padronizados, permitindo reconstrução posterior de evidências.
Essa necessidade se torna ainda mais crítica em ambientes regulados ou de missão crítica, onde explicabilidade e rastreabilidade são requisitos institucionais.
Além disso, a variação observada na consistência semântica entre slices indica que modelos uniformes de validação podem mascarar diferenças relevantes de comportamento.
Assim, recomenda-se que operadores adotem critérios de qualidade segmentados por perfil de serviço, em vez de métricas globais únicas.
Finalmente, os resultados reforçam que maturidade operacional em 5G depende da convergência entre engenharia de dados, observabilidade e desenho de política decisória.
Essa convergência, quando formalizada em pipeline reprodutível, reduz risco operacional e fortalece capacidade de evolução contínua.

## 8.3 Limitações da Pesquisa

Como toda investigação empírica aplicada, esta pesquisa apresenta limitações que devem ser explicitadas para preservar rigor científico e orientar leituras responsáveis dos resultados.
A primeira limitação refere-se à dependência de condições de infraestrutura no momento da campanha, que podem influenciar magnitude de slopes e taxas de validade das amostras.
A segunda diz respeito ao caráter predominantemente linear das métricas principais de sensibilidade, que pode sub-representar comportamentos não lineares em cenários de saturação.
A terceira limitação está na própria definição de consistência semântica, que, embora robusta e ponderada, ainda simplifica fenômenos multidimensionais em uma medida agregada.
Também é necessário reconhecer que a distribuição de cenários, apesar de ampla, não cobre todas as combinações possíveis de falha, concorrência e instabilidade temporal.
Adicionalmente, parte dos efeitos observados em mMTC sugere interação entre fatores de Core que mereceria modelagem causal mais profunda.
Outra limitação prática é a sensibilidade do experimento a alinhamento temporal entre coleta de métricas e resposta do sistema, tema recorrente em ambientes distribuídos.
Isso não invalida os achados, mas recomenda prudência ao extrapolar resultados para contextos operacionais com características muito distintas.
Do ponto de vista de dissertação, explicitar essas limitações fortalece a credibilidade do trabalho ao demonstrar consciência dos seus próprios contornos.
Assim, os resultados devem ser entendidos como evidência sólida em um escopo bem definido, e não como verdade universal independente de contexto.

## 8.4 Ameaças à Validade e Estratégias de Mitigação

As ameaças à validade interna foram tratadas com a separação entre dataset bruto e limpo, uso de critérios explícitos de validade e preservação de trilha completa de execução.
Essa estratégia reduz impacto de amostras inconsistentes e permite verificar quanto cada filtro afeta o resultado final.
No plano da validade de construto, a pesquisa mitigou ambiguidades ao definir claramente o que se entende por influência, sensibilidade e coerência semântica.
A inclusão de métrica híbrida e de ponderação por desvio contribuiu para aproximar os indicadores do fenômeno que se pretende medir.
Quanto à validade externa, reconhece-se que a generalização depende de similaridade de contexto operacional, especialmente em relação ao comportamento de telemetria e carga.
Ainda assim, a estrutura metodológica pode ser reproduzida em outros ambientes, preservando comparabilidade de processo mesmo quando os valores absolutos mudam.
A validade de conclusão foi reforçada com múltiplas lentes analíticas convergentes, reduzindo dependência de um único indicador.
Também se adotou postura interpretativa conservadora em cenários de sinal fraco, evitando inferências categóricas sem suporte consistente.
Essas medidas não eliminam todas as ameaças, mas elevam substancialmente a robustez do estudo.
Em conjunto, elas sustentam a confiança de que as conclusões apresentadas refletem fenômenos reais observados na campanha.

## 8.5 Síntese do Capítulo

O capítulo evidenciou que as contribuições da pesquisa vão além de um experimento pontual, alcançando uma proposta metodológica e tecnológica para avaliação SLA-aware em arquitetura multi-domínio.
Também mostrou que os resultados têm implicações práticas relevantes para operação 5G, sobretudo na necessidade de governança contextual por tipo de slice.
As limitações e ameaças à validade foram tratadas com transparência, preservando uma postura acadêmica equilibrada entre confiança nos achados e cautela de extrapolação.
Essa postura é importante para manter o trabalho intelectualmente honesto e cientificamente útil para a comunidade.
Ao reconhecer zonas de incerteza, a dissertação evita triunfalismo e abre caminho para pesquisa incremental de alto valor.
Além disso, a explicitação de mitigadores metodológicos oferece um roteiro replicável para investigações futuras.
Com isso, o capítulo consolida a maturidade analítica do trabalho e prepara o terreno para conclusões finais consistentes.
O encadeamento entre contribuição, implicação e limitação reforça a coerência interna da tese.
Esse encadeamento também contribui para posicionar a TriSLA como base evolutiva, e não artefato fechado.
No capítulo seguinte, são apresentadas as conclusões finais e a agenda de trabalhos futuros.

---

# Capítulo 9 — Conclusões e Trabalhos Futuros

## 9.1 Conclusões Gerais da Dissertação

Esta dissertação teve como objetivo investigar e validar uma abordagem SLA-aware para tomada de decisão em ambiente 5G multi-domínio, com foco na adequação contextual por tipo de slice.
Os resultados obtidos confirmam, no escopo experimental definido, que a arquitetura TriSLA responde de forma diferenciada e semanticamente orientada aos perfis URLLC, eMBB e mMTC.
A combinação de métricas de slope, importância relativa, influência híbrida e consistência semântica ponderada permitiu construir uma validação robusta e multifacetada.
Com isso, superou-se a limitação de análises baseadas apenas em correlações isoladas ou médias globais pouco informativas.
Também foi demonstrado que a reprodutibilidade do processo é viável por meio de pipeline estruturado de coleta, limpeza, análise, visualização e empacotamento de artefatos.
Esse aspecto é central para credibilidade acadêmica e para adoção prática em contextos de engenharia de rede.
Do ponto de vista teórico-aplicado, a pesquisa contribui ao aproximar semântica de serviço e telemetria operacional em um processo decisório auditável.
Assim, a hipótese principal da dissertação é suportada: a TriSLA apresenta comportamento coerente com o conceito de decisão orientada a SLA por slice.
Ao mesmo tempo, os resultados revelam que tal coerência não é uniforme em todos os cenários, exigindo calibração contínua e leitura contextual.
Portanto, conclui-se que a proposta é tecnicamente promissora, cientificamente consistente e operacionalmente evolutiva.

## 9.2 Resposta aos Objetivos Específicos

Em relação ao objetivo de construir um protocolo experimental rastreável, a pesquisa entregou um fluxo completo com artefatos verificáveis em cada etapa.
Quanto ao objetivo de medir sensibilidade por domínio e slice, os gráficos e métricas evidenciaram padrões distintos e interpretáveis entre URLLC, eMBB e mMTC.
No objetivo de sintetizar influência entre domínios, o heatmap híbrido mostrou-se instrumento adequado para comparação estruturada e tomada de decisão analítica.
Para o objetivo de validar coerência semântica, a métrica ponderada trouxe maior aderência entre relevância de variação e significado do comportamento decisório.
No objetivo de gerar resultados utilizáveis para redação acadêmica e auditoria técnica, o pacote final de evidências foi consolidado com dados, figuras e métricas.
Dessa forma, os objetivos específicos não apenas foram alcançados, mas articulados em uma narrativa metodológica única.
A principal força dessa articulação está na convergência entre evidência quantitativa, interpretação contextual e documentação reprodutível.
Isso reduz lacunas entre “prova estatística” e “significado operacional”, aspecto frequentemente negligenciado em estudos aplicados.
Além disso, o trabalho oferece base concreta para extensão em cenários mais amplos de rede e governança de SLA.
Assim, a resposta aos objetivos confirma a coerência interna da proposta e a contribuição efetiva da dissertação.

## 9.3 Agenda de Trabalhos Futuros

Como continuidade natural desta pesquisa, recomenda-se investigar modelos não lineares de sensibilidade para capturar regimes complexos de saturação e transição entre estados operacionais.
Também é pertinente evoluir a métrica de consistência semântica para versões multivariadas, incorporando interações explícitas entre domínios.
Outra frente promissora é integrar análise temporal mais fina, com janelas dinâmicas e alinhamento causal entre evento de carga, telemetria e decisão.
No plano de engenharia, vale expandir a campanha para ambientes com maior diversidade de topologias, perfis de tráfego e mecanismos de controle RAN.
Adicionalmente, a adoção de técnicas de explainable AI pode aprofundar a interpretabilidade de decisões em cenários de baixa linearidade.
Para fortalecer validade externa, recomenda-se replicar o protocolo em múltiplos clusters e condições de infraestrutura, comparando estabilidade dos indicadores.
Uma agenda relevante é investigar thresholds adaptativos por slice, substituindo bandas estáticas por políticas aprendidas com restrições operacionais.
Também se sugere avaliar impacto de atrasos de observabilidade na qualidade decisória, tema crítico em sistemas distribuídos de missão contínua.
Esses avanços podem transformar a TriSLA em plataforma de referência para governança inteligente de SLA em ecossistemas 5G e futuros ambientes 6G.
Em síntese, os trabalhos futuros devem preservar a base reprodutível deste estudo, ampliando profundidade analítica e abrangência de aplicação.

## 9.4 Encerramento

A trajetória desta dissertação evidencia que decisões de SLA em redes modernas não podem ser tratadas como um problema estritamente estatístico nem puramente operacional.
Elas exigem integração entre semântica de serviço, leitura contextual de domínios e disciplina metodológica de validação.
Foi justamente essa integração que orientou o desenvolvimento, a execução e a análise da campanha V6.2 apresentada neste trabalho.
Os resultados obtidos demonstram viabilidade da proposta e sinalizam potencial de impacto real em ambientes de gestão de rede orientada a qualidade.
Ao mesmo tempo, o estudo mantém compromisso com prudência científica, reconhecendo limites e apontando caminhos concretos de evolução.
Esse equilíbrio entre assertividade e cautela é essencial para que a contribuição seja sólida no presente e fértil para pesquisa futura.
Do ponto de vista humano e profissional, a pesquisa também reforça que sistemas automáticos de decisão precisam ser transparentes, auditáveis e alinhados a objetivos de serviço claramente definidos.
Nesse sentido, a TriSLA representa não apenas um artefato técnico, mas uma proposta de governança decisória contextualizada.
Conclui-se, portanto, que a abordagem aqui consolidada oferece base consistente para avanço do estado da arte em SLA-aware orchestration.
Com isso, encerra-se a dissertação com contribuição efetiva, agenda de continuidade e compromisso com evolução responsável.
