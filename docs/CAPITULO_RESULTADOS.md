# Capítulo 5 — Resultados Experimentais

## 5.1 Introdução aos Resultados

Este capítulo apresenta os resultados experimentais obtidos através da execução controlada de validações do sistema TriSLA em ambiente real (NASP). Os experimentos foram concebidos para avaliar o comportamento do sistema sob diferentes condições de carga e requisitos de qualidade de serviço, cobrindo dois eixos principais: Enhanced Mobile Broadband (eMBB) e Ultra-Reliable Low-Latency Communications (URLLC).

Todos os resultados apresentados são empíricos e foram coletados através de execuções controladas, sem modificações no código produtivo ou nas regras de decisão do sistema. A metodologia experimental garantiu isolamento total dos experimentos, preservação completa de evidências e rastreabilidade integral através de correlation_ids únicos para cada SLA processado.

Os dados experimentais foram consolidados e estão disponíveis em formato estruturado, incluindo tabelas consolidadas, visualizações gráficas e análises interpretativas detalhadas. Esta seção apresenta uma síntese dos resultados observados, com referência explícita aos artefatos de dados que sustentam as conclusões apresentadas.

## 5.2 Resultados do Eixo C1 — Enhanced Mobile Broadband (eMBB)

O eixo C1 foi concebido para avaliar o comportamento do sistema TriSLA sob carga incremental de SLAs do tipo eMBB, caracterizados por requisitos moderados de latência (50ms), throughput (100Mbps) e confiabilidade (0.99). Três cenários experimentais foram executados, variando o número de SLAs simultâneos de 5 (C1.1_R1) para 10 (C1.2_R1) e finalmente 20 (C1.3_R1).

### 5.2.1 Cenário C1.1_R1 — Carga Baixa (5 SLAs)

O primeiro cenário do eixo C1 submeteu 5 SLAs simultâneos do tipo eMBB ao sistema TriSLA. Todos os 5 SLAs foram processados com sucesso pelo pipeline end-to-end, resultando em 100% de decisões de renegociação (RENEG). Nenhum SLA foi aceito diretamente (ACCEPT) ou rejeitado (REJECT) neste cenário.

A ausência de falhas de processamento e a consistência do comportamento decisório indicam que o sistema está funcionalmente estável mesmo sob condições de carga inicial. Os resultados detalhados estão consolidados na Tabela 5.1 (referência: table_C1_eMBB_results.md).

### 5.2.2 Cenário C1.2_R1 — Carga Moderada (10 SLAs)

O segundo cenário dobrou a carga em relação ao primeiro, submetendo 10 SLAs simultâneos. O comportamento observado foi idêntico ao cenário anterior: todos os 10 SLAs foram processados com sucesso, resultando em 100% de renegociação. Esta observação é cientificamente relevante, pois demonstra que o comportamento decisório do sistema não foi impactado pela duplicação da carga.

A estabilidade do comportamento decisório sob carga dobrada sugere que a arquitetura do TriSLA possui mecanismos robustos de processamento que não são significativamente impactados por variações na carga de trabalho, pelo menos dentro do intervalo testado.

### 5.2.3 Cenário C1.3_R1 — Carga Elevada (20 SLAs)

O terceiro cenário quadruplicou a carga inicial, submetendo 20 SLAs simultâneos ao sistema. Novamente, o comportamento decisório manteve-se completamente consistente: todos os 20 SLAs foram processados com sucesso, resultando em 100% de renegociação.

A consistência do comportamento decisório mesmo quando a carga é quadruplicada (5 → 20 SLAs) demonstra que o sistema mantém estabilidade funcional e previsibilidade comportamental sob condições de carga variável. Esta observação é particularmente relevante para ambientes de produção onde a carga de trabalho pode variar significativamente.

### 5.2.4 Análise de Escalabilidade do Eixo C1

A análise consolidada dos três cenários do eixo C1 revela um padrão consistente de comportamento decisório independente da carga. A Figura 5.1 (referência: fig_scalability_C1.png) visualiza a taxa de renegociação mantendo-se constante em 100% para todos os níveis de carga testados (5, 10 e 20 SLAs simultâneos).

Esta independência de carga sugere que os limites operacionais do sistema TriSLA para SLAs do tipo eMBB estão além do intervalo testado, pelo menos em termos de capacidade de processamento. A ausência de degradação de desempenho ou mudança no comportamento decisório indica que a arquitetura possui mecanismos robustos de processamento sequencial que não são significativamente impactados por variações na carga de trabalho.

A distribuição de decisões para o eixo C1 está visualizada na Figura 5.2 (referência: fig_decision_distribution_C1.png), demonstrando visualmente a consistência do comportamento observado em todos os cenários.

