# AUDITORIA DE DIVERGÊNCIA DO CHART DO RELEASE trisla-portal (Frontend)

**Data:** 2026-03-16  
**Escopo:** Descobrir por que o cluster usa imagem em formato **repo@digest** enquanto o chart local **helm/trisla-portal** renderiza **repository:tag**. Sem alteração de código, chart, values; sem deploy. Somente auditar e documentar.

---

## 1. Evidências coletadas

### 1.1 Histórico do release

```bash
helm history trisla-portal -n trisla
```

**Saída:**
```
REVISION	UPDATED                 	STATUS    	CHART              	APP VERSION	DESCRIPTION     
46      	Thu Mar 12 16:26:01 2026	superseded	trisla-portal-1.0.2	1.0.0      	Upgrade complete
47      	Thu Mar 12 16:30:05 2026	superseded	trisla-portal-1.0.2	1.0.0      	Upgrade complete
...
55      	Thu Mar 12 17:27:10 2026	deployed  	trisla-portal-1.0.2	1.0.0      	Upgrade complete
```

- Apenas revisões 46–55 visíveis (todas trisla-portal-1.0.2).
- Não é possível, só com esse histórico, identificar a primeira revisão que passou a usar repo@digest no frontend.

### 1.2 Manifest completo do release (armazenado pelo Helm)

```bash
helm get manifest trisla-portal -n trisla > /tmp/trisla-portal.manifest.txt
```

**Linhas com `image:` no manifest:**
```
64:        image: "ghcr.io/abelisboa/trisla-portal-backend:latest"
129:        image: "ghcr.io/abelisboa/trisla-portal-frontend@sha256:7903261048522d920d5e3b0448f8e152dd26955ecaffe88d72146ea19f7d6e02"
```

**Conclusão:** O manifest **gravado** pelo Helm para o release trisla-portal (revisão 55) contém o frontend em formato **repo@digest** (digest 79032610...). Ou seja, o **chart usado no upgrade que gerou a rev 55** era capaz de renderizar repo@digest.

### 1.3 Valores completos do release

```bash
helm get values trisla-portal -n trisla -a > /tmp/trisla-portal.values.all.yaml
```

**Trecho relevante (COMPUTED VALUES):**
```yaml
frontend:
  image:
    digest: sha256:7903261048522d920d5e3b0448f8e152dd26955ecaffe88d72146ea19f7d6e02
    pullPolicy: Always
    repository: ghcr.io/abelisboa/trisla-portal-frontend
    tag: ""
```

Os values do release têm `frontend.image.digest` preenchido e `tag: ""`, coerentes com um template que usa digest quando presente.

### 1.4 Helper de image no chart local

```bash
grep -R "define .*image" -n helm/trisla-portal
grep -R "trisla-portal.image" -n helm/trisla-portal
```

**Resultado:**
- `helm/trisla-portal/templates/_helpers.tpl` linha 1: `{{- define "trisla-portal.image" -}}`
- O helper existe e suporta digest: se `$digest` não vazio, usa `printf "%s@%s" $repo $digest`; senão usa tag.
- **Nenhuma referência** a `trisla-portal.image` ou `include "trisla-portal.image"` nos templates do chart (apenas a definição no _helpers.tpl).

### 1.5 Template do frontend local

**Arquivo:** `helm/trisla-portal/templates/frontend-deployment.yaml` (linhas 1–53 relevantes)

Linha 22:
```yaml
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
```

O template usa **apenas** `repository` e `tag`; **não** chama o helper `trisla-portal.image`. Com `tag: ""`, o render local produz `image: "ghcr.io/abelisboa/trisla-portal-frontend:"` (formato repository:tag com tag vazia, inválido).

### 1.6 Charts duplicados / alternativos no repositório

**Frontend deployment templates:**
```
helm/trisla-portal/templates/frontend-deployment.yaml
trisla-portal/helm/trisla-portal/templates/frontend-deployment.yaml
helm_snapshot_pre_s31_1_20260128_124711/trisla-portal/templates/frontend-deployment.yaml
backup_portal_20260305-140528/.../frontend-deployment.yaml (2 paths)
TriSLA/trisla-portal/helm/trisla-portal/templates/frontend-deployment.yaml
```

