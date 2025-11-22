# Guia de Publicação de Imagens GHCR — TriSLA

**Versão:** 1.0  
**Data:** 2025-11-22  
**Objetivo:** Publicar todas as imagens Docker dos módulos TriSLA no GitHub Container Registry (GHCR)

---

## Pré-requisitos

### 1. Token GHCR

Crie um **Personal Access Token (PAT)** no GitHub com as seguintes permissões:

- `write:packages` — Para publicar imagens
- `read:packages` — Para ler imagens (opcional, mas recomendado)

**Como criar:**
1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione os scopes: `write:packages`, `read:packages`
4. Copie o token gerado

### 2. Docker ou Podman

- **Docker:** Versão ≥ 20.10
- **Podman:** Versão ≥ 4.0 (compatível com Docker CLI)

### 3. Docker Buildx (Recomendado)

Para builds multi-plataforma:

```bash
docker buildx create --use
```

---

## Publicação Automática

### Método 1: Script Bash (Linux/macOS/WSL)

```bash
# Definir token
export GHCR_TOKEN="ghp_xxxxxxxxxxxx"

# Executar script
./scripts/publish_all_images_ghcr.sh
```

### Método 2: Script PowerShell (Windows)

```powershell
# Definir token
$env:GHCR_TOKEN = "ghp_xxxxxxxxxxxx"

# Executar script
.\scripts\publish_all_images_ghcr.ps1
```

### Método 3: Manual (Passo a Passo)

#### 1. Login no GHCR

```bash
echo $GHCR_TOKEN | docker login ghcr.io -u abelisboa --password-stdin
```

#### 2. Construir e Publicar Cada Módulo

```bash
# SEM-CSMF
docker buildx build \
  -t ghcr.io/abelisboa/trisla-sem-csmf:latest \
  -f apps/sem-csmf/Dockerfile \
  --platform linux/amd64 \
  --push \
  ./apps/sem-csmf

# ML-NSMF
docker buildx build \
  -t ghcr.io/abelisboa/trisla-ml-nsmf:latest \
  -f apps/ml-nsmf/Dockerfile \
  --platform linux/amd64 \
  --push \
  ./apps/ml-nsmf

# Decision Engine
docker buildx build \
  -t ghcr.io/abelisboa/trisla-decision-engine:latest \
  -f apps/decision-engine/Dockerfile \
  --platform linux/amd64 \
  --push \
  ./apps/decision-engine

# BC-NSSMF
docker buildx build \
  -t ghcr.io/abelisboa/trisla-bc-nssmf:latest \
  -f apps/bc-nssmf/Dockerfile \
  --platform linux/amd64 \
  --push \
  ./apps/bc-nssmf

# SLA-Agent Layer
docker buildx build \
  -t ghcr.io/abelisboa/trisla-sla-agent-layer:latest \
  -f apps/sla-agent-layer/Dockerfile \
  --platform linux/amd64 \
  --push \
  ./apps/sla-agent-layer

# NASP Adapter
docker buildx build \
  -t ghcr.io/abelisboa/trisla-nasp-adapter:latest \
  -f apps/nasp-adapter/Dockerfile \
  --platform linux/amd64 \
  --push \
  ./apps/nasp-adapter

# UI Dashboard
docker buildx build \
  -t ghcr.io/abelisboa/trisla-ui-dashboard:latest \
  -f apps/ui-dashboard/Dockerfile \
  --platform linux/amd64 \
  --push \
  ./apps/ui-dashboard
```

#### 3. Validar Publicação

```bash
# Executar auditoria
python3 scripts/audit_ghcr_images.py

# Verificar relatório
cat docs/IMAGES_GHCR_MATRIX.md
```

---

## Validação Pós-Publicação

### 1. Verificar Imagens no GHCR

Acesse: https://github.com/users/abelisboa/packages

Você deve ver 7 pacotes:
- `trisla-sem-csmf`
- `trisla-ml-nsmf`
- `trisla-decision-engine`
- `trisla-bc-nssmf`
- `trisla-sla-agent-layer`
- `trisla-nasp-adapter`
- `trisla-ui-dashboard`

### 2. Testar Pull Local

```bash
# Testar pull de uma imagem
docker pull ghcr.io/abelisboa/trisla-sem-csmf:latest

# Verificar se imagem foi baixada
docker images | grep ghcr.io/abelisboa/trisla
```