## 5.3 Resultados do Eixo C2 — Ultra-Reliable Low-Latency Communications (URLLC)

O eixo C2 foi concebido para avaliar o comportamento do sistema TriSLA sob SLAs com requisitos extremamente rigorosos de latência e confiabilidade, característicos de aplicações URLLC. Os SLAs testados apresentavam latência de 5ms (10x mais rigoroso que eMBB), confiabilidade de 0.99999 (100x mais rigoroso que eMBB) e jitter de 1ms. Três cenários experimentais foram executados, variando o número de SLAs simultâneos de 3 (C2.1_R1) para 6 (C2.2_R1) e finalmente 10 (C2.3_R1).

### 5.3.1 Cenário C2.1_R1 — Carga Inicial (3 SLAs)

O primeiro cenário do eixo C2 submeteu 3 SLAs simultâneos com requisitos URLLC rigorosos ao sistema TriSLA. Todos os 3 SLAs foram processados com sucesso, resultando em 100% de decisões de renegociação (RENEG). A ausência de falhas de processamento mesmo sob requisitos extremamente rigorosos demonstra que o sistema é capaz de processar SLAs URLLC de forma funcionalmente estável.

A decisão sistemática por renegociação mesmo para cargas menores (3 SLAs) sugere que o comportamento decisório do sistema não é primariamente determinado pela carga, mas sim pelos thresholds configurados no Decision Engine. Os resultados detalhados estão consolidados na Tabela 5.2 (referência: table_C2_URLLC_results.md).

### 5.3.2 Cenário C2.2_R1 — Carga Dobrada (6 SLAs)

O segundo cenário dobrou a carga em relação ao primeiro, submetendo 6 SLAs simultâneos com requisitos URLLC. O comportamento observado foi idêntico ao cenário anterior: todos os 6 SLAs foram processados com sucesso, resultando em 100% de renegociação.

A consistência do comportamento decisório mesmo quando a carga é dobrada (3 → 6 SLAs) demonstra que o sistema mantém estabilidade funcional mesmo sob requisitos extremamente rigorosos e carga incremental. Esta observação é particularmente relevante para SLAs URLLC, onde a criticidade dos requisitos torna a estabilidade do sistema ainda mais importante.

### 5.3.3 Cenário C2.3_R1 — Carga Triplicada (10 SLAs)

O terceiro cenário triplicou a carga inicial, submetendo 10 SLAs simultâneos com requisitos URLLC ao sistema. Novamente, o comportamento decisório manteve-se completamente consistente: todos os 10 SLAs foram processados com sucesso, resultando em 100% de renegociação.

A estabilidade do comportamento decisório mesmo quando a carga é triplicada (3 → 10 SLAs) sob requisitos extremamente rigorosos demonstra que a arquitetura do TriSLA possui mecanismos robustos de processamento que não são significativamente impactados por variações na carga de trabalho, mesmo para SLAs com requisitos críticos.

### 5.3.4 Análise de Escalabilidade do Eixo C2

A análise consolidada dos três cenários do eixo C2 revela o mesmo padrão consistente observado no eixo C1: comportamento decisório independente da carga. A Figura 5.3 (referência: fig_scalability_C2.png) visualiza a taxa de renegociação mantendo-se constante em 100% para todos os níveis de carga testados (3, 6 e 10 SLAs simultâneos).

Esta independência de carga sob requisitos extremamente rigorosos sugere que os limites operacionais do sistema TriSLA para SLAs do tipo URLLC estão além do intervalo testado, pelo menos em termos de capacidade de processamento. A ausência de degradação de desempenho ou mudança no comportamento decisório indica que a arquitetura possui mecanismos robustos capazes de processar SLAs com requisitos críticos de forma estável e consistente.

A distribuição de decisões para o eixo C2 está visualizada na Figura 5.4 (referência: fig_decision_distribution_C2.png), demonstrando visualmente a consistência do comportamento observado em todos os cenários URLLC.

## 5.4 Comparação Consolidada C1 × C2

A comparação formal entre os eixos C1 (eMBB) e C2 (URLLC) revela observações científicas significativas sobre o comportamento do sistema TriSLA sob diferentes tipos de slice e requisitos de qualidade de serviço. A Tabela 5.3 (referência: table_C1_vs_C2_comparison.md) consolida esta comparação de forma estruturada.

### 5.4.1 Comportamento Decisório Idêntico

A observação mais significativa da comparação entre os eixos é que o comportamento decisório foi completamente idêntico para SLAs eMBB (requisitos moderados) e URLLC (requisitos extremamente rigorosos). Em todos os seis cenários testados (três por eixo), o sistema apresentou 100% de renegociação, 0% de aceitação direta e 0% de rejeição.

