# RECUPERAÇÃO DO FRONTEND TRISLA (ImagePullBackOff)

**Data:** 2026-03-16 / 2026-03-17  
**Escopo:** Restaurar o frontend para o último digest funcional após falha da revisão 56 (digest não encontrado no registry). Apenas frontend; backend e demais módulos não alterados.

---

## REGRAS OBSERVADAS

- Mexer somente no frontend.
- Não alterar: backend, SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, NASP Adapter, observabilidade, contratos ou outros módulos estáveis.

---

## FASE 1 — ROLLBACK IMEDIATO DO FRONTEND

### Comando executado

```bash
cd /home/porvir5g/gtp5g/trisla

helm upgrade trisla-portal helm/trisla-portal -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772 \
  --set frontend.image.tag="" \
  --reuse-values
```

**Resultado Helm:** Release upgraded. **REVISION: 57.** STATUS: deployed.

### Validações obrigatórias

| Validação | Resultado |
|-----------|-----------|
| `kubectl -n trisla rollout status deployment/trisla-portal-frontend` | `deployment "trisla-portal-frontend" successfully rolled out` |
| Deployment image | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772` |
| Pod imageID | `ghcr.io/abelisboa/trisla-portal-frontend@sha256:2fcb07a60e5a6752d95d13f5ab375af0d52a43b3335e5fa1beb7c990b10d0772` |
| Pod status | `1/1 Running` (trisla-portal-frontend-7574c6948f-xxx) |

**Conclusão Fase 1:** Frontend restaurado com digest estável **sha256:2fcb07a6...**. Portal operacional. Parar e documentar conforme regra.

---

## FASE 2 — AUDITORIA DO DIGEST FALHO

**Digest que falhou no deploy (rev 56):**  
`sha256:c0fa3cfdf40d1d124cf839c28a62464f3ba0bb4a94dc75d811ed9d5245acd835`

**Objetivo:** Entender por que o digest c0fa3cf... não foi pullável, sem alterar código.

### Verificações realizadas

1. **Imagem foi realmente publicada?**  
   **Não confirmado.** O registry ghcr.io retornou "not found" / "manifest unknown" para esse digest.

2. **Digest remoto existe?**  
   **Não.** Consulta com skopeo (com authfile) ao repositório `ghcr.io/abelisboa/trisla-portal-frontend@sha256:c0fa3cf...` retornou:  
   `reading manifest sha256:c0fa3cf... in ghcr.io/abelisboa/trisla-portal-frontend: manifest unknown`

3. **Digest remoto confere com o usado no helm upgrade?**  
   Não é possível conferir porque o manifest com esse digest **não existe** no registry para esse repositório. O digest usado no upgrade (c0fa3cf...) não está disponível em ghcr.io/abelisboa/trisla-portal-frontend.

4. **Houve erro de push incompleto?**  
   **Provável.** O digest c0fa3cf... pode ter sido obtido localmente (ex.: após `podman build`) mas o `podman push` pode não ter sido executado, ter falhado ou ter sido feito para outro repositório/tag. O registry não possui esse manifest.

5. **Erro de autenticação/visibilidade do GHCR?**  
   O cluster (kubelet) e o skopeo com authfile acessam o mesmo registry. O cluster retornou "not found"; o skopeo com authfile retornou "manifest unknown". Isso aponta para **ausência do manifest** no repo (imagem não publicada ou publicada com outro digest/tag), não apenas para falha de autenticação (que tipicamente seria "unauthorized" ou "forbidden").

6. **Digest local vs digest remoto?**  
   O digest c0fa3cf... usado no helm upgrade provavelmente era o **digest local** da imagem construída (ex.: v3.10.16-pnl). Se o push não foi feito ou falhou, o **digest remoto** no GHCR nunca passou a ser esse; ou a imagem foi pushada com outra tag e o digest efetivo no registry é outro.

### Conclusão da auditoria

- **Causa raiz:** A imagem com digest `sha256:c0fa3cf...` **não existe** (ou não está acessível) no repositório `ghcr.io/abelisboa/trisla-portal-frontend`. O deploy da rev 56 usou um digest que não foi publicado com sucesso nesse repo.
- **Recomendação:** Para futuros deploys de frontend, **sempre** obter o digest **após** o push (ex.: via `skopeo inspect` no `docker://...:<tag>`) e usar **esse** digest no `helm upgrade`. Nunca usar apenas o digest local do build antes de validar que o mesmo digest existe no registry.

