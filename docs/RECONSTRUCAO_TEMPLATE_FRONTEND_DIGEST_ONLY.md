# RECONSTRUÇÃO CONTROLADA DO TEMPLATE DO FRONTEND (DIGEST-ONLY)

**Data:** 2026-03-16  
**Escopo:** Corrigir apenas o template do frontend no chart local `helm/trisla-portal` para voltar a suportar digest-only, usando o helper já existente em `_helpers.tpl`. Sem deploy, sem helm upgrade, sem alteração de backend ou outros módulos.

---

## A. Diff exato aplicado

**Arquivo:** `helm/trisla-portal/templates/frontend-deployment.yaml`

**Alteração:** Apenas a linha da imagem do container frontend (linha 22).

```diff
       containers:
       - name: frontend
-        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
+        image: {{ include "trisla-portal.image" (dict "repository" .Values.frontend.image.repository "tag" .Values.frontend.image.tag "digest" .Values.frontend.image.digest) }}
         imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
```

Nenhuma outra linha foi alterada (replicas, selectors, env, service, labels, annotations, strategy permanecem iguais).

---

## B. Linha image renderizada

**Comando de validação executado:**
```bash
helm template trisla-portal helm/trisla-portal -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835 \
  --set frontend.image.tag="" \
  | grep "image:"
```

**Saída (linha do frontend):**
```
        image: ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835
```

Resultado aceito: formato **repo@digest** com o digest informado. A primeira linha (`image: "ghcr.io/abelisboa/trisla-portal-backend:latest"`) é do backend, inalterado.

---

## C. Se agora iguala manifest canônico

**Sim.** O manifest canônico (armazenado pelo Helm na rev 55) tinha o frontend em formato `image: "ghcr.io/abelisboa/trisla-portal-frontend@sha256:...". O chart local, após a correção, passa a renderizar o frontend no **mesmo formato** (repo@digest). O comportamento do template volta a ser equivalente ao que gerou o manifest da revisão 55 (uso do helper para digest quando presente).

---

## D. Se chart local voltou a suportar digest-only

**Sim.** O chart local `helm/trisla-portal` voltou a suportar digest-only para o frontend:

- Com `frontend.image.digest` definido e `frontend.image.tag` vazio, o template renderiza **repo@sha256:...**.
- O helper `trisla-portal.image` em `_helpers.tpl` já existia; apenas o `frontend-deployment.yaml` foi ajustado para usá-lo na linha da imagem do frontend.

Nenhum deploy foi executado. Parar após validação local.
