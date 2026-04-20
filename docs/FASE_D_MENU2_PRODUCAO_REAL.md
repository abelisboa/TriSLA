# FASE D — PUBLICAÇÃO REAL DO MENU 2 (Criar SLA PNL) COM DIGEST REMOTO CORRETO

**Data:** 2026-03-17  
**Referência:** `@PROMPTS/CURSOR_PROMPT_DEFINITIVO_FRONTEND_TRISLA.md`  
**Escopo:** Publicar a versão do frontend que contém Menu 2 em produção usando digest remoto real. Somente frontend; backend e demais módulos não alterados.

---

## 1. Auditoria pré-build

**Comandos executados:**
```bash
grep -R "slaInterpret" -n apps/portal-frontend/src
grep -R "Criar SLA PNL" -n apps/portal-frontend/src
grep -R "semantic_class" -n apps/portal-frontend/src
```

**Resultados:**

| Item | Localização |
|------|-------------|
| **slaInterpret** | `apps/portal-frontend/src/lib/api.ts` (definição); `apps/portal-frontend/src/sections/PnlSlaSection.tsx` (chamada) |
| **Criar SLA PNL** | `apps/portal-frontend/src/sections/PnlSlaSection.tsx` (título); `apps/portal-frontend/src/components/layout/Sidebar.tsx` (menu) |
| **semantic_class** | `apps/portal-frontend/src/sections/PnlSlaSection.tsx` (tipo e exibição) |

**Respostas:**

- **A. Arquivo final correto do Menu 2:** `apps/portal-frontend/src/sections/PnlSlaSection.tsx` (e suporte em `api.ts`, `Sidebar.tsx`).
- **B. Código local contém versão real:** Sim. Endpoint real `/api/v1/sla/interpret`, chamada `portalApi.slaInterpret`, exibição de semantic_class, profile_sla, template_id, message, sla_requirements, recommended slice, XAI (confidence/explanation ou "Campo ainda não exposto neste endpoint"), JSON expandível.
- **C. Pronto para build:** Sim.

---

## 2. Tag usada

**TS** (timestamp UTC): `20260317T001745Z`

**Imagem:** `ghcr.io/abelisboa/trisla-portal-frontend:20260317T001745Z`

---

## 3. Digest remoto

**Comando:**
```bash
REMOTE_DIGEST=$(skopeo inspect --authfile ~/.config/containers/auth.json \
  docker://ghcr.io/abelisboa/trisla-portal-frontend:20260317T001745Z | jq -r .Digest)
echo "REMOTE_DIGEST=${REMOTE_DIGEST}"
```

**Resultado:**  
`REMOTE_DIGEST=sha256:8d954d6357dd4e297930ccb03c22ed5e9c769bf85f4231db0fe9f8f718832a9e`

Digest obtido **após push**; existe no GHCR e foi usado no helm upgrade.

---

## 4. Helm revision

**Comando:**  
`helm upgrade trisla-portal helm/trisla-portal -n trisla --set frontend.image.repository=... --set frontend.image.digest=${REMOTE_DIGEST} --set frontend.image.tag="" --reuse-values`

**Revisão nova:** **58** (anterior: 57). STATUS: deployed.

---

## 5. Deployment image

```bash
kubectl -n trisla get deployment trisla-portal-frontend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
```

**Resultado:**  
`ghcr.io/abelisboa/trisla-portal-frontend@sha256:8d954d6357dd4e297930ccb03c22ed5e9c769bf85f4231db0fe9f8f718832a9e`

---

## 6. Pod imageID

```bash
kubectl -n trisla get pod -l app=trisla-portal-frontend -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'; echo
```

**Resultado:**  
`ghcr.io/abelisboa/trisla-portal-frontend@sha256:8d954d6357dd4e297930ccb03c22ed5e9c769bf85f4231db0fe9f8f718832a9e`

Deployment e pod alinhados ao digest remoto.

---

## 7. Bundle validado

**Comandos:**
```bash
POD=$(kubectl -n trisla get pod -l app=trisla-portal-frontend -o jsonpath='{.items[0].metadata.name}')
kubectl -n trisla exec $POD -- sh -c "grep -R 'slaInterpret' /usr/share/nginx/html || true"
kubectl -n trisla exec $POD -- sh -c "grep -R 'Criar SLA PNL' /usr/share/nginx/html || true"
```

**Resultado:**

- **slaInterpret:** presente em `/usr/share/nginx/html/_next/static/chunks/app/page-4c0eea5fb5659b8b.js` (API e uso no Menu 2).
- **Criar SLA PNL:** presente no mesmo chunk e em `index.html` (menu lateral).

Bundle do Menu 2 está presente no pod em produção.

---

## 8. Teste funcional

**Passos para validação manual (obrigatória):**

1. Abrir o portal no browser.
2. Clicar em **Menu 2 — Criar SLA PNL**.
3. No campo de frase, digitar: **cirurgia remota**.
4. Clicar em **Interpretar**.
5. Validar se aparecem:
   - **semantic_class**
   - **profile_sla**
   - **template_id**
   - **recommended slice**
   - **sla_requirements**
   - **Semantic interpretation**
   - **JSON técnico expandível** (botão "Expandir detalhes técnicos").

**Status:** Rollout e bundle OK. O teste funcional no browser deve ser executado pelo operador; o endpoint real `/api/v1/sla/interpret` é usado pelo frontend (sem mock).

---

## 9. Conclusão

- **FASE D concluída.** Menu 2 (Criar SLA PNL) foi publicado em produção com **digest remoto** `sha256:8d954d6357dd4e297930ccb03c22ed5e9c769bf85f4231db0fe9f8f718832a9e`.
- Fluxo utilizado: build → push → digest remoto (skopeo) → helm upgrade → validações (rollout, deployment image, pod imageID, bundle).
- Backend e demais módulos não foram alterados.
- **Não avançar para Menu 3** até conclusão do teste funcional manual e aprovação explícita.

---

**Regra final:** Se qualquer validação futura falhar, parar imediatamente. Nenhuma alteração em backend, SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, NASP Adapter ou observabilidade.
