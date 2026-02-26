# Changelog v3.7.34

## Correção Definitiva - Same-Origin /api/v1 com Proxy Next.js

### 🎯 Objetivo

Eliminar definitivamente hardcodes de IP/NodePort. O frontend sempre usa `/api/v1` (same-origin) e o Next.js faz proxy interno para o backend via Service Kubernetes.

### ✅ Correções Implementadas

#### 1. Next.js Rewrites (`next.config.js`)

**NOVO**: Adicionado `rewrites()` que faz proxy de `/api/v1/*` para o backend:

```javascript
async rewrites() {
  const backendBase = process.env.BACKEND_URL || "http://trisla-portal-backend:8001/api/v1";
  return [
    {
      source: "/api/v1/:path*",
      destination: `${backendBase}/:path*`,
    },
  ];
}
```

**Resultado**: Browser sempre chama `http://localhost:3001/api/v1/...` (ou host do Portal) e Next.js faz proxy interno.

#### 2. Config Simplificado (`config.ts`)

**ANTES**: Lógica complexa com fallbacks para localhost/IP  
**AGORA**: Simplesmente `export const API_BASE = "/api/v1"`

**Resultado**: Sem IP hardcoded, sempre same-origin.

#### 3. API Client Refatorado (`api.ts`)

**NOVO**: Funções `apiGet()` e `apiPost()` usando same-origin:

```typescript
export async function apiGet<T>(path: string, timeoutMs = 30000): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { signal: controller.signal });
  // ...
}
```

**Mantido**: Função `api()` genérica para compatibilidade com código existente.

**Resultado**: Todas as chamadas usam `/api/v1` (same-origin).

#### 4. Dockerfile Simplificado

**ANTES**: Build-args para `NEXT_PUBLIC_TRISLA_API_BASE_URL`  
**AGORA**: Apenas `BACKEND_URL` (usado no server-side para rewrites)

**Resultado**: Build mais simples, sem necessidade de build-args para desenvolvimento.

#### 5. Helm Chart Atualizado

- Removido comentário sobre `NEXT_PUBLIC_TRISLA_API_BASE_URL`
- Mantido apenas `BACKEND_URL` para rewrites do Next.js

### 📋 Arquivos Modificados

#### Frontend
- ✅ `next.config.js` - Adicionado `rewrites()` para proxy
- ✅ `src/lib/config.ts` - Simplificado para `API_BASE = "/api/v1"`
- ✅ `src/lib/api.ts` - Refatorado com `apiGet`/`apiPost` usando same-origin
- ✅ `src/app/page.tsx` - Health check usa `/health` (same-origin)
- ✅ `src/app/modules/page.tsx` - Usa `apiClient.getModules()`
- ✅ `src/lib/version.ts` - Versão `3.7.34`
- ✅ `package.json` - Versão `3.7.34`
- ✅ `Dockerfile` - Simplificado, apenas `BACKEND_URL`

#### Helm
- ✅ `Chart.yaml` - Versão `3.7.34`
- ✅ `values.yaml` - Comentários atualizados

### 🔍 Como Funciona

#### Em Kubernetes (Produção)

1. Browser acessa Portal: `http://node006:32001` (via NodePort)
2. Browser faz requisição: `GET http://node006:32001/api/v1/modules`
3. Next.js (server-side) intercepta `/api/v1/*` via rewrites
4. Next.js faz proxy interno: `GET http://trisla-portal-backend:8001/api/v1/modules`
5. Resposta retornada ao browser

**Resultado**: Browser nunca vê IP interno, sempre same-origin.

#### Em Desenvolvimento Local (Túnel SSH)

1. Browser acessa Portal: `http://localhost:3001` (via túnel)
2. Browser faz requisição: `GET http://localhost:3001/api/v1/modules`
3. Next.js (server-side) intercepta `/api/v1/*` via rewrites
4. Next.js faz proxy: `GET http://trisla-portal-backend:8001/api/v1/modules` (ou via túnel se configurado)
5. Resposta retornada ao browser

**Resultado**: Funciona igual, sem hardcode.

### ✅ Garantias

- ✅ **Zero hardcode de IP/NodePort**: Browser sempre usa same-origin
- ✅ **Funciona em Kubernetes**: Next.js faz proxy interno
- ✅ **Funciona em desenvolvimento**: Mesmo padrão, sem configuração adicional
- ✅ **Compatibilidade mantida**: Código existente continua funcionando
- ✅ **Build simplificado**: Não precisa mais de build-args complexos

### 🧪 Testes Realizados

1. ✅ Build local → Sucesso (13 páginas geradas)
2. ✅ Lint e TypeScript → Sem erros
3. ✅ Todas as chamadas API usam `/api/v1` (same-origin)

### 🚀 Build e Push

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/frontend

# Build simples - não precisa mais de build-args
docker build -t ghcr.io/abelisboa/trisla-portal-frontend:v3.7.34 .

docker push ghcr.io/abelisboa/trisla-portal-frontend:v3.7.34
```

**IMPORTANTE**: Não use `--build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=...` nunca mais. O frontend sempre usa same-origin.

### 📝 Notas Técnicas

**Por que same-origin é melhor?**
- Evita problemas de CORS
- Browser não precisa conhecer IPs internos
- Funciona igual em todos os ambientes
- Next.js faz proxy de forma transparente

**Compatibilidade com código existente:**
- Função `api()` genérica mantida
- Métodos `api.getContract()`, `api.getModules()`, etc. mantidos
- Código existente continua funcionando sem mudanças

### ⚠️ Breaking Changes

**Nenhum** - Esta é uma correção que melhora a arquitetura sem quebrar compatibilidade.

