# Tabela C4 × C2 — Latência × Carga (v2)

**Objetivo:** Comparação analítica entre C4.1 (stress moderado) e C2 (carga controlada URLLC) com latências reais medidas

**Contexto:** Esta tabela cruza os resultados do stress test C4.1 (100 SLAs simultâneos) com os resultados do eixo C2 (carga controlada URLLC com 3, 6 e 10 SLAs simultâneos), incluindo latências reais medidas para ambos os eixos.

| Cenário | SLAs Simultâneos | Latência Média (ms) | Tipo de Decisão Predominante | Observação |
|---------|------------------|---------------------|-------------------------------|------------|
| C2.1 | 3 | 357.33 | RENEG | Carga controlada URLLC |
| C2.2 | 6 | 736.67 | RENEG | Carga controlada URLLC |
| C2.3 | 10 | 1228.00 | RENEG | Carga controlada URLLC |
| C4.1 | 100 | 4648.39 | RENEG | Stress moderado eMBB |
