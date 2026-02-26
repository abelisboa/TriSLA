# Análise Comparativa C4.1 × C2 (Latência × Carga)

**Data:** 2025-12-26
**Objetivo:** Cruzamento analítico entre stress test C4.1 e eixo C2 (carga controlada URLLC)

## Contexto do Cruzamento

Esta análise compara os resultados do stress test C4.1 (100 SLAs simultâneos do tipo eMBB) com os resultados do eixo C2 (carga controlada URLLC com 3, 6 e 10 SLAs simultâneos), permitindo análise comparativa de latência e comportamento decisório sob diferentes condições de carga e tipos de slice.

## Justificativa Metodológica

O cruzamento C4.1 × C2 é metodologicamente válido porque:

1. **Mesmo pipeline decisório:** Ambos os cenários exercitam o mesmo pipeline decisório do TriSLA (SEM-CSMF → ML-NSMF → Decision Engine)

2. **Comportamento decisório consistente:** Ambos os cenários apresentaram comportamento decisório idêntico (100% RENEG), permitindo comparação focada em latência e carga

3. **Complementaridade:** C2 representa carga controlada (3-10 SLAs), enquanto C4.1 representa stress moderado (100 SLAs), permitindo análise de escalabilidade

4. **Validade empírica:** Ambos os conjuntos de dados foram coletados em ambiente real (NASP) sem modificações no código produtivo

## Resumo dos Resultados Cruzados

### Eixo C2 (Carga Controlada URLLC)
- **C2.1:** 3 SLAs simultâneos → 100% RENEG
- **C2.2:** 6 SLAs simultâneos → 100% RENEG
- **C2.3:** 10 SLAs simultâneos → 100% RENEG
- **Comportamento:** Estável e consistente, independente da carga (3-10 SLAs)

### C4.1 (Stress Moderado eMBB)
- **C4.1:** 100 SLAs simultâneos → 100% RENEG
- **Latência média:** 4648.39 ms
- **Comportamento:** Pipeline decisório funcional sob carga 10x maior que C2.3

## Análise Comparativa

### Comportamento Decisório
Ambos os eixos (C2 e C4.1) apresentaram comportamento decisório idêntico: 100% de renegociação (RENEG), independentemente da carga aplicada. Esta consistência sugere que o comportamento decisório do TriSLA é estável e previsível tanto sob carga controlada (3-10 SLAs) quanto sob stress moderado (100 SLAs).

### Escalabilidade
O cruzamento revela que o sistema mantém funcionalidade decisória mesmo quando a carga é aumentada significativamente:
- **C2.3:** 10 SLAs → Pipeline funcional
- **C4.1:** 100 SLAs → Pipeline funcional (10x a carga de C2.3)

Esta observação sugere que o pipeline decisório possui capacidade de processamento além do intervalo testado no eixo C2, pelo menos até 100 SLAs simultâneos.

### Limites Operacionais
O cruzamento C4.1 × C2 estabelece limites operacionais claros:
- **Limite inferior confirmado:** 3 SLAs (C2.1 processado com sucesso)
- **Limite superior confirmado:** 100 SLAs (C4.1 processado com sucesso)
- **Limite de taxa identificado:** Entre 100 e 200 SLAs (C4.2 atingiu rate limit)

## Implicações

O cruzamento analítico C4.1 × C2 demonstra que:
1. O comportamento decisório é consistente independentemente da carga (3-100 SLAs)
2. O pipeline decisório mantém funcionalidade sob stress moderado (100 SLAs)
3. O limite operacional funcional está além de 100 SLAs simultâneos
4. O limite de taxa (rate limit) está localizado entre 100 e 200 SLAs simultâneos

## Referências

- Tabela comparativa: 
- Gráfico comparativo: 
- Resultados C2: 
- Resultados C4.1: 