### 3. Executar Auditoria Automática

```bash
python3 scripts/audit_ghcr_images.py
```

O script irá:
- Verificar existência de cada imagem
- Listar tags disponíveis
- Obter digests
- Atualizar `docs/IMAGES_GHCR_MATRIX.md`

---

## Troubleshooting

### Problema: "unauthorized: authentication required"

**Causa:** Token GHCR inválido ou expirado.

**Solução:**
1. Verificar se `GHCR_TOKEN` está definido corretamente
2. Gerar novo token no GitHub
3. Fazer login novamente: `echo $GHCR_TOKEN | docker login ghcr.io -u abelisboa --password-stdin`

### Problema: "failed to solve: failed to compute cache key"

**Causa:** Dockerfile ou contexto incorreto.

**Solução:**
1. Verificar se Dockerfile existe: `ls apps/<module>/Dockerfile`
2. Verificar se está na pasta raiz do projeto
3. Verificar se o contexto do build está correto

### Problema: "buildx not found"

**Causa:** Docker Buildx não instalado.

**Solução:**
```bash
# Instalar buildx
docker buildx create --use

# Ou usar docker build tradicional (sem --platform)
docker build -t ghcr.io/abelisboa/trisla-<module>:latest -f apps/<module>/Dockerfile ./apps/<module>
docker push ghcr.io/abelisboa/trisla-<module>:latest
```

### Problema: "denied: permission_denied"

**Causa:** Token sem permissão `write:packages`.

**Solução:**
1. Gerar novo token com permissão `write:packages`
2. Fazer login novamente

---

## Estrutura de Imagens

### Nomenclatura

- **Formato:** `ghcr.io/abelisboa/trisla-<module-name>:<tag>`
- **Tag padrão:** `latest`
- **Tags recomendadas:** Versões semânticas (ex: `v1.0.0`)

### Módulos Publicados

| Módulo | Imagem | Dockerfile |
|--------|--------|------------|
| SEM-CSMF | `ghcr.io/abelisboa/trisla-sem-csmf` | `apps/sem-csmf/Dockerfile` |
| ML-NSMF | `ghcr.io/abelisboa/trisla-ml-nsmf` | `apps/ml-nsmf/Dockerfile` |
| Decision Engine | `ghcr.io/abelisboa/trisla-decision-engine` | `apps/decision-engine/Dockerfile` |
| BC-NSSMF | `ghcr.io/abelisboa/trisla-bc-nssmf` | `apps/bc-nssmf/Dockerfile` |
| SLA-Agent Layer | `ghcr.io/abelisboa/trisla-sla-agent-layer` | `apps/sla-agent-layer/Dockerfile` |
| NASP Adapter | `ghcr.io/abelisboa/trisla-nasp-adapter` | `apps/nasp-adapter/Dockerfile` |
| UI Dashboard | `ghcr.io/abelisboa/trisla-ui-dashboard` | `apps/ui-dashboard/Dockerfile` |

---

## Publicação com Tags de Versão

Para publicar com tag de versão específica:

```bash
VERSION="v1.0.0"

docker buildx build \
  -t ghcr.io/abelisboa/trisla-sem-csmf:latest \
  -t ghcr.io/abelisboa/trisla-sem-csmf:$VERSION \
  -f apps/sem-csmf/Dockerfile \
  --platform linux/amd64 \
  --push \
  ./apps/sem-csmf
```

---

## Integração com CI/CD

### GitHub Actions

Exemplo de workflow para publicar automaticamente:

```yaml
name: Publish Images to GHCR

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        run: |
          export GHCR_TOKEN=${{ secrets.GITHUB_TOKEN }}
          ./scripts/publish_all_images_ghcr.sh
```

---

## Referências

- **Matriz de Imagens:** `docs/IMAGES_GHCR_MATRIX.md`
- **Script de Auditoria:** `scripts/audit_ghcr_images.py`
- **Script de Publicação:** `scripts/publish_all_images_ghcr.sh` (Bash) ou `scripts/publish_all_images_ghcr.ps1` (PowerShell)

---

**Versão:** 1.0  
**ENGINE MASTER:** Sistema de Publicação GHCR TriSLA

