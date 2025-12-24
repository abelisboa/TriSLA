# Matriz de Imagens GHCR — TriSLA

**Data:** 2025-12-03  
**Versão:** 3.7.8  
**GHCR User:** abelisboa  
**Status:** ✅ Todas as imagens validadas e prontas para produção

**Última atualização:** 2025-12-03 — Adicionadas tags v3.7.8 para sla-agent-layer e ui-dashboard (correções de bugfix)

---

## Introdução Conceitual

Todas as imagens Docker do TriSLA são publicadas no **GitHub Container Registry (GHCR)**.
Esta matriz é baseada em verificações reais via:

```bash
docker manifest inspect ghcr.io/abelisboa/trisla-<module-name>:latest
```

Uma imagem é considerada **OK** se o comando acima retornar código de saída 0.

### Estrutura de Nomenclatura

- **Registry base:** `ghcr.io/abelisboa/`
- **Formato:** `ghcr.io/abelisboa/trisla-<module-name>`
- **Tag padrão avaliada:** `latest`

---

## Tabela Principal de Imagens

| Módulo | Imagem GHCR (com tag) | Tag Padrão | Status de Auditoria | Observação |
|--------|-----------------------|------------|---------------------|------------|
| SEM-CSMF | `ghcr.io/abelisboa/trisla-sem-csmf:latest` | ✅ | ✅ OK | ontologia trisla.ttl |
| ML-NSMF | `ghcr.io/abelisboa/trisla-ml-nsmf:latest` | ✅ | ✅ OK | modelo ML (viability_model.pkl), scaler |
| Decision Engine | `ghcr.io/abelisboa/trisla-decision-engine:latest` | ✅ | ✅ OK | consumidor I-03, produtor I-04/I-05 |
| BC-NSSMF | `ghcr.io/abelisboa/trisla-bc-nssmf:latest` | ✅ | ✅ OK | integração com Besu |
| SLA-Agent Layer | `ghcr.io/abelisboa/trisla-sla-agent-layer:latest` | ✅ | ✅ OK | agentes RAN/Transporte/Core |
| SLA-Agent Layer | `ghcr.io/abelisboa/trisla-sla-agent-layer:v3.7.8` | ✅ | ✅ OK | correção: python-multipart, bugfix crashloop |
| NASP Adapter | `ghcr.io/abelisboa/trisla-nasp-adapter:latest` | ✅ | ✅ OK | interface com NASP real |
| UI Dashboard | `ghcr.io/abelisboa/trisla-ui-dashboard:latest` | ✅ | ✅ OK | interface de observação TriSLA |
| UI Dashboard | `ghcr.io/abelisboa/trisla-ui-dashboard:v3.7.8` | ✅ | ✅ OK | correção: nginx proxy_pass com variáveis, bugfix DNS |

---

## Status de Auditoria

**Última auditoria:** 2025-11-22 14:36:16 UTC

**Resumo:**
- ✅ Imagens OK: 7
- ❌ Imagens faltando: 0

---

## Como interpretar este relatório

- **✅ OK** : a imagem foi localizada com sucesso no GHCR via `docker manifest inspect`.
- **❌ FALTANDO** : o comando retornou erro. Verifique se:
  - a imagem realmente foi publicada com a tag `latest`; ou
  - existe algum problema de autenticação ou de rede com o registry.

---

## Como Publicar Imagens Faltantes

Se uma imagem estiver marcada como **FALTANDO**, siga estes passos:

### Método Manual (Recomendado)

1. **Login no GHCR:**
   ```bash
   echo $GHCR_TOKEN | docker login ghcr.io -u abelisboa --password-stdin
   ```

2. **Build e push da imagem:**
   ```bash
   docker buildx build \
     -t ghcr.io/abelisboa/trisla-<module-name>:latest \
     -f apps/<module-name>/Dockerfile \
     --platform linux/amd64 \
     --push \
     ./apps/<module-name>
   ```

3. **Validar imagem publicada:**
   ```bash
   docker manifest inspect ghcr.io/abelisboa/trisla-<module-name>:latest
   ```

**Guia completo:** `docs/ghcr/GHCR_PUBLISH_GUIDE.md`

**Nota:** Para build e publicação em lote, use os scripts disponíveis em `scripts/` (ex: `build-all-images.sh`, `push-all-images.ps1`).

---

**Versão:** 2.0
**ENGINE MASTER:** Sistema de Auditoria GHCR TriSLA (docker-based)
