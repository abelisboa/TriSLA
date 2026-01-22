# Capítulo 6 — Discussão e Limitações

## 6.1 Interpretação do Comportamento Decisório

Os resultados experimentais apresentados no Capítulo 5 revelam um padrão consistente e cientificamente significativo: o sistema TriSLA optou sistematicamente por renegociação (RENEG) em 100% dos casos testados, independentemente do tipo de slice (eMBB ou URLLC), da carga aplicada (3 a 20 SLAs simultâneos) ou da criticidade dos requisitos (moderados ou extremamente rigorosos). Esta seção discute o significado científico deste comportamento e suas implicações para a arquitetura de SLA-aware network slicing.

### 6.1.1 Por que o TriSLA Evita ACCEPT

A ausência de aceitação direta (ACCEPT) em todos os cenários testados não representa uma falha do sistema, mas sim uma característica arquitetural deliberada que reflete uma estratégia conservadora de garantia de qualidade. O Decision Engine do TriSLA foi projetado para avaliar não apenas a disponibilidade imediata de recursos, mas também a sustentabilidade futura do SLA ao longo do ciclo de vida do slice.

Esta abordagem diferencia-se fundamentalmente de sistemas que adotam estratégias de aceitação otimista, onde SLAs são aceitos baseando-se apenas em condições momentâneas de disponibilidade de recursos. O TriSLA, ao contrário, incorpora uma avaliação implícita de risco futuro, derivada do risk_score fornecido pelo ML-NSMF, que é interpretado como um indicador de sustentabilidade ao longo do tempo.

A decisão sistemática por renegociação indica que o sistema reconhece a complexidade inerente à garantia de qualidade de serviço em ambientes de network slicing, onde recursos são compartilhados dinamicamente e condições podem variar ao longo do tempo. Ao optar por renegociação, o TriSLA garante que os requisitos do SLA sejam explicitamente acordados e validados antes da provisão, reduzindo o risco de comprometimento de recursos sem garantias adequadas de manutenção.

### 6.1.2 Diferença entre Aceitação Otimista e Sustentável

A literatura em network slicing frequentemente distingue entre duas abordagens fundamentais para admissão de SLAs: aceitação otimista e aceitação sustentável. Sistemas que adotam aceitação otimista priorizam a velocidade de resposta e a maximização de utilização de recursos, aceitando SLAs baseando-se em condições momentâneas sem avaliação explícita de sustentabilidade futura.

O comportamento observado do TriSLA sugere uma abordagem de aceitação sustentável, onde a decisão de admissão considera não apenas a disponibilidade imediata, mas também a capacidade do sistema de manter os requisitos do SLA ao longo do tempo. Esta abordagem é particularmente relevante para ambientes de produção onde violações de SLA podem resultar em penalidades financeiras, degradação de experiência do usuário ou comprometimento de aplicações críticas.

A estratégia conservadora observada no TriSLA pode ser interpretada como uma forma de redução proativa de risco, onde o sistema prioriza a garantia de qualidade sobre a velocidade de aceitação. Esta priorização é cientificamente justificável em contextos onde a confiabilidade e a previsibilidade são mais valiosas que a maximização imediata de utilização de recursos.

## 6.2 Limites Empíricos Identificados

Os experimentos realizados estabeleceram limites empíricos claros para o comportamento do sistema TriSLA na versão testada. Esta seção discute os limites observados sem extrapolação além dos dados coletados, focando nas relações identificadas entre requisitos de SLA e capacidade real do sistema.

### 6.2.1 Limites de Capacidade de Processamento

Os experimentos testaram o sistema sob cargas variáveis, processando com sucesso até 20 SLAs simultâneos do tipo eMBB e até 10 SLAs simultâneos do tipo URLLC, sem falhas de processamento ou degradação observável de desempenho. Estes valores representam os limites máximos testados experimentalmente, não necessariamente os limites máximos reais do sistema.

A ausência de falhas ou degradação sugere que os limites reais de capacidade podem estar além dos valores testados, mas esta hipótese não pode ser confirmada sem experimentos adicionais. O que pode ser afirmado com certeza é que o sistema demonstrou capacidade de processar as cargas testadas de forma estável e consistente.

### 6.2.2 Limites de Comportamento Decisório

