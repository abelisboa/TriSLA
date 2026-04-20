# DEPLOY MENU 2 (FRONTEND) — EXECUTADO

**Data:** 2026-03-16 / 2026-03-17  
**Escopo:** Deploy controlado do Menu 2 (Criar SLA PNL), somente frontend, digest-only. Chart local corrigido; comando oficial executado.

---

## Comando executado

```bash
cd /home/porvir5g/gtp5g/trisla

helm upgrade trisla-portal helm/trisla-portal -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835 \
  --set frontend.image.tag="" \
  --reuse-values
```

**Resultado do Helm:** Release upgraded. REVISION: **56**. STATUS: deployed.

---

## A. Helm revision nova

**56** (anterior: 55).

---

## B. Digest aplicado

O deployment **trisla-portal-frontend** foi atualizado com:

- **Imagem (spec):** `ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835`

Validação 1 (deployment image) **OK** — o spec do deployment contém o digest correto.

---

## C. imageID real do pod

**Não disponível.** O pod do frontend entrou em **ImagePullBackOff**.

- **Motivo (eventos do pod):** `failed to resolve reference "ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835": not found`
- A imagem com esse digest **não foi encontrada** no registry **ghcr.io** (acesso do cluster ao registry retornou "not found").
- **Status do pod:** `0/1 ImagePullBackOff` — rollout **não** concluído.

---

## D. Bundle validado

**Não.** O pod do frontend não está Ready; não foi possível executar no container:

- `kubectl -n trisla exec $POD -- sh -c "grep -R 'slaInterpret' /usr/share/nginx/html || true"`
- `kubectl -n trisla exec $POD -- sh -c "grep -R 'Criar SLA PNL' /usr/share/nginx/html || true"`

Validação de bundle **não realizada** (pod não em execução).

---

## E. Teste funcional

**Não realizado.** O frontend não está disponível (pod em ImagePullBackOff). Não foi possível abrir o portal e validar Menu 2 → Criar SLA PNL (semantic_class, profile_sla, template_id, recommended slice, etc.).

---

## F. Backend intacto

- **Pods portal-backend:** Existe pod em **Running** (`trisla-portal-backend-648d7b8c86-t5xxp`, 2d22h). Outro pod em ImagePullBackOff (`trisla-portal-backend-86dd666bbc-7jmzs`, ~4 min) — possivelmente novo ReplicaSet do mesmo release.
- **Logs do deployment backend (pod em Running):** Serviço respondendo (GET /api/v1/nasp/diagnostics 200, GET /health 200, health checks aos dependentes). Backend operacional no pod antigo.

---

## VALIDAÇÃO FALHOU — PARAR

**Regra:** Se qualquer validação falhar, parar imediatamente e documentar.

**Falha:** A imagem do frontend com digest `sha256:c0fa3cf...` **não existe** (ou não é acessível) no registry **ghcr.io** para o cluster. Resultado:

1. Rollout do deployment **trisla-portal-frontend** não concluído (timeout).
2. imageID do pod não obtido (pod não em Running).
3. Bundle e teste funcional não validados.

**Ação:** Parar imediatamente. **Não avançar para Menu 3.**

**Próximos passos recomendados (antes de novo deploy):**

- Confirmar que a imagem `ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835` está publicada e **pública** (ou que o cluster tem permissão de pull no ghcr.io para esse repositório).
- Se a imagem estiver em outro registry ou com tag diferente, ajustar digest/tag no comando e reexecutar o upgrade após validação local com `helm template`.

---

**Deploy executado; validações pós-deploy falharam por indisponibilidade da imagem no registry. Nenhum avanço para Menu 3.**
