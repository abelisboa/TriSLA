# Tabela C4 × C2 — Latência × Carga

**Objetivo:** Comparação analítica entre C4.1 (stress moderado) e C2 (carga controlada URLLC)

**Contexto:** Esta tabela cruza os resultados do stress test C4.1 (100 SLAs simultâneos) com os resultados do eixo C2 (carga controlada URLLC com 3, 6 e 10 SLAs simultâneos), permitindo análise comparativa de latência e comportamento decisório sob diferentes condições de carga.

| Cenário | SLAs Simultâneos | Latência Média (ms) | Tipo de Decisão Predominante | Observação |
|---------|------------------|---------------------|-------------------------------|------------|
| C2.1 | 3 | N/A | RENEG | Carga controlada URLLC (3 SLAs) |
| C2.2 | 6 | N/A | RENEG | Carga controlada URLLC (6 SLAs) |
| C2.3 | 10 | N/A | RENEG | Carga controlada URLLC (10 SLAs) |
| C4.1 | 100 | 4648.39 | RENEG | Stress moderado, 100 SLAs simultâneos |
