# AUDITORIA DE DEPLOY — Menu 2 (Frontend) — Digest-only

**Data:** 2025-03-16  
**Escopo:** Determinar qual release Helm controla o deployment do frontend TriSLA e preparar o comando correto de deploy digest-only. **Sem alteração de código; upgrade não executado.**

---

## Comandos executados e saídas registradas

### helm list -A | grep -E 'trisla|portal'

```
trisla                	trisla          	406     	2026-03-15 16:47:43	deployed	trisla-3.10.0       	3.10.0
trisla-besu           	trisla          	4       	2026-01-31 14:49:09	failed  	trisla-besu-1.0.0   	23.10.1
trisla-portal         	trisla          	55      	2026-03-12 17:27:10	deployed	trisla-portal-1.0.2	1.0.0
(... demais releases em outros namespaces omitidos)
```

### helm get values trisla -n trisla

```
USER-SUPPLIED VALUES:
portalFrontend:
  image:
    digest: sha256:0ded338f755059cf4bd5bb5ed37dedec2df68d27b845630d6a7452279500b205
    repository: ghcr.io/abelisboa/trisla-portal-frontend
```

### helm get values trisla-portal -n trisla

```
USER-SUPPLIED VALUES:
frontend:
  image:
    digest: sha256:7903261048522d920d5e3b0448f8e152dd26955ecaffe88d72146ea19f7d6e02
    repository: ghcr.io/abelisboa/trisla-portal-frontend
    tag: ""
```

### kubectl -n trisla get deployment | grep portal

```
trisla-portal-backend        1/1     1            1           10d
trisla-portal-frontend       1/1     1            1           86d
```

### kubectl -n trisla get deployment trisla-portal-frontend -o yaml | grep image:

```
    image: ghcr.io/abelisboa/trisla-portal-frontend@sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772
```

(Anotações do deployment: `meta.helm.sh/release-name: trisla-portal`, `meta.helm.sh/release-namespace: trisla`.)

### kubectl -n trisla describe deployment trisla-portal-frontend

- **Name:** trisla-portal-frontend  
- **Namespace:** trisla  
- **Labels:** app=trisla-portal-frontend, app.kubernetes.io/managed-by=Helm, component=frontend  
- **Annotations:** meta.helm.sh/release-name: **trisla-portal**, meta.helm.sh/release-namespace: trisla  
- **Image (container frontend):** ghcr.io/abelisboa/trisla-portal-frontend@sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772  
- **Replicas:** 1 desired | 1 updated | 1 total | 1 available  

---

## Respostas com evidência

### A. Qual release Helm controla trisla-portal-frontend?

**trisla-portal.**

Evidência: no deployment `trisla-portal-frontend` consta `meta.helm.sh/release-name: trisla-portal`. O release `trisla` tem user values `portalFrontend.image`, mas o recurso em questão pertence ao release **trisla-portal**.

### B. Qual chart está em uso?

**trisla-portal-1.0.2** (APP VERSION 1.0.0).

Evidência: `helm list -n trisla` e `helm get metadata trisla-portal -n trisla`: CHART trisla-portal, VERSION 1.0.2. Manifesto gerado referencia `trisla-portal/templates/` (frontend-service.yaml, frontend-deployment, etc.).

### C. Qual values key controla portalFrontend.image?

No release que controla o frontend (**trisla-portal**), a key é:

**frontend.image**

(com subkeys: `frontend.image.repository`, `frontend.image.digest`, `frontend.image.tag`.)

Evidência: `helm get values trisla-portal -n trisla` e `helm get values trisla-portal -n trisla -a` (COMPUTED VALUES) mostram `frontend.image.digest`, `frontend.image.repository`, `frontend.image.tag`. O chart usa essa estrutura; não `portalFrontend` (que é do release `trisla`).

### D. Qual digest está rodando hoje?

**sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772**

Evidência:  
- `kubectl -n trisla get deployment trisla-portal-frontend -o yaml` → image com esse digest.  
- `kubectl -n trisla get pods -l app=trisla-portal-frontend -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'` → mesmo digest.

### E. Release correto: trisla ou trisla-portal?

**trisla-portal.**

O deployment `trisla-portal-frontend` é gerenciado pelo release **trisla-portal** (annotations no deployment). O release **trisla** não é o dono desse deployment; seus values `portalFrontend` são de outro uso (ex.: chart trisla que pode referenciar portal em outro contexto).

---

## Divergência entre deployment, pod e Helm values

| Origem              | Digest / imagem |
|---------------------|------------------|
| Deployment (spec)   | sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772 |
| Pod (imageID)       | sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772 |
| trisla-portal values (user) | sha256:7903261048522d920d5e3b0448f8e152dd26955ecaffe88d72146ea19f7d6e02 |
| trisla-portal values (computed) | sha256:79032610... (igual ao user) |

