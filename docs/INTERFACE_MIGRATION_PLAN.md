# Plano de Migração de Interfaces (Zero Regressão)

Objetivo: evoluir para interfaces formais sem downtime, sem quebra de API e sem alterar fluxo operacional atual.

## FASE 0 - Shadow Interfaces (documentação + observação)
- Criar catálogo documental `interface_name -> endpoint atual -> owner -> domínio`.
- Não alterar endpoints existentes.
- Instrumentar rastreabilidade por interface lógica em logs/telemetria (tags).
- Critério de saída: 100% das interfaces críticas mapeadas em catálogo.

## FASE 1 - Wrapper Layer (abstração não intrusiva)
- Introduzir camada wrapper/adapter por serviço para encapsular chamadas atuais.
- Cada wrapper representa uma interface lógica (`RAN-I1`, `TN-I1`, etc.) e delega ao endpoint atual.
- Não alterar payload de API externa já existente.
- Critério de saída: chamadas inter-serviço principais passam pela camada wrapper sem mudança de comportamento.

## FASE 2 - Dual Operation (antigo + formal em paralelo)
- Operar duas visões simultâneas:
  - contrato atual (runtime ativo),
  - contrato formal nomeado (wrapper/interface catalog).
- Habilitar telemetria comparativa de equivalência (old vs wrapper path).
- Critério de saída: equivalência funcional validada para cadeia crítica SEM->ML->Decision->NASP->SLA-Agent->BC.

## FASE 3 - Switch Controlado (feature flags)
- Introduzir flags por interface lógica (ex.: `USE_INTERFACE_RAN_I1=true`).
- Ativar gradualmente por ambiente/campanha.
- Rollback imediato por flag.
- Critério de saída: produção/campanha estável sem erro adicional e sem alteração de outputs críticos.

## FASE 4 - Depreciação gradual
- Publicar janela de depreciação dos caminhos legados internos.
- Manter compatibilidade de endpoints externos públicos.
- Remover somente adaptações internas obsoletas após janela e evidência de estabilidade.
- Critério de saída: catálogo formal é a referência padrão; legados mínimos e documentados.

## Guardrails obrigatórios
- Sem downtime.
- Sem quebra de API externa.
- Sem rename de serviço/endpoint público.
- Sem dependências novas obrigatórias.
- Toda mudança controlada por flag + rollback documentado.