Esta observação é cientificamente relevante, pois indica que o Decision Engine do TriSLA não diferencia significativamente entre tipos de slice no processo decisório, ou que os thresholds configurados são suficientemente conservadores para resultar em renegociação mesmo para requisitos moderados, tornando a diferença entre requisitos moderados e rigorosos irrelevante para a decisão final.

### 5.4.2 Diferenças de Exigência e Impacto no Comportamento

Apesar das diferenças substanciais nos requisitos entre eMBB e URLLC (latência 10x mais rigorosa, confiabilidade 100x mais rigorosa para URLLC), o comportamento decisório do sistema manteve-se idêntico. Esta observação sugere que os limites operacionais podem estar relacionados mais aos thresholds de decisão do que à capacidade de processamento em si.

A Figura 5.5 (referência: fig_C1_vs_C2_comparison.png) visualiza a comparação entre os eixos, demonstrando visualmente a similaridade do comportamento decisório independentemente do tipo de slice ou da criticidade dos requisitos.

### 5.4.3 Estabilidade sob Carga Variável

Ambos os eixos demonstraram estabilidade notável sob condições de carga variável. O eixo C1 testou carga até 20 SLAs simultâneos, enquanto o eixo C2 testou carga até 10 SLAs simultâneos. Em ambos os casos, o comportamento decisório manteve-se completamente consistente, independentemente da carga testada.

Esta observação sugere que a arquitetura do TriSLA possui mecanismos robustos de processamento que não são significativamente impactados por variações na carga de trabalho, seja para SLAs com requisitos moderados (eMBB) ou extremamente rigorosos (URLLC).

## 5.5 Síntese dos Resultados

A síntese consolidada dos resultados experimentais dos eixos C1 e C2 revela padrões consistentes e observações científicas significativas sobre o comportamento do sistema TriSLA.

### 5.5.1 Padrões Observados

O padrão mais consistente observado em todos os seis cenários testados foi a decisão sistemática por renegociação (RENEG) em 100% dos casos. Este padrão foi mantido independentemente do tipo de slice (eMBB ou URLLC), da carga testada (3 a 20 SLAs simultâneos) ou da criticidade dos requisitos (moderados ou extremamente rigorosos).

A ausência de aceitação direta (ACCEPT) ou rejeição (REJECT) em todos os cenários testados sugere que o sistema está configurado com thresholds conservadores, priorizando a garantia de qualidade através de ajustes negociados antes da provisão do serviço.

### 5.5.2 Consistência Decisória

A consistência do comportamento decisório observada em todos os cenários testados é cientificamente significativa. O sistema demonstrou comportamento completamente previsível e reproduzível, independentemente das condições experimentais. Esta consistência sugere que o sistema opera de forma determinística dentro dos parâmetros testados, o que é desejável para sistemas críticos onde previsibilidade é essencial.

### 5.5.3 Estabilidade Funcional

Todos os SLAs submetidos em todos os cenários foram processados com sucesso pelo pipeline end-to-end, sem falhas de processamento ou degradação observável de desempenho. Esta estabilidade funcional demonstra que a arquitetura do TriSLA possui mecanismos robustos de processamento capazes de lidar com variações na carga de trabalho e na criticidade dos requisitos.

### 5.5.4 Limites Empíricos Observados

Os experimentos realizados estabeleceram limites empíricos claros para o comportamento decisório do sistema TriSLA na versão testada. O sistema demonstrou capacidade de processar até 20 SLAs simultâneos do tipo eMBB e até 10 SLAs simultâneos do tipo URLLC sem falhas de processamento. No entanto, nenhum SLA foi aceito diretamente nas condições testadas, sugerindo que os limites operacionais podem estar relacionados mais aos thresholds de decisão do que à capacidade de processamento em si.

## 5.6 Encerramento do Capítulo

Este capítulo apresentou os resultados experimentais obtidos através da execução controlada de validações do sistema TriSLA em ambiente real. Os experimentos cobriram dois eixos principais (eMBB e URLLC) e demonstraram que o sistema apresenta comportamento decisório consistente, estável e previsível sob condições de carga variável e requisitos de qualidade de serviço diversos.

Os resultados consolidados fornecem uma base empírica sólida para compreensão do comportamento real do sistema TriSLA e identificação de áreas potenciais de evolução futura. A consistência observada e a estabilidade funcional demonstrada indicam que a arquitetura possui fundamentos sólidos, enquanto a estratégia conservadora de renegociação observada sugere oportunidades de otimização para cenários onde aceitação direta é desejável.

Os dados experimentais completos, incluindo tabelas consolidadas, visualizações gráficas e análises interpretativas detalhadas, estão disponíveis no diretório  para referência e análise adicional.