**Chart.yaml com name: trisla-portal:**
```
helm/trisla-portal/Chart.yaml
trisla-portal/infra/helm/trisla-portal/Chart.yaml
trisla-portal/helm/trisla-portal/Chart.yaml
helm_snapshot_pre_s31_1_20260128_124711/trisla-portal/Chart.yaml
backup_portal_20260305-140528/... (vários)
TriSLA/trisla-portal/... (2 paths)
```

**Inspeção dos frontend-deployment:** Em todos os paths verificados, a linha da imagem é `{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}`. **Nenhum** usa `include "trisla-portal.image"`. Não foi encontrada no repositório uma versão do chart que use o helper no deployment do frontend.

### 1.7 Deployment atual no cluster

```bash
kubectl -n trisla get deployment trisla-portal-frontend -o yaml > /tmp/trisla-portal-frontend.deployment.yaml
```

**Linha da imagem:**
```
54:        image: ghcr.io/abelisboa/trisla-portal-frontend@sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772
```

**Outras diferenças em relação ao manifest do Helm:**
- **Digest diferente:** cluster = 2fcb07a6...; manifest Helm = 79032610...
- **Anotações:** `kubectl.kubernetes.io/restartedAt: "2026-03-14T16:46:27-03:00"` (restart após o último upgrade de 12/03).
- **Env adicionais no deployment:** TRISLA_OBS_*, PUBLIC_OBS_PROMETHEUS_URL, PUBLIC_OBS_TEMPO_URL, PUBLIC_OBS_JAEGER_URL, PUBLIC_OBS_GRAFANA_URL, PORT.
- **imagePullSecrets:** `ghcr-secret` presente no deployment; não aparece no manifest Helm.
- **Estratégia:** deployment com `strategy: Recreate`; manifest Helm não define strategy (default RollingUpdate).

Isso mostra que o **recurso Deployment no cluster foi alterado** após o último `helm upgrade` (por patch, `kubectl set image`, restart ou edição manual), ou que o chart/values usados no upgrade já tinham parte dessas diferenças e o manifest armazenado pelo Helm não reflete todas.

### 1.8 Comparação direta: image no manifest Helm vs deployment

| Origem              | Linha image (frontend) |
|---------------------|------------------------|
| Manifest Helm (rev 55) | `image: "ghcr.io/abelisboa/trisla-portal-frontend@sha256:7903261048522d920d5e3b0448f8e152dd26955ecaffe88d72146ea19f7d6e02"` |
| Deployment no cluster  | `image: ghcr.io/abelisboa/trisla-portal-frontend@sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772` |

- Ambos estão em formato **repo@digest**.
- **Digests diferentes:** 79032610 (Helm) vs 2fcb07a6 (cluster) — o deployment atual não corresponde ao último manifest aplicado pelo Helm.

---

## 2. Hipóteses validadas

| Hipótese | Avaliação |
|----------|-----------|
| **A. Release gerado por versão diferente do chart** | **Provável.** O manifest do release (helm get manifest) está em repo@digest; o chart local não gera isso. Logo uma **versão do chart** que usava o helper (ou equivalente) no frontend-deployment foi usada no upgrade; essa versão **não** está nas cópias atuais do repo (helm/trisla-portal, trisla-portal/helm, backups, TriSLA, snapshot). |
| **B. Existe outro chart do trisla-portal no ambiente** | **Possível.** O upgrade pode ter sido feito a partir de outro path (ex.: chart empacotado ou diretório fora do repo atual). Não é possível confirmar só com os arquivos do repo. |
| **C. Upgrade anterior com chart externo** | **Possível.** Compatível com A e B. |
| **D. Deployment alterado por outro método entre revisões** | **Comprovado.** Digest no cluster (2fcb07a6) ≠ digest no manifest Helm (79032610); restartedAt 14/03; env e imagePullSecrets extras. O deployment sofreu alterações fora do último helm upgrade (ou o manifest armazenado não reflete o que foi de fato aplicado). |
| **E. Manifest atual do cluster não corresponde ao chart no repositório** | **Comprovado.** O chart local renderiza `repository:tag` (tag vazia); o manifest armazenado pelo Helm tem repo@digest. O chart no repositório atual **não** é o que gerou o manifest da rev 55. |

---

## 3. Respostas às perguntas do documento

1. **Qual foi a primeira revisão do trisla-portal que passou a usar repo@digest no frontend?**  
   O histórico exibido (rev 46–55) não permite identificar. O que se sabe é que o **manifest da rev 55** (armazenado pelo Helm) já está em repo@digest (79032610).

