# Mapa de Contribuições Científicas — TriSLA

## 1. Contribuições Arquiteturais

### 1.1 Arquitetura de SLA-aware Network Slicing com Avaliação de Sustentabilidade Futura

O TriSLA introduz uma arquitetura que incorpora avaliação explícita de sustentabilidade futura no processo de admissão de SLAs. Diferentemente de sistemas que avaliam apenas condições momentâneas, o Decision Engine do TriSLA interpreta o risk_score fornecido pelo ML-NSMF como um indicador de sustentabilidade ao longo do ciclo de vida do slice, permitindo decisões baseadas não apenas em disponibilidade imediata, mas também em capacidade de manutenção futura.

**Diferenciação:** Esta abordagem diferencia-se de sistemas que adotam estratégias de aceitação otimista, onde SLAs são aceitos baseando-se apenas em condições momentâneas, resultando em maior risco de violações futuras.

### 1.2 Integração de Machine Learning com Lógica de Decisão Conservadora

A arquitetura integra predições de machine learning (ML-NSMF) com lógica de decisão conservadora (Decision Engine), onde o modelo ML fornece indicadores de risco sem decidir diretamente, e a lógica de decisão interpreta estes indicadores considerando sustentabilidade futura. Esta separação de responsabilidades permite que o sistema mantenha controle explícito sobre decisões críticas enquanto aproveita capacidades preditivas do ML.

**Diferenciação:** Esta abordagem diferencia-se de sistemas onde modelos ML decidem diretamente, oferecendo maior transparência e controle sobre decisões críticas de admissão de SLAs.

### 1.3 Rastreabilidade Completa através de Correlation IDs

A arquitetura garante rastreabilidade completa de cada SLA processado através de correlation_ids únicos, permitindo auditoria e análise posterior de decisões. Esta característica é essencial para ambientes de produção onde compliance e auditoria são prioritários.

**Diferenciação:** Esta abordagem diferencia-se de sistemas que priorizam velocidade sobre rastreabilidade, oferecendo capacidade de auditoria completa sem comprometer funcionalidade.

## 2. Contribuições Metodológicas

### 2.1 Metodologia Experimental Isolada e Reprodutível

O trabalho introduz uma metodologia experimental rigorosa que garante isolamento total dos experimentos do código produtivo, preservação completa de evidências e rastreabilidade integral. Esta metodologia permite validação empírica do sistema sem risco de invalidação de resultados através de modificações acidentais.

**Diferenciação:** Esta abordagem diferencia-se de metodologias experimentais ad-hoc, oferecendo garantias formais de reprodutibilidade e integridade de evidências.

### 2.2 Validação Empírica em Ambiente Real sem Modificações

Os experimentos foram executados em ambiente real (NASP) sem modificações no código produtivo ou nas regras de decisão, demonstrando comportamento real do sistema sob condições operacionais. Esta abordagem diferencia-se de validações em ambientes simulados ou com modificações específicas para demonstração.

**Diferenciação:** Esta abordagem diferencia-se de validações que modificam o sistema para demonstrar resultados desejados, oferecendo evidência empírica genuína do comportamento real.

### 2.3 Consolidação Científica de Resultados Experimentais

O trabalho introduz uma estrutura formal para consolidação científica de resultados experimentais, incluindo tabelas consolidadas, visualizações gráficas e análises interpretativas. Esta estrutura permite reutilização dos dados para análises adicionais e publicação científica.

**Diferenciação:** Esta abordagem diferencia-se de apresentações ad-hoc de resultados, oferecendo estrutura formal e reprodutível para consolidação científica.

## 3. Contribuições Empíricas

### 3.1 Demonstração Empírica de Comportamento Conservador e Previsível

Os experimentos demonstraram empiricamente que o TriSLA apresenta comportamento decisório extremamente conservador e previsível, optando sistematicamente por renegociação (RENEG) em 100% dos casos testados, independentemente do tipo de slice (eMBB ou URLLC), da carga aplicada (3 a 20 SLAs simultâneos) ou da criticidade dos requisitos.

**Diferenciação:** Esta observação empírica diferencia-se de afirmações teóricas ou simulações, oferecendo evidência real de comportamento sob condições operacionais.

### 3.2 Estabelecimento de Limites Empíricos para SLA-aware Network Slicing

Os experimentos estabeleceram limites empíricos claros para o comportamento do sistema, demonstrando capacidade de processar até 20 SLAs simultâneos do tipo eMBB e até 10 SLAs simultâneos do tipo URLLC sem falhas de processamento. Estes limites representam evidência empírica real, não extrapolações teóricas.

**Diferenciação:** Esta contribuição diferencia-se de limites teóricos ou simulados, oferecendo limites observados em ambiente real.

### 3.3 Demonstração de Independência de Carga no Comportamento Decisório

