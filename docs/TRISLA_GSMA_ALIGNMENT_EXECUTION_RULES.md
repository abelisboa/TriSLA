# TriSLA — GSMA Alignment — Execution Rules (resumo operacional)

**Versão:** 0.1  
**SSOT detalhada:** `docs/TRISLA_GSMA_ALIGNMENT_MASTER_RUNBOOK.md` (v0.2+)  
**Modelo canónico (alvo):** `docs/TRISLA_CANONICAL_SLA_MODEL.md`

Este ficheiro é o **atalho** para operadores e autores: regras rápidas, sequência oficial, checklist e gates. **Não** substitui o runbook mestre; em caso de conflito, prevalece o runbook mestre.

---

## 1. Regras rápidas (não negociáveis)

1. **Ler primeiro** o runbook mestre na secção da fase em curso (§9–§19) e o quadro de estados no topo do runbook.
2. **Não alterar** thresholds, pesos nem fórmulas de scoring do Decision Engine salvo programa de projeto **fora** deste alinhamento GSMA.
3. **Não remover** `template_id`, `form_values`, metadata de orquestração/governação/telemetria exigida pelo baseline.
4. **Não declarar** conformidade GSMA, TMF, NWDAF ou orquestrações **não** presentes no repositório.
5. **Não apagar** pastas `evidencias_*` congeladas; novos runs usam novo sufixo `_<TS>`.
6. **Não avançar** fase N+1 sem **PASS** explícito na fase N no runbook mestre.

---

## 2. Sequência oficial de fases

| Ordem | Fase | Estado (fonte: runbook mestre) |
|-------|------|--------------------------------|
| 0 | Auditoria | PASS (repo) |
| 1 | Modelagem | PASS (doc) |
| 2 | Canonicalization (SEM-CSMF) | PASS (repo) |
| 3 | Backward compatibility / equivalence | **FAIL** (gate GSMA runtime; portal **Running/Ready** pós §12-J; reexecutar `gsma_phase3_runtime_validate.sh` para PASS formal) |
| 4 | Decision Engine alignment (leitura canónica, sem mudar score) | NOT_STARTED (bloqueada) |
| 5 | XAI alignment | NOT_STARTED (bloqueada) |
| 6 | SLA-Agent alignment | NOT_STARTED (bloqueada) |
| 7 | Listings update | NOT_STARTED (bloqueada) |
| 8 | Paper validation | NOT_STARTED (bloqueada) |
| 9 | E2E (node006) | NOT_STARTED (bloqueada) |
| 10 | Scientific freeze | NOT_STARTED (bloqueada) |

> **Nota (2026-05-14):** a FASE 3 permanece **FAIL** no sentido **GSMA** (falta **PASS** do script `docs/scripts/gsma_phase3_runtime_validate.sh`). **Infra:** portal voltou a **Running/Ready** após recuperação do plano de controlo / kubelet em `node1` (runbook §12-J; `evidencias_control_plane_portal_restore_20260514T143349Z/`). Fases 4–10 **bloqueadas** até PASS formal da FASE 3.

> **Nota:** A coluna «Estado» aqui é informativa; a **única** fonte autoritativa é o quadro no `TRISLA_GSMA_ALIGNMENT_MASTER_RUNBOOK.md`. Se divergir, actualizar este ficheiro ou o runbook para realinhar.

---

## 3. Gates obrigatórios (checklist mínimo)

Antes de declarar PASS a uma fase com código:

- [ ] `python3 -m py_compile` nos ficheiros Python alterados (quando aplicável).
- [ ] Testes automáticos exigidos pela fase (ex.: FASE 2 — unittest SEM-CSMF).
- [ ] E2E em `node006` com digest GHCR — quando a fase ou release o exigir (FASE 9+).
- [ ] `decision` / BC / SLA-Agent / telemetria — quando o cenário incluir esses passos (ver runbook §20).
- [ ] Verificação explícita: **sem** mudança de thresholds, **sem** mudança de pesos, **sem** score drift não explicado.

---

## 4. Checklist antes de merge / deploy científico

- [ ] Runbook mestre actualizado (ficheiros tocados, evidência, PASS/FAIL, data).
- [ ] Histórico §28 do runbook com entrada nova.
- [ ] Evidência em `evidencias_gsma_alignment_*` ou pasta acordada para a fase.
- [ ] Rollback documentado (digest anterior, commits a reverter).

---

## 5. Deploy (laboratório)

1. Resolver imagem com **`skopeo inspect`** (digest), não confiar em `:latest` como prova.
2. `kubectl set image …@sha256:…`
3. Registar digest no pacote de evidência e no runbook quando a fase o exigir.

---

## 6. Onde está o detalhe

| Tema | Secção do runbook mestre |
|------|---------------------------|
| Invariantes arquitecturais | §2 |
| Mapa de dependências | §4 |
| Garantias retroactivas | §6 |
| Gates completos | §20 |
| Regras de validação científica | §21 |
| Modelo de evidência runtime | §22 |
| Regras de deploy (laboratório) | §23 |
| Proibições absolutas | §24 |
| Alinhamento paper / dissertação | §25 |
| Contrato de execução futura | §27 |

---

## 7. Coerência e anti-invenção

- Qualquer afirmação em paper ou defesa deve ser **rastreável** a: runbook, commit, ou ficheiro de evidência.
- **GSMA-aligned** (vocabuário e partição de dados) **≠** certificação GSMA; não misturar no texto científico.

---

**Fim do documento de regras de execução (resumo).**