2. **Isso veio de chart, patch manual, ou outra fonte?**  
   O formato **repo@digest** no manifest do Helm veio do **chart** usado no upgrade (aquele chart renderizava digest). O **digest** que está no cluster hoje (2fcb07a6) é diferente do do manifest (79032610), então a imagem em runtime foi alterada depois por outro meio (patch, set image, etc.).

3. **O chart local pode ser considerado canônico?**  
   **Não**, para o comportamento “frontend em repo@digest”. O chart em **helm/trisla-portal** é o candidato a canônico no repo, mas ele **não** gera repo@digest; o manifest da rev 55 foi gerado por uma versão do chart que o repositório atual não contém (ou não foi localizada).

4. **O deployment atual está driftado em relação ao chart?**  
   **Sim**, em dois níveis:  
   - Em relação ao **chart local:** o chart renderiza repository:tag; o deployment está em repo@digest.  
   - Em relação ao **manifest do Helm:** mesmo estando ambos em repo@digest, o digest e outros campos (env, imagePullSecrets, restartedAt) diferem.

5. **Qual é a forma segura de avançar sem regressão?**  
   Não fazer deploy do Menu 2 com o chart atual até que: (a) o template do frontend use o helper (ou lógica equivalente) para imagem em repo@digest quando `frontend.image.digest` estiver definido, e (b) se desejar alinhar totalmente ao Helm, reaplicar o deployment via Helm (evitando patch/set image fora do Helm) e validar o render com `helm template` antes de qualquer upgrade.

---

## 4. Hipótese mais provável

O release trisla-portal (rev 55) foi gerado por um **chart trisla-portal-1.0.2** cujo **frontend-deployment** usava o helper `trisla-portal.image` (ou lógica equivalente), produzindo **repo@digest** quando `frontend.image.digest` estava definido. Esse chart **não** corresponde ao que está em **helm/trisla-portal** (e nas outras cópias verificadas no repo), onde o frontend-deployment usa apenas `repository:tag`. Em seguida, o deployment no cluster foi alterado (imagem, env, restart, imagePullSecrets), gerando drift em relação ao manifest armazenado pelo Helm.

---

## 5. Conclusão técnica

- O **manifest armazenado** pelo Helm para trisla-portal está em **repo@digest** (79032610). Portanto o cluster “consegue” usar repo@digest porque o **chart usado no upgrade** já gerava esse formato.
- O **chart local** (helm/trisla-portal) **não** gera repo@digest para o frontend: o template não usa o helper; nenhuma cópia do chart no repositório usa o helper no frontend-deployment.
- A **origem canônica** do comportamento repo@digest (chart que usa o helper no frontend) **não** está comprovada no repositório atual: não foi encontrado nenhum frontend-deployment que use `trisla-portal.image`. Logo **não se pode afirmar** que o chart atual é a origem canônica do que está no release.

---

## 6. Recomendação segura de próximo passo

- **Não autorizar deploy do Menu 2** com o chart **helm/trisla-portal** no estado atual, pois o template do frontend não renderiza repo@digest e um upgrade geraria imagem inválida ou indesejada.
- **Próximos passos recomendados (antes de qualquer deploy):**
  1. Ajustar **apenas o template** `helm/trisla-portal/templates/frontend-deployment.yaml` para usar o helper `trisla-portal.image` na linha da imagem do frontend (ex.: `image: {{ include "trisla-portal.image" .Values.frontend.image }}`), mantendo chart/values e comportamento do backend inalterados.
  2. Validar com `helm template` que a imagem do frontend sai no formato `repo@sha256:...` quando `frontend.image.digest` estiver definido.
  3. Só então reavaliar a autorização do comando de upgrade do Menu 2 (digest c0fa3cf...), ainda sem executar até aprovação explícita.

---

## 7. Regra final

**Se a auditoria não provar origem canônica do repo@digest no repositório atual:**  
**Não autorizar deploy do Menu 2.**

**Resultado desta auditoria:** A origem canônica (template que gera repo@digest) **não** foi encontrada no repositório. O manifest do Helm foi gerado por um chart que não corresponde ao chart local.  

**Ação:** **Não autorizar deploy do Menu 2** com o chart no estado atual. Parar após esta documentação.

---

**Auditoria somente de leitura. Nenhum helm upgrade, kubectl patch, set image, rollout restart ou edição de chart/values/código foi executado.**