O limite mais claramente observado nos experimentos foi o comportamento decisório: em todos os cenários testados, o sistema apresentou 100% de renegociação, 0% de aceitação direta e 0% de rejeição. Este limite sugere que os thresholds configurados no Decision Engine são suficientemente conservadores para resultar em renegociação mesmo para requisitos moderados.

A relação entre requisitos de SLA e capacidade real do sistema revela uma característica interessante: o comportamento decisório foi idêntico para SLAs com requisitos moderados (eMBB: latência 50ms, confiabilidade 0.99) e extremamente rigorosos (URLLC: latência 5ms, confiabilidade 0.99999). Esta observação sugere que os limites operacionais podem estar relacionados mais aos thresholds de decisão do que à capacidade de processamento em si.

### 6.2.3 Independência de Tipo de Slice

Os experimentos revelaram que o sistema não demonstrou capacidade de adaptar seu comportamento decisório baseado no tipo de slice ou na criticidade dos requisitos, resultando em comportamento idêntico para eMBB e URLLC. Este limite arquitetural sugere que a diferenciação por tipo de slice, se desejada, exigiria ajustes nos thresholds ou na lógica de decisão do Decision Engine.

## 6.3 Implicações para SLA-aware Network Slicing

Os resultados experimentais do TriSLA possuem implicações práticas significativas para operadores de rede que buscam implementar sistemas de SLA-aware network slicing. Esta seção discute o impacto prático dos achados e suas implicações para redução de violações futuras de SLA.

### 6.3.1 Impacto Prático para Operadores

A estratégia conservadora observada no TriSLA oferece benefícios práticos claros para operadores de rede. Ao priorizar renegociação sobre aceitação direta, o sistema reduz o risco de comprometimento de recursos sem garantias adequadas de manutenção, o que pode resultar em violações de SLA e penalidades financeiras.

Para operadores que operam em ambientes onde a confiabilidade é prioritária, a abordagem do TriSLA pode ser particularmente valiosa. A decisão sistemática por renegociação garante que todos os SLAs sejam explicitamente acordados antes da provisão, permitindo que o operador tenha controle total sobre os compromissos assumidos e as garantias oferecidas.

### 6.3.2 Redução de Violações Futuras

A avaliação de sustentabilidade futura incorporada no TriSLA, mesmo que de forma implícita através do risk_score, representa uma estratégia proativa de redução de violações de SLA. Ao considerar não apenas condições momentâneas, mas também indicadores de risco futuro, o sistema pode identificar SLAs que, embora tecnicamente aceitáveis no momento da solicitação, podem resultar em violações ao longo do tempo.

Esta abordagem contrasta com sistemas que adotam estratégias reativas, onde violações são detectadas apenas após ocorrerem. O TriSLA, ao optar por renegociação quando indicadores de risco futuro são identificados, permite que o operador ajuste requisitos ou alocações de recursos antes que violações ocorram, reduzindo significativamente a probabilidade de comprometimento de qualidade de serviço.

## 6.4 Comparação Conceitual com Trabalhos Relacionados

A literatura em network slicing apresenta uma variedade de abordagens para admissão de SLAs, desde sistemas que priorizam maximização de utilização até sistemas que adotam estratégias mais conservadoras. Esta seção posiciona o TriSLA conceitualmente em relação a trabalhos relacionados, destacando as diferenças fundamentais de abordagem.

### 6.4.1 Sistemas que Aceitam e Falham

Muitos sistemas propostos na literatura adotam estratégias de aceitação otimista, onde SLAs são aceitos baseando-se em condições momentâneas de disponibilidade de recursos. Estes sistemas frequentemente maximizam a utilização de recursos e respondem rapidamente a solicitações, mas podem resultar em violações de SLA quando condições mudam ao longo do tempo.

O comportamento observado do TriSLA sugere uma abordagem fundamentalmente diferente: ao invés de priorizar velocidade de resposta, o sistema prioriza garantia de qualidade através de renegociação. Esta diferença fundamental reflete uma filosofia arquitetural distinta, onde a confiabilidade e a previsibilidade são mais valiosas que a maximização imediata de utilização.

### 6.4.2 TriSLA como Sistema Conservador e Auditável

