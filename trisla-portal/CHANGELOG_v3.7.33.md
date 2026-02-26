# Changelog v3.7.33

## Correção de Regressão - Estabilização Kubernetes

### 🐛 Problema Identificado

A versão v3.7.32 introduziu uma regressão crítica onde o frontend usava `localhost:8001` como fallback padrão para comunicação com o backend. Isso causava falhas em ambiente Kubernetes, onde:

- O frontend não conseguia se comunicar com o backend via Service Kubernetes
- Chamadas de API retornavam `ERR_EMPTY_RESPONSE` ou timeouts
- O portal não carregava corretamente em produção

### ✅ Correção Implementada

#### 1. Nova Configuração Kubernetes-Safe (`runtimeConfig.ts`)

Criado arquivo `src/lib/runtimeConfig.ts` que:

- **Default Kubernetes-safe**: `http://trisla-portal-backend:8001/api/v1` (Service Kubernetes)
- **Prioridade**: `NEXT_PUBLIC_TRISLA_API_BASE_URL` (se definido) > Service Kubernetes
- **Sem fallback para localhost**: Elimina regressão em ambiente Kubernetes

#### 2. Atualização do Dockerfile

- **Default alterado**: De `localhost:8001` para `http://trisla-portal-backend:8001/api/v1`
- **Override permitido**: Para desenvolvimento local via túnel SSH, pode passar `--build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1`
- **Kubernetes-first**: Build padrão funciona em Kubernetes sem configuração adicional

#### 3. Refatoração de Imports

- `api.ts` agora importa de `runtimeConfig.ts` diretamente
- `config.ts` mantido para compatibilidade (deprecated, redireciona para `runtimeConfig.ts`)
- `page.tsx` atualizado para usar `runtimeConfig.ts`

#### 4. Helm Chart Atualizado

- `values.yaml`: Removido hardcode de `localhost` em `NEXT_PUBLIC_TRISLA_API_BASE_URL`
- Comentário adicionado explicando que o default é Kubernetes-safe
- Versão atualizada para `v3.7.33`

### 📋 Arquivos Modificados

#### Frontend
- ✅ `src/lib/runtimeConfig.ts` - **NOVO**: Configuração Kubernetes-safe
- ✅ `src/lib/config.ts` - Atualizado para usar `runtimeConfig.ts`
- ✅ `src/lib/api.ts` - Import atualizado para `runtimeConfig.ts`
- ✅ `src/app/page.tsx` - Import atualizado
- ✅ `src/lib/version.ts` - Versão atualizada para `3.7.33`
- ✅ `package.json` - Versão atualizada para `3.7.33`
- ✅ `Dockerfile` - Default alterado para Service Kubernetes

#### Helm
- ✅ `helm/trisla-portal/Chart.yaml` - Versão `3.7.33`
- ✅ `helm/trisla-portal/values.yaml` - Removido hardcode de localhost

### 🔍 Garantias de Compatibilidade

#### ✅ Kubernetes (Produção)
- Frontend se comunica com backend via Service `trisla-portal-backend:8001`
- Sem necessidade de variáveis de ambiente adicionais
- Funciona out-of-the-box após deploy

#### ✅ Desenvolvimento Local (Túnel SSH)
- Pode passar `--build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1` no build
- Ou definir via `.env.local` em desenvolvimento
- Mantém compatibilidade com fluxo de desenvolvimento existente

#### ✅ Compatibilidade com v3.7.31
- Todas as funcionalidades da v3.7.31 mantidas
- Correções de hooks (v3.7.32) preservadas
- Nenhuma regressão adicional introduzida

### 🧪 Testes Realizados

1. ✅ Build local sem variáveis de ambiente → Usa Service Kubernetes (default)
2. ✅ Build local com `NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1` → Funciona para túnel SSH
3. ✅ Lint e TypeScript → Sem erros
4. ✅ Build Next.js → Sucesso (13 páginas geradas)

### 📝 Notas Técnicas

**Motivo da Regressão (v3.7.32)**:
- Fallback para `localhost:8001` foi adicionado para facilitar desenvolvimento local
- Porém, isso quebrou o comportamento padrão em Kubernetes
- A correção prioriza Kubernetes (produção) sobre desenvolvimento local

**Solução Escolhida**:
- Default Kubernetes-safe garante funcionamento em produção
- Desenvolvimento local requer configuração explícita (mais seguro)
- Separação clara entre ambientes

### 🚀 Próximos Passos

1. Build da imagem com tag `v3.7.33`
2. Push para `ghcr.io/abelisboa/trisla-portal-frontend:v3.7.33`
3. Deploy no NASP via Helm (sem necessidade de variáveis de ambiente adicionais)
4. Verificação: Portal carrega, chamadas `/health`, `/modules`, `/sla` funcionam

### ⚠️ Breaking Changes

**Nenhum** - Esta é uma correção de regressão que restaura o comportamento esperado.

### 🔄 Rollback

Se necessário, pode fazer rollback para `v3.7.31` (versão estável anterior a v3.7.32).

