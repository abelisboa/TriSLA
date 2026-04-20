# Regra absoluta permanente — SSOT + Árvore única + Backend first

**Válida para todas as execuções e fases do Portal TriSLA.**

---

## Consulta obrigatória antes de qualquer alteração

1. **PROMPT MESTRE CURSOR — TRI SLA FRONTEND SCIENTIFIC REBUILD (SSOT OFICIAL)** — `PROMPTS/`
2. **MATRIZ TÉCNICA OFICIAL — Portal TriSLA Científico SLA-Centric** — `PROMPTS/`
3. **Evolução do Portal TriSLA para Portal Científico SLA-Centric** — `PROMPTS/`

---

## Regras obrigatórias

| Regra | Descrição |
|-------|-----------|
| Path | Usar somente `/home/porvir5g/gtp5g/trisla` |
| Remoto | Entrar sempre por **ssh node006** para build, deploy e validação |
| Árvore única | Frontend oficial **somente** em `apps/portal-frontend/src/app` |
| app/ | **Nunca** reativar `app/` |
| Backend | **Nunca** alterar backend sem auditoria prévia |
| Campos | **Nunca** inventar campo |
| XAI | **Nunca** inventar XAI |
| Lifecycle | **Nunca** inventar lifecycle agregado |
| Build | Build **só vale** com `rm -rf .next && npm run build` |
| Deploy | Deploy **só vale** com digest remoto = deployment image = pod imageID |
| Fase | Fase **só conclui** com evidência visual final (screenshot ou confirmação explícita) |

---

## Escopo permitido

- **Alterações permitidas:** `apps/portal-frontend/**`

## Escopo proibido

- `apps/portal-backend/**`
- `apps/sem-csmf/**`, `apps/ml-nsmf/**`, `apps/decision-engine/**`, `apps/bc-nssmf/**`
- `apps/nasp-adapter/**`, `apps/sla-agent-layer/**`, `apps/ui-dashboard/**`
- Charts Helm, deployment backend, service backend

(Backend e outros módulos só após auditoria prévia documentada.)

---

## Referência de auditorias

- `docs/AUDITORIA_SSOT_MODULOS_XAI_PIPELINES.md` — módulos, XAI, decision, blockchain, lifecycle, gaps
- `docs/AUDITORIA_ONTOLOGIA_PNL_TEMPLATE.md` — origem dos campos PNL, ontologia, SEM, template

---

## Evidência visual final

Cada fase deve ser considerada concluída apenas quando houver:

- Screenshot das páginas afetadas (PNL, Template, Lifecycle, etc.), ou
- Confirmação explícita de que o digest do pod coincide com o digest da imagem deployada (REMOTE_DIGEST = pod imageID).
