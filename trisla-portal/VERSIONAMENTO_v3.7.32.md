# Versionamento v3.7.32

## Arquivos Atualizados

### Frontend
- ✅ `frontend/package.json` → `"version": "3.7.32"`
- ✅ `frontend/src/lib/version.ts` → `PORTAL_VERSION = '3.7.32'`
- ✅ `frontend/Dockerfile` → Removido hardcode, usa `NEXT_PUBLIC_TRISLA_API_BASE_URL`

### Helm Chart
- ✅ `helm/trisla-portal/Chart.yaml` → `version: 3.7.32`, `appVersion: "3.7.32"`
- ✅ `helm/trisla-portal/values.yaml` → `frontend.image.tag: v3.7.32`
- ✅ `helm/trisla-portal/values.yaml` → `frontend.env.NEXT_PUBLIC_TRISLA_API_BASE_URL`

### Backend
- ⚠️ Backend **NÃO** foi alterado (mantém tag `v3.7.11`)
- ⚠️ Backend **NÃO** requer rebuild

## Variáveis de Ambiente

### Frontend (Build Time)
- `NEXT_PUBLIC_TRISLA_API_BASE_URL`: URL base da API (client-side)
  - Default: `http://localhost:8001/api/v1`
  - Pode ser sobrescrito no build do Docker

### Frontend (Runtime)
- `INTERNAL_API_URL`: URL para comunicação server-side (SSR)
  - Default: `http://trisla-portal-backend:8001/api/v1`
  - Usado apenas em server-side rendering

## Build e Deploy

### Build Local
```bash
cd frontend
docker build -t ghcr.io/abelisboa/trisla-portal-frontend:v3.7.32 \
  --build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1 \
  .
```

### Push
```bash
docker push ghcr.io/abelisboa/trisla-portal-frontend:v3.7.32
```

### Deploy no NASP
```bash
helm upgrade --install trisla-portal ./helm/trisla-portal \
  -n trisla \
  --create-namespace \
  --wait
```

## Verificação

Após deploy, verificar:
1. Versão visível no footer do portal
2. Versão visível na página `/modules`
3. Health check funcionando via túnel SSH
4. Sem erros React #418 no console do browser

