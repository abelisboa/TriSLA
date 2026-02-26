# Changelog v3.7.35

## Garantia Definitiva - Zero IP Hardcoded

### 🎯 Objetivo

Garantir que **NUNCA MAIS** exista qualquer chamada para `http://192.168.10.16:32002/api/v1/*` no frontend. Todas as chamadas usam **EXCLUSIVAMENTE** `/api/v1/*` (same-origin).

### ✅ Verificações Realizadas

#### 1. Teste de Regressão

```bash
grep -r "192.168" src  # Resultado: Nenhuma ocorrência
grep -r "32002" src    # Resultado: Nenhuma ocorrência
```

**Confirmado**: Zero referências a IPs hardcoded ou NodePort no código fonte.

#### 2. Configuração Central

**Arquivo**: `src/lib/config.ts`

```typescript
export const API_BASE = "/api/v1";
```

**Status**: ✅ Correto - apenas same-origin, sem IPs.

#### 3. Cliente de API Padronizado

**Arquivo**: `src/lib/api.ts`

- Função `apiFetch()` usando `API_BASE` (same-origin)
- Função `api()` mantida para compatibilidade
- Métodos `apiClient.getModules()`, `apiClient.getHealthGlobal()`, etc. usando `apiFetch`

**Status**: ✅ Todas as chamadas usam `/api/v1/*`.

#### 4. Arquivos Verificados

Todos os arquivos que fazem chamadas de API foram verificados:

- ✅ `src/app/page.tsx` - Usa `apiFetch("/health")`
- ✅ `src/app/modules/page.tsx` - Usa `apiFetch("/modules")`
- ✅ `src/app/modules/[module]/page.tsx` - Usa `apiFetch("/modules/...")`
- ✅ `src/app/slas/metrics/page.tsx` - Usa `apiFetch("/sla/...")`
- ✅ `src/app/slas/monitoring/page.tsx` - Usa `apiFetch("/health/global")`
- ✅ `src/app/slas/create/pln/page.tsx` - Usa `apiFetch("/sla/submit", ...)`
- ✅ `src/app/slas/create/template/page.tsx` - Usa `apiFetch("/sla/submit", ...)`
- ✅ `src/app/slas/result/page.tsx` - Usa `apiFetch("/sla/status/...")`
- ✅ `src/app/slas/create/page.tsx` - Usa `apiFetch("/sla/...")`
- ✅ `src/store/useStore.ts` - Usa `apiClient.getHealthGlobal()` e `apiClient.getModules()`

**Status**: ✅ Todos usando same-origin `/api/v1/*`.

### 📋 Arquivos Modificados

#### Frontend
- ✅ `src/lib/version.ts` - Versão `3.7.35`
- ✅ `package.json` - Versão `3.7.35`
- ✅ `src/store/useStore.ts` - Corrigido para usar `apiClient` em vez de `api`

#### Helm
- ✅ `Chart.yaml` - Versão `3.7.35`
- ✅ `values.yaml` - Tag `v3.7.35`

### 🔍 Referências a `localhost` (Permitidas)

As únicas referências a `localhost` encontradas são:

1. **Links para Grafana** (`localhost:3001`):
   - `src/app/modules/page.tsx` - Link externo para Grafana
   - `src/app/slas/monitoring/page.tsx` - Link externo para Grafana
   
   **Status**: ✅ Permitido - são links externos, não chamadas de API.

2. **Mensagens informativas**:
   - `src/app/slas/create/pln/page.tsx` - Mensagem sobre port-forward em `localhost:8080`
   - `src/app/slas/metrics/page.tsx` - Mensagem sobre port-forward em `localhost:8084`
   
   **Status**: ✅ Permitido - são apenas mensagens de texto para o usuário.

### ✅ Garantias

- ✅ **Zero hardcode de IP/NodePort**: Nenhuma chamada de API usa IP ou porta hardcoded
- ✅ **Todas as chamadas usam same-origin**: `/api/v1/*` exclusivamente
- ✅ **Next.js faz proxy**: Rewrites em `next.config.js` fazem proxy interno
- ✅ **Funciona em Kubernetes**: Next.js resolve backend via Service Kubernetes
- ✅ **Funciona em desenvolvimento**: Mesmo padrão, sem configuração adicional
- ✅ **Build testado**: Sucesso (13 páginas geradas)

### 🧪 Testes Realizados

1. ✅ **Build local**: Sucesso sem erros
2. ✅ **Lint e TypeScript**: Sem erros
3. ✅ **Teste de regressão**: Nenhuma ocorrência de `192.168` ou `32002`
4. ✅ **Verificação de arquivos**: Todos usando `apiFetch` ou `apiClient`

### 🚀 Build e Push

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/frontend

docker build -t ghcr.io/abelisboa/trisla-portal-frontend:v3.7.35 .

docker push ghcr.io/abelisboa/trisla-portal-frontend:v3.7.35
```

**IMPORTANTE**: Não use `--build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=...` nunca mais. O frontend sempre usa same-origin.

### 📝 Notas Técnicas

**Por que esta versão?**
- v3.7.34 já tinha a correção de same-origin implementada
- v3.7.35 adiciona verificação definitiva e correção do `useStore.ts`
- Garantia adicional de que não há IPs hardcoded em nenhum lugar

**Compatibilidade:**
- Mantém compatibilidade com código existente
- Função `api()` e métodos `apiClient.*` funcionam igual
- Nenhuma breaking change

### ⚠️ Breaking Changes

**Nenhum** - Esta é uma garantia adicional de que não há IPs hardcoded.