---

## FASE 3 — REGRA OBRIGATÓRIA PARA FUTUROS DEPLOYS DE FRONTEND

**Nunca** executar upgrade do frontend antes de validar, **nesta ordem**:

1. Build local do frontend  
2. Push da imagem  
3. Obter digest **remoto** do GHCR (após o push)  
4. Validar que o digest remoto existe e é pullável (ex.: skopeo inspect)  
5. Só então executar `helm upgrade` do release **trisla-portal** com esse digest  

Usar a rotina manual que já funcionava anteriormente; não inventar novo método sem essa validação.

### Pipeline obrigatório

```bash
cd /home/porvir5g/gtp5g/trisla

TS=$(date -u +%Y%m%dT%H%M%SZ)

# 1. Build
podman build --format docker \
  -t ghcr.io/abelisboa/trisla-portal-frontend:${TS} \
  -f apps/portal-frontend/Dockerfile \
  apps/portal-frontend

# 2. Push
podman push ghcr.io/abelisboa/trisla-portal-frontend:${TS}

# 3. Obter digest REMOTO (obrigatório antes do upgrade)
REMOTE_DIGEST=$(skopeo inspect --authfile ~/.config/containers/auth.json \
  docker://ghcr.io/abelisboa/trisla-portal-frontend:${TS} | jq -r .Digest)

echo "REMOTE_DIGEST=${REMOTE_DIGEST}"

# 4. Conferir que o digest remoto é o que será usado no upgrade
# Só depois executar:
helm upgrade trisla-portal helm/trisla-portal -n trisla \
  --set frontend.image.repository=ghcr.io/abelisboa/trisla-portal-frontend \
  --set frontend.image.digest=${REMOTE_DIGEST} \
  --set frontend.image.tag="" \
  --reuse-values
```

**Obrigatório:** Antes de qualquer novo `helm upgrade`, confirmar que o digest retornado pelo skopeo (remoto) é exatamente o digest usado em `--set frontend.image.digest`. Não usar digest apenas do build local.

### Validações obrigatórias pós-deploy

```bash
kubectl -n trisla rollout status deployment/trisla-portal-frontend

kubectl -n trisla get deployment trisla-portal-frontend \
  -o jsonpath='{.spec.template.spec.containers[0].image}'; echo

kubectl -n trisla get pod -l app=trisla-portal-frontend \
  -o jsonpath='{.items[0].status.containerStatuses[0].imageID}'; echo

POD=$(kubectl -n trisla get pod -l app=trisla-portal-frontend -o jsonpath='{.items[0].metadata.name}')
kubectl -n trisla exec $POD -- sh -c "grep -R 'slaInterpret' /usr/share/nginx/html || true"
kubectl -n trisla exec $POD -- sh -c "grep -R 'Criar SLA PNL' /usr/share/nginx/html || true"
```

---

## REGRAS FINAIS

1. Frontend recuperado com digest estável **sha256:2fcb07a6...** (revisão 57).  
2. Falha do digest c0fa3cf... documentada: imagem não presente no registry.  
3. Backend e outros módulos não foram alterados.  
4. Não avançar para Menu 3 até que novo build/push do frontend Menu 2 siga o pipeline acima e o digest remoto seja validado.  
5. Parar após recuperação e documentação.

---

**Recuperação concluída. Portal operacional com frontend no digest 2fcb07a6...**