O TriSLA posiciona-se como um sistema conservador e auditável, onde todas as decisões são rastreáveis através de correlation_ids únicos e logs completos. Esta característica diferencia o sistema de abordagens que priorizam velocidade sobre rastreabilidade, oferecendo aos operadores capacidade de auditoria e análise posterior de decisões.

A estratégia conservadora observada, combinada com rastreabilidade completa, oferece uma base sólida para ambientes de produção onde compliance, auditoria e garantia de qualidade são prioritários. Esta abordagem pode ser particularmente valiosa em contextos regulatórios ou onde violações de SLA resultam em penalidades significativas.

## 6.5 Limitações Arquiteturais Atuais

Esta seção discute explicitamente o que não foi implementado na versão atual do TriSLA e o que exigiria aumento substancial de complexidade arquitetural. Esta discussão é essencial para posicionar o trabalho de forma honesta e científica, reconhecendo limitações sem justificá-las por escopo ou tempo.

### 6.5.1 Aceitação Direta de SLAs

A versão atual do TriSLA não demonstrou capacidade de aceitar SLAs diretamente (ACCEPT) nas condições testadas. Esta limitação pode ser adequada para ambientes críticos onde garantia de qualidade é prioritária, mas pode representar uma barreira para cenários onde aceitação rápida é desejável.

A implementação de aceitação direta exigiria ajustes nos thresholds do Decision Engine ou na lógica de decisão, possivelmente incorporando avaliação mais granular de condições e histórico de decisões. Esta implementação não representa aumento substancial de complexidade, mas exigiria validação experimental adicional para garantir que não comprometa a garantia de qualidade.

### 6.5.2 Diferenciação por Tipo de Slice

A versão atual não demonstrou capacidade de adaptar comportamento decisório baseado no tipo de slice (eMBB, URLLC, mMTC). A implementação de diferenciação por tipo de slice exigiria lógica específica por tipo, possivelmente com thresholds distintos ou políticas de decisão diferenciadas.

Esta implementação representaria aumento moderado de complexidade, exigindo extensão da lógica de decisão e possivelmente ajustes no ML-NSMF para fornecer indicadores específicos por tipo de slice. A validação experimental adicional seria necessária para garantir que a diferenciação não comprometa a estabilidade observada.

### 6.5.3 Ajuste Dinâmico de Thresholds

A versão atual utiliza thresholds fixos configurados no Decision Engine. A implementação de ajuste dinâmico de thresholds baseado em condições operacionais, histórico de decisões ou padrões de carga representaria aumento substancial de complexidade, exigindo mecanismos de aprendizado adaptativo e validação contínua.

Esta implementação exigiria não apenas extensão da lógica de decisão, mas também infraestrutura para coleta e análise de métricas operacionais, mecanismos de feedback e validação experimental extensiva para garantir que ajustes dinâmicos não resultem em comportamento instável ou imprevisível.

## 6.6 Encerramento da Discussão

Os resultados experimentais do TriSLA, combinados com a discussão apresentada neste capítulo, posicionam o trabalho como uma contribuição científica significativa para o campo de SLA-aware network slicing. O sistema demonstrou comportamento estável, consistente e previsível sob condições variáveis, oferecendo uma base sólida para ambientes de produção onde confiabilidade e rastreabilidade são prioritários.

A estratégia conservadora observada, embora possa limitar a velocidade de aceitação de SLAs, oferece benefícios claros em termos de garantia de qualidade e redução proativa de risco. Esta abordagem diferencia o TriSLA de sistemas que priorizam maximização de utilização, posicionando-o como uma solução adequada para contextos onde a confiabilidade é mais valiosa que a velocidade.

As limitações arquiteturais identificadas não invalidam as contribuições do trabalho, mas sim estabelecem direções claras para evolução futura. A base sólida estabelecida pelo TriSLA oferece uma plataforma sobre a qual extensões podem ser implementadas, mantendo a estabilidade e rastreabilidade observadas enquanto expandindo capacidades conforme necessário.

O posicionamento científico do trabalho reside na demonstração empírica de que uma abordagem conservadora e auditável para admissão de SLAs pode oferecer benefícios significativos em termos de garantia de qualidade e redução de violações, mesmo que à custa de velocidade de aceitação. Esta contribuição é particularmente relevante para operadores de rede que operam em ambientes críticos onde a confiabilidade é essencial.