**Conclusão:** Deployment e pod estão alinhados (mesmo digest 2fcb07a6...). Os **values** do release trisla-portal (user e computed) indicam digest **79032610...**, diferente do que está rodando (2fcb07a6...). Ou seja, em algum momento o deployment foi atualizado (ex.: upgrade com outro digest ou alteração manual) e o valor gravado nos values do release ficou desatualizado. Para deploy digest-only do Menu 2, usar o release **trisla-portal** e setar o novo digest explicitamente.

---

## Imagem nova já publicada (Menu 2)

```
ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835
```

---

## Release e chart corretos

- **Release:** trisla-portal  
- **Namespace:** trisla  
- **Chart:** trisla-portal (versão 1.0.2 instalada). O chart **está** no repositório atual no path validado abaixo.

---

## AUDITORIA FINAL DO CHART REAL (executada)

### Comandos de auditoria executados

- **pwd:** `/home/porvir5g/gtp5g/trisla`
- **find ... grep portal:** diretórios encontrados incluem `helm/trisla-portal`, `trisla-portal/helm/trisla-portal`, `trisla-portal/infra/helm/trisla-portal`, entre outros.
- **find Chart.yaml:** múltiplos `Chart.yaml` com nome trisla-portal; o chart **canônico** do repo (raiz do trisla) está em **`helm/trisla-portal`**.
- **grep "name: trisla-portal":** presente em `helm/trisla-portal/Chart.yaml` (name: trisla-portal, version: 1.0.2).
- **grep "frontend.image":** usado em `helm/trisla-portal/templates/frontend-deployment.yaml` e em `helm/trisla-portal/values.yaml` (repository, tag, digest).
- **helm get manifest trisla-portal -n trisla:** manifest referencia `# Source: trisla-portal/templates/...` (backend-service, frontend-service, backend-deployment, frontend-deployment). Imagem do frontend no cluster: `ghcr.io/abelisboa/trisla-portal-frontend@sha256:7903261048522d920d5e3b0448f8e152dd26955ecaffe88d72146ea19f7d6e02` (formato repo@digest).

### Respostas da auditoria

| Pergunta | Resposta |
|----------|----------|
| **A. Onde está o chart real usado pelo release trisla-portal?** | No repositório atual: diretório **`helm/trisla-portal`** (Chart name: trisla-portal, version: 1.0.2). |
| **B. Qual path correto do chart?** | **`/home/porvir5g/gtp5g/trisla/helm/trisla-portal`** ou, a partir da raiz do repo: **`helm/trisla-portal`**. |
| **C. Values local batem com o manifest do cluster?** | Estrutura sim: `frontend.image.repository`, `frontend.image.digest`, `frontend.image.tag`. Valores não: values do release têm digest 79032610...; deployment/pod no cluster têm digest 2fcb07a6... (já documentado na divergência acima). |
| **D. Existe chart fora do repo atual?** | Não é necessário: o chart está no repo em **`helm/trisla-portal`**. Existem outras cópias (trisla-portal/helm/trisla-portal, backups, snapshots); a referência canônica para o release no namespace trisla é **`helm/trisla-portal`**. |
| **E. Comando exato final (sem placeholder)?** | Ver bloco abaixo. |

### Aviso sobre template e digest

O manifest no cluster mostra a imagem do frontend em formato **repo@digest**. O chart em `helm/trisla-portal` possui `_helpers.tpl` com helper `trisla-portal.image` que suporta digest (repo@digest quando `frontend.image.digest` está definido). O arquivo `templates/frontend-deployment.yaml` atual usa apenas `repository:tag`. Se ao fazer upgrade o template renderizar `repository:tag` com `tag=""`, a imagem ficaria inválida (`repo:`). Antes de executar o upgrade, fazer um dry-run e conferir a linha `image:` do frontend no manifest gerado; se não sair no formato `repo@sha256:...`, o chart em uso na rev 55 pode ser de uma versão que usa o helper no deployment (não alterar código nesta auditoria).

---

## Comando exato de helm upgrade (NÃO EXECUTADO)

Path do chart validado: **`helm/trisla-portal`** (ou path absoluto `/home/porvir5g/gtp5g/trisla/helm/trisla-portal`).

**Comando final 100% pronto para execução (ainda sem executar):**

```bash
helm upgrade trisla-portal /home/porvir5g/gtp5g/trisla/helm/trisla-portal -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835 \
  --set frontend.image.tag="" \
  --reuse-values
```

Alternativa usando path relativo (executar a partir da raiz do repo `/home/porvir5g/gtp5g/trisla`):

```bash
helm upgrade trisla-portal helm/trisla-portal -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835 \
  --set frontend.image.tag="" \
  --reuse-values
```

**Imagem nova usada no comando:**  
`ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835`

**Não executar** até validar em ambiente controlado. Recomenda-se antes: `helm template trisla-portal helm/trisla-portal -n trisla --set frontend.image.digest=sha256:c0fa3cf... --set frontend.image.tag="" ...` e conferir se a imagem do frontend sai como `repo@sha256:c0fa3cf...`.

