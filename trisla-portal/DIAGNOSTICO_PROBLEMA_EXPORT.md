# 🔍 FASE 1 - Diagnóstico do Problema

## ❌ Erro Identificado

```
Page "/modules/[module]" is missing generateStaticParams() so it cannot be used with output: export
```

## 🔎 Análise do Problema

### Por que o erro ocorre?

1. **Rotas Dinâmicas sem `generateStaticParams()`**:
   - O Portal TriSLA possui rotas dinâmicas:
     - `/modules/[module]/page.tsx`
     - `/contracts/[id]/page.tsx`
   - Essas rotas usam `useParams()` para obter valores dinâmicos em runtime
   - Com `output: 'export'`, o Next.js tenta gerar todas as páginas estaticamente
   - Rotas dinâmicas requerem `generateStaticParams()` para export estático, mas isso não é adequado para dados em tempo real

2. **Consumo de API em Tempo Real**:
   - As páginas fazem chamadas dinâmicas à API:
     - `api.getModule(moduleName)`
     - `api.getContract(contractId)`
   - Essas chamadas dependem de parâmetros de URL que só existem em runtime
   - Export estático não suporta isso sem pré-gerar todas as possibilidades

### Por que o Portal TriSLA não pode usar `output: 'export'`?

1. **Rotas Dinâmicas**: Múltiplas rotas com parâmetros dinâmicos (`[module]`, `[id]`)
2. **API Calls em Runtime**: Dados são buscados dinamicamente baseados em parâmetros de URL
3. **Server Components**: Alguns componentes podem precisar de server-side rendering
4. **Sem `generateStaticParams()`**: As rotas não têm todas as possibilidades pré-definidas

### Por que o modo correto é `standalone` para produção Docker?

1. **Suporte a Rotas Dinâmicas**: Permite renderização server-side quando necessário
2. **API Routes**: Mantém capacidade de ter API routes se necessário no futuro
3. **Otimização**: Next.js standalone inclui apenas dependências necessárias
4. **Compatibilidade NASP**: Funciona perfeitamente com Kubernetes e NodePort
5. **Performance**: Mantém otimizações do Next.js (SSR, ISR quando aplicável)

### Arquivos que Precisam ser Corrigidos

1. **`frontend/next.config.js`**:
   - ❌ Atual: `output: 'export'`
   - ✅ Correto: `output: 'standalone'`

2. **`frontend/Dockerfile`**:
   - ❌ Atual: Copia `/app/out` (export estático)
   - ✅ Correto: Copia `.next/standalone` e executa `node standalone/server.js`

3. **`helm/trisla-portal/templates/frontend-deployment.yaml`**:
   - ❌ Atual: `containerPort: 80`
   - ✅ Correto: `containerPort: 3000` (porta padrão do Next.js standalone)

4. **`helm/trisla-portal/templates/frontend-service.yaml`**:
   - ❌ Atual: `targetPort: 80`
   - ✅ Correto: `targetPort: 3000`

5. **`scripts/build_frontend.sh`**:
   - ✅ Já está correto (caminho relativo)

### Impactos no Dockerfile, Helm e Scripts

#### Dockerfile
- **Impacto**: Mudança completa de estratégia
  - De: nginx servindo arquivos estáticos
  - Para: Node.js servindo aplicação standalone
  - Porta: 80 → 3000

#### Helm Chart
- **Impacto**: Ajuste de portas e health checks
  - `containerPort`: 80 → 3000
  - `targetPort`: 80 → 3000
  - Health checks: Ajustar para porta 3000

#### Scripts
- **Impacto**: Mínimo (apenas validação de caminhos)
  - Build script: Já está correto
  - Push script: Sem alterações

---

## ✅ Solução Proposta

1. Alterar `next.config.js` para `output: 'standalone'`
2. Recriar `Dockerfile` para modo standalone
3. Ajustar Helm Chart para porta 3000
4. Validar todos os caminhos e configurações

---

**Diagnóstico concluído em**: 2025-12-10

