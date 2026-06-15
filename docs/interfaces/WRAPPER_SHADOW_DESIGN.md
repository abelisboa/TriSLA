# Desenho de wrappers *shadow* (futuro)

Canonical interface reference: [`docs/modules/interfaces.md`](../modules/interfaces.md).

**Objetivo:** descrever como uma camada **shadow** de wrappers deve funcionar **sem alterar** o caminho de execução atual (mesmos endpoints, mesmos payloads, mesma ordem SEM → Decision → ML no interior do fluxo SEM, depois NASP → BC → SLA-Agent conforme `docs/TRISLA_E2E_FLOW_CANONICAL.md`).

**Restrições (fase documental / shadow):** sem novo gateway obrigatório, sem wrappers executáveis nesta fase de documentação apenas, sem deploy.

## Princípios

1. **Delegação 1:1:** cada wrapper lógico invoca **exatamente** o cliente/URL atual (mesma assinatura efetiva).
2. **Sem bifurcação de produção:** em shadow, o resultado do wrapper **não substitui** a resposta ao cliente; apenas regista evidência (log estruturado, span opcional, métrica `shadow_*`).
3. **Nomenclatura estável:** `RAN-I1`, `TN-I1`, `CN-I1`, `OBS-I1`, `BC-I1` são **rótulos de governança** sobre chamadas existentes.
4. **Flags futuras:** `USE_INTERFACE_*` permanecem desligadas até fase de dual-run aprovada (`docs/INTERFACE_MIGRATION_PLAN.md`).

## Componentes lógicos (não implementados aqui)

| Componente | Função |
|------------|--------|
| **Interface registry** | Mapeia nome lógico → lista de (serviço, método HTTP, path template, owner) |
| **Shadow delegate** | Reexecuta ou espelha a chamada já feita (preferível: interceptação única que chama legado + regista tags) |
| **Equivalence recorder** | Armazena hash/canónico de request/response para comparação futura dual-run |
| **Tagging** | `interface_id`, `migration_phase=shadow`, `trace_id` em logs |

## Comportamento por fase

### Fase shadow (atual alvo documental)

- Apenas **catálogo + matriz + este desenho**; nenhuma mudança de binário obrigatória.
- Opcional futuro: logs adicionais **não bloqueantes** com tag de interface.

### Fase wrapper (FASE 1 do plano de migração)

- Código chama primeiro o **wrapper**; o wrapper chama o **cliente legado**.
- Testes de contrato validam igualdade de saída frente ao baseline.

### Fase dual (FASE 2)

- Legado e wrapper executam em paralelo (ou replay seguro de leitura); comparador de equivalência.
- Rollback = desligar flag e manter apenas legado.

## Anti-padrões

- Introduzir **novo** URL público que substitua `/api/v1/sla/submit` etc.
- Encaminhar tráfego obrigatoriamente por um **gateway** novo nesta fase.
- Alterar ordem **SEM → ML → Decision** no interior do pipeline SEM sem evidência e testes (o fluxo canónico documentado passa pelo SEM).

## Relação com não regressão

- Checklist operacional: `docs/interfaces/NON_REGRESSION_CHECKLIST_V2.md` e `docs/INTERFACE_NON_REGRESSION_CHECKLIST.md`.
