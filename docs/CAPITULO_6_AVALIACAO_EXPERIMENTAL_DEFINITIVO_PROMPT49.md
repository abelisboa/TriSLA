# Capítulo 6 — Avaliação experimental (versão definitiva)

Documento alinhado ao **PROMPT_48** (`evidencias/PROMPT48/`) e consolidado no **PROMPT_49**. Os valores numéricos reportados correspondem a médias calculadas sobre as amostras com resposta válida (`ok=1`), tal como em `09_analysis.txt`. Figuras finais (300 dpi, tipografia serif, eixos com unidade ou escala explícita): `evidencias/PROMPT49/fig1_resource_pressure_v1_v2.png`, `fig2_feasibility_v1_v2.png`, `fig3_boxplot_by_slice.png`.

---

## 6.1 Enquadramento experimental

A avaliação experimental da arquitetura TriSLA foi conduzida no *runtime* NASP, com submissões reais ao endpoint `POST /api/v1/sla/submit` e telemetria multi-domínio (RAN, Transporte, Core) materializada no `metadata.telemetry_snapshot` conforme o contrato V2. A comparação entre políticas de agregação SLA **V1** e **V2** foi obtida ativando exclusivamente a *feature flag* `USE_SLA_V2` no *deployment* do *portal-backend*, mantendo inalterados os restantes serviços e a mesma versão de imagem em ambas as campanhas.

O *runner* `prompt21_multi_domain_validation.py` gerou, para cada política, sessenta pedidos determinísticos (vinte repetições por cada um dos perfis URLLC, eMBB e mMTC). A métrica ativa de pressão de recursos (`resource_pressure`) e o *feasibility score* foram extraídos diretamente do *payload* JSON de resposta, sem pós-processamento que altere valores numéricos.

## 6.2 Resultados quantitativos principais

Sobre as amostras válidas, a média de **resource pressure** foi de aproximadamente **0,0740** sob a política V1 e **0,0928** sob a política V2, correspondendo a um incremento médio **Δ ≈ +0,01874** entre V2 e V1. O **feasibility score** apresentou médias de cerca de **0,7984** (V1) e **0,7929** (V2), ou seja, **Δ ≈ −0,00545**. Estas diferenças encontram-se visualmente sintetizadas nas Figuras 6.1 e 6.2.

A Figura 6.3 complementa a análise com distribuições por tipo de *slice*, permitindo verificar a coerência do comportamento entre URLLC, eMBB e mMTC quando a política V2 está ativa.

Quanto à taxa de sucesso das submissões, registaram-se **quarenta e oito** amostras válidas em **sessenta** pedidos na campanha V1 (**48/60**) e **sessenta** em **sessenta** na campanha V2 (**60/60**). Em todas as amostras válidas de ambas as campanhas, a decisão devolvida foi `ACCEPT`.

A política V2 introduz maior sensibilidade à pressão de recursos, refletindo um modelo mais conservador na avaliação de viabilidade, sem induzir instabilidade nas decisões observadas nas amostras bem-sucedidas.

## 6.3 Limitações experimentais

Esta secção explicita condições que **delimitam o alcance** da validação; não invalidam o modelo proposto, mas definem o perímetro dentro do qual as conclusões são sustentadas.

Na campanha V1 ocorreram **doze** falhas HTTP em **sessenta** pedidos, correspondendo a respostas de erro do *backend* sem *payload* analisável para métricas de SLA. Estas falhas são interpretadas como variabilidade do *runtime* sob sequência de carga e não como manipulação dos dados. A campanha V2 completou integralmente os sessenta pedidos com sucesso HTTP; para efeitos de comparação estatística, as médias apresentadas utilizam apenas linhas `ok=1`, o que torna as duas políticas comparáveis em termos de métricas, mas com cardinalidades distintas (quarenta e oito versus sessenta observações válidas).

O domínio **Core** continua a depender, no *Prometheus* observado, de agregações de processo (`process_*`) enquanto métricas `container_*` escopadas ao *namespace* do Free5GC não se encontram disponíveis no *scrape* atual; trata-se de uma limitação de **observabilidade de infraestrutura**, já documentada na auditoria correspondente, e não de omissão deliberada no desenho TriSLA.

O domínio **Transporte** permanece alimentado por métricas de *probe* e séries já integradas no coletor; **não** foi integrado, nesta fase, sinal direto do controlador ONOS no cálculo de `resource_pressure`, apesar de o ONOS estar operacional no plano de dados — a integração exigiria camada REST ou *exporter* adicional, fora do âmbito desta coleta.

Por fim, o ensaio decorreu em **ambiente controlado**, sem injeção de tráfego de utilizador massivo nem perturbações prolongadas; conclusões sobre comportamento extremo de escala ou de *chaos* operacional extrapolam o evidenciado e devem ser objeto de trabalho futuro.

## 6.4 Contribuição científica

Este trabalho demonstra, em ambiente operacional real, a viabilidade de uma arquitetura *SLA-aware* baseada na integração de múltiplas fontes de telemetria e decisão inteligente, mantendo estabilidade operacional mesmo com aumento de sensibilidade do modelo quando a política V2 está ativa. A evidência empírica de que a pressão média subjacente e o *feasibility score* se ajustam de forma coerente, sem alterar a decisão de admissão nas observações válidas analisadas, reforça a utilidade de um controlo fino por *flag* sobre a política de agregação, preservando reversibilidade e auditabilidade.

## 6.5 Conclusão do capítulo

Os resultados obtidos evidenciam que a política SLA V2 introduz maior sensibilidade à pressão de recursos, sem comprometer a estabilidade das decisões nas amostras válidas, validando **parcialmente** a hipótese de que a integração de múltiplas métricas melhora a capacidade de decisão em ambientes multi-domínio, **no âmbito** das condições experimentais aqui descritas e sujeitas às limitações da Secção 6.3.

---

*Fonte de dados: `evidencias/PROMPT48/07_dataset_final.csv`, `09_analysis.txt`, `LIMITACOES_E_NOTAS.md`. Gerador de figuras: `evidencias/PROMPT49/generate_figures_ieee_final.py`.*
