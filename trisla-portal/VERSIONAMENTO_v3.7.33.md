# Versionamento v3.7.33

## Correção de Regressão - Estabilização Kubernetes

### Arquivos Atualizados

#### Frontend
- ✅ `frontend/package.json` → `"version": "3.7.33"`
- ✅ `frontend/src/lib/version.ts` → `PORTAL_VERSION = '3.7.33'`
- ✅ `frontend/src/lib/runtimeConfig.ts` → **NOVO**: Configuração Kubernetes-safe
- ✅ `frontend/Dockerfile` → Default alterado para Service Kubernetes

#### Helm Chart
- ✅ `helm/trisla-portal/Chart.yaml` → `version: 3.7.33`, `appVersion: "3.7.33"`
- ✅ `helm/trisla-portal/values.yaml` → `frontend.image.tag: v3.7.33`
- ✅ `helm/trisla-portal/values.yaml` → Removido hardcode de `localhost` em env

### Mudanças Técnicas

#### Nova Configuração (`runtimeConfig.ts`)

```typescript
export const API_BASE_URL = (() => {
  if (typeof window === 'undefined') {
    // Server-side (SSR)
    return process.env.INTERNAL_API_URL ?? 
           process.env.NEXT_PUBLIC_TRISLA_API_BASE_URL ?? 
           'http://trisla-portal-backend:8001/api/v1';
  }
  
  // Client-side (browser)
  return process.env.NEXT_PUBLIC_TRISLA_API_BASE_URL ?? 
         'http://trisla-portal-backend:8001/api/v1';
})();
```

**Diferença chave**: Default é Service Kubernetes, não `localhost`.

#### Dockerfile

**Antes (v3.7.32)**:
```dockerfile
ARG NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1
```

**Agora (v3.7.33)**:
```dockerfile
ARG NEXT_PUBLIC_TRISLA_API_BASE_URL=http://trisla-portal-backend:8001/api/v1
```

### Build e Deploy

#### Build para Kubernetes (Produção)

```bash
cd frontend
docker build -t ghcr.io/abelisboa/trisla-portal-frontend:v3.7.33 .
```

**Não precisa passar build-arg** - default é Kubernetes-safe.

#### Build para Desenvolvimento Local (Túnel SSH)

```bash
cd frontend
docker build -t ghcr.io/abelisboa/trisla-portal-frontend:v3.7.33 \
  --build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1 \
  .
```

#### Push

```bash
docker push ghcr.io/abelisboa/trisla-portal-frontend:v3.7.33
```

#### Deploy no NASP

```bash
helm upgrade --install trisla-portal ./helm/trisla-portal \
  -n trisla \
  --create-namespace \
  --wait
```

**Não precisa passar variáveis de ambiente** - default funciona em Kubernetes.

### Verificação Pós-Deploy

1. **Pods rodando**:
```bash
kubectl get pods -n trisla | grep portal
```

2. **Serviços**:
```bash
kubectl get svc -n trisla | grep portal
```

3. **Teste via túnel SSH** (se necessário):
```bash
# Criar túnel
ssh -L 32001:localhost:32001 -L 32002:localhost:32002 porvir5g@node1

# Testar
curl http://localhost:32001
curl http://localhost:32002/health
```

4. **Console do browser**: Verificar ausência de erros de conexão

### Comparação com Versões Anteriores

| Versão | Default API URL | Kubernetes | Desenvolvimento Local |
|--------|----------------|------------|----------------------|
| v3.7.31 | Service Kubernetes | ✅ | Requer override |
| v3.7.32 | `localhost:8001` ❌ | ❌ | ✅ |
| v3.7.33 | Service Kubernetes | ✅ | Requer override |

### Notas Importantes

1. **Backend não foi alterado**: Mantém tag `v3.7.11`
2. **Compatibilidade**: Funciona com Helm chart existente sem modificações
3. **Rollback**: Se necessário, pode fazer rollback para `v3.7.31`

