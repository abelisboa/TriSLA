# Fase C — Menu 2 (Criar SLA PNL) — Build, digest e validação

**Data:** 2025-03-16  
**Escopo:** Somente frontend — Menu 2 Criar SLA PNL. Sem alteração de backend, endpoints, Helm estrutural ou outros menus.

---

## 1. Alterações realizadas

### api.ts
- Adicionada função `postJson(path, payload)` para POST com JSON.
- Adicionado `portalApi.slaInterpret(body)` → `POST /api/v1/sla/interpret` com `{ intent_text, tenant_id }`.

### PnlSlaSection.tsx
- Chamada real a `portalApi.slaInterpret({ intent_text, tenant_id })` (tenant_id fixo `default`).
- Bloco 1 — Entrada: texto natural enviado.
- Bloco 2 — Resultado semântico real: semantic_class, profile_sla, template_id, message, sla_requirements.
- Bloco 3 — Explicação científica: ontology match (se existir), recommended slice (URLLC/eMBB/mMTC em destaque), semantic interpretation.
- Bloco 4 — Estado XAI: confidence e explanation só se vierem na resposta; caso contrário: "Campo ainda não exposto neste endpoint".
- Slice type em destaque (badge URLLC/eMBB/mMTC).
- Detalhes técnicos em bloco colapsável (JSON bruto).
- UI limpa, orientada a evidência, sem cards decorativos.

---

## 2. Build local

```bash
cd /home/porvir5g/gtp5g/trisla/apps/portal-frontend
npm run build
```
**Status:** ✅ Passou.

---

## 3. Imagem e digest

- **Imagem:** `ghcr.io/abelisboa/trisla-portal-frontend:v3.10.16-pnl`
- **Digest (manifest):** `sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835`
- **Imagem digest-only:**  
  `ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835`

Build e push realizados a partir do repositório em `/home/porvir5g/gtp5g/trisla`.

---

## 4. Helm upgrade (digest-only)

O chart `trisla-portal` não está no repositório atual (release `trisla-portal` existe no cluster). Para deploy digest-only, use o repositório/chart onde o trisla-portal estiver definido e atualize o frontend para a imagem por digest.

Exemplo (ajustar path do chart e nome do value conforme seu chart):

```bash
# Exemplo genérico — ajustar conforme values do chart trisla-portal
helm upgrade trisla-portal <path-do-chart-trisla-portal> -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835 \
  --set frontend.image.tag="" \
  --reuse-values
```

Ou, se o chart usar apenas image com digest:

```bash
helm upgrade trisla-portal <path-do-chart> -n trisla \
  --set frontend.image=ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835
```

---

## 5. Validações obrigatórias (após deploy)

```bash
# 5) Imagem do deployment
kubectl -n trisla get deployment trisla-portal-frontend -o jsonpath='{.spec.template.spec.containers[0].image}'

# 6) imageID do pod
kubectl -n trisla get pods -l app=trisla-portal-frontend -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'

# 7) Bundle em runtime (conteúdo do bundle no pod)
POD=$(kubectl -n trisla get pods -l app=trisla-portal-frontend -o jsonpath='{.items[0].metadata.name}')
kubectl -n trisla exec "$POD" -- grep -l "Criar SLA PNL" /usr/share/nginx/html/_next/static/chunks/*.js 2>/dev/null || true
kubectl -n trisla exec "$POD" -- grep -l "slaInterpret" /usr/share/nginx/html/_next/static/chunks/*.js 2>/dev/null || true
```

Não considerar concluído sem: deployment com imagem por digest, imageID do pod conferido e presença do bundle (ex.: "Criar SLA PNL", "slaInterpret") no conteúdo servido pelo pod.

---

## 6. Parada após Menu 2

Não avançar para Menu 3 sem autorização explícita.