---

## VALIDAÇÃO FINAL DE RENDERIZAÇÃO

**Objetivo:** Confirmar se o chart local `helm/trisla-portal` renderiza o frontend em formato **repo@sha256** (digest) e não em **repository:tag**. Sem alterar chart, values ou templates; apenas renderizar e auditar. **Upgrade não executado.**

### Comandos executados

- **Observação:** `helm template` **não** aceita a flag `--reuse-values` (válida apenas para `helm upgrade`/`helm install`). A validação foi feita com os mesmos `--set` sem `--reuse-values`.

```bash
helm template trisla-portal helm/trisla-portal -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835 \
  --set frontend.image.tag="" \
  2>&1 | grep -A5 "name: trisla-portal-frontend"
```

**Saída (trecho):**
```
  name: trisla-portal-frontend
  namespace: trisla
  labels:
    app: trisla-portal-frontend
    component: frontend
spec:
```

```bash
helm template trisla-portal helm/trisla-portal -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835 \
  --set frontend.image.tag="" \
  2>&1 | grep "image:"
```

**Saída:**
```
        image: "ghcr.io/abelisboa/trisla-portal-backend:latest"
        image: "ghcr.io/abelisboa/trisla-portal-frontend:"
```

### Respostas com evidência

| Pergunta | Resposta |
|----------|----------|
| **A. Linha image renderizada do frontend** | `image: "ghcr.io/abelisboa/trisla-portal-frontend:"` |
| **B. Sai repo@digest?** | **Não.** O frontend não sai no formato `repo@sha256:...`. |
| **C. Sai repository:tag?** | **Sim.** O template usa `{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}`; com `tag=""` resulta em `repository:` (tag vazia), imagem inválida. |
| **D. Helper trisla-portal.image está sendo usado?** | **Não.** O arquivo `helm/trisla-portal/templates/frontend-deployment.yaml` usa diretamente `repository` e `tag`; não chama `include "trisla-portal.image"`. O helper existe em `_helpers.tpl` mas não é referenciado no deployment do frontend. |
| **E. Chart local corresponde ao chart que gerou a revisão atual?** | **Não.** No cluster, o manifest do trisla-portal mostra frontend em formato **repo@digest**. O chart local renderiza **repository:tag** (com tag vazia). Logo o chart que gerou a revisão atual (55) provavelmente era uma versão em que o template do frontend usava o helper para digest. |

### REGRA FINAL

- **Se renderizar repo@digest:** liberar comando final de upgrade.
- **Se não renderizar:** parar imediatamente e documentar divergência.

**Resultado:** O chart local **não** renderiza repo@digest; renderiza `ghcr.io/abelisboa/trisla-portal-frontend:` (repository:tag com tag vazia).  

**Ação:** **Parar.** Divergência documentada. **Não liberar** o comando de upgrade com o chart atual. **Não executar deploy** até que o template do frontend use o helper `trisla-portal.image` (ou equivalente) para que a imagem saia em formato repo@sha256 quando `frontend.image.digest` estiver definido.

---

## Checklist pós-upgrade (quando o deploy for executado)

- [ ] `kubectl -n trisla get deployment trisla-portal-frontend -o jsonpath='{.spec.template.spec.containers[0].image}'` → deve retornar `ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835`
- [ ] `kubectl -n trisla get pods -l app=trisla-portal-frontend -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'` → mesmo digest
- [ ] Pod em Running e Ready (1/1)
- [ ] Validação de bundle em runtime: dentro do pod, existir chunk JS contendo "Criar SLA PNL" e "slaInterpret" (ex.: `kubectl -n trisla exec <pod> -- grep -l "slaInterpret" /usr/share/nginx/html/_next/static/chunks/*.js`)
- [ ] Teste funcional: abrir Menu 2, informar frase natural, clicar Interpretar e conferir resposta real do backend (sem mock)

---

## Risco de regressão identificado

1. **Values desatualizados:** Os values atuais do trisla-portal (digest 79032610...) não refletem o digest em execução (2fcb07a6...). Usar `--reuse-values` e sobrescrever apenas `frontend.image.*` mantém o restante da configuração e reduz risco de mudança indesejada em backend ou outros parâmetros.
2. **Chart no repo:** O chart trisla-portal está em `helm/trisla-portal` (versão 1.0.2). Usar esse path no upgrade; confirmar que o template do frontend renderiza imagem em formato repo@digest antes de executar.
3. **Um único deployment de frontend:** Alterar a imagem do trisla-portal-frontend afeta todo o portal; garantir que a imagem com digest c0fa3cf... é a desejada (build do Menu 2) antes do upgrade.
4. **Rollback:** Em caso de problema, `helm rollback trisla-portal 55 -n trisla` volta para a revisão atual (digest 2fcb07a6...).

---

**Auditoria apenas documental. Nenhum deploy, upgrade ou alteração de código foi executado.**