Os experimentos demonstraram empiricamente que o comportamento decisório do TriSLA é independente da carga aplicada, mantendo-se consistente mesmo quando a carga é quadruplicada (5 → 20 SLAs para eMBB) ou triplicada (3 → 10 SLAs para URLLC). Esta observação é cientificamente significativa, pois sugere que os limites operacionais estão relacionados mais aos thresholds de decisão do que à capacidade de processamento.

**Diferenciação:** Esta observação empírica diferencia-se de hipóteses teóricas, oferecendo evidência real de comportamento sob carga variável.

### 3.4 Demonstração de Comportamento Idêntico para Diferentes Tipos de Slice

Os experimentos demonstraram empiricamente que o comportamento decisório do TriSLA é idêntico para SLAs eMBB (requisitos moderados) e URLLC (requisitos extremamente rigorosos), sugerindo que o sistema não diferencia significativamente entre tipos de slice no processo decisório. Esta observação estabelece um limite empírico claro da versão atual do sistema.

**Diferenciação:** Esta observação empírica diferencia-se de afirmações arquiteturais, oferecendo evidência real de comportamento sob diferentes tipos de slice.

## 4. Contribuições para a Comunidade

### 4.1 Contribuições para Pesquisa em Network Slicing

O trabalho contribui para a pesquisa em network slicing através de:

- **Evidência empírica de comportamento conservador:** Demonstração real de que estratégias conservadoras podem oferecer benefícios em termos de garantia de qualidade e redução de violações, mesmo que à custa de velocidade de aceitação.

- **Metodologia experimental reprodutível:** Estrutura formal que pode ser reutilizada por outros pesquisadores para validação empírica de sistemas de network slicing.

- **Limites empíricos estabelecidos:** Valores reais observados que podem servir como referência para comparação com outros sistemas.

### 4.2 Contribuições para Operadores de Rede

O trabalho contribui para operadores de rede através de:

- **Arquitetura auditável:** Sistema que oferece rastreabilidade completa de decisões, essencial para ambientes de produção onde compliance é prioritário.

- **Estratégia de redução proativa de violações:** Abordagem que identifica riscos futuros antes que violações ocorram, permitindo ajustes preventivos.

- **Comportamento previsível:** Sistema que opera de forma determinística e reproduzível, essencial para planejamento e operação.

### 4.3 Contribuições para Sistemas SLA-aware

O trabalho contribui para o campo de sistemas SLA-aware através de:

- **Separação de responsabilidades entre ML e lógica de decisão:** Arquitetura que mantém controle explícito sobre decisões críticas enquanto aproveita capacidades preditivas do ML.

- **Avaliação de sustentabilidade futura:** Incorporação de avaliação de risco futuro no processo de admissão, diferenciando-se de abordagens que avaliam apenas condições momentâneas.

- **Estratégia conservadora validada empiricamente:** Demonstração real de que estratégias conservadoras podem ser adequadas para ambientes críticos onde confiabilidade é prioritária.

## 5. Síntese Final

### Contribuições Principais

1. **Arquitetura de SLA-aware Network Slicing com avaliação de sustentabilidade futura:** Sistema que incorpora avaliação explícita de risco futuro no processo de admissão de SLAs.

2. **Metodologia experimental isolada e reprodutível:** Estrutura formal que garante isolamento, rastreabilidade e preservação de evidências.

3. **Demonstração empírica de comportamento conservador e previsível:** Evidência real de comportamento sob condições operacionais variáveis.

4. **Estabelecimento de limites empíricos:** Valores reais observados para capacidade de processamento e comportamento decisório.

5. **Evidência de independência de carga:** Demonstração empírica de que comportamento decisório não varia com carga aplicada.

6. **Evidência de comportamento idêntico para diferentes tipos de slice:** Observação empírica de que sistema não diferencia significativamente entre tipos de slice.

7. **Arquitetura auditável com rastreabilidade completa:** Sistema que oferece capacidade de auditoria através de correlation_ids únicos.

8. **Estratégia de redução proativa de violações:** Abordagem que identifica riscos futuros antes que violações ocorram.

9. **Separação de responsabilidades entre ML e lógica de decisão:** Arquitetura que mantém controle explícito sobre decisões críticas.

10. **Validação empírica em ambiente real:** Demonstração de comportamento real sem modificações no código produtivo.

### Diferenciação Científica

As contribuições deste trabalho diferenciam-se de trabalhos relacionados através de:

- **Evidência empírica real:** Diferentemente de simulações ou demonstrações com modificações, este trabalho oferece evidência genuína de comportamento em ambiente real.

- **Metodologia rigorosa:** Diferentemente de validações ad-hoc, este trabalho oferece metodologia formal e reprodutível.

- **Foco em sustentabilidade futura:** Diferentemente de sistemas que avaliam apenas condições momentâneas, este trabalho incorpora avaliação de risco futuro.

- **Estratégia conservadora validada:** Diferentemente de sistemas que priorizam velocidade, este trabalho demonstra empiricamente benefícios de estratégias conservadoras.

- **Rastreabilidade completa:** Diferentemente de sistemas que priorizam velocidade sobre auditoria, este trabalho oferece capacidade completa de auditoria.

