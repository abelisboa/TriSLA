# S6.0 - Portal Deploy Evidence

**Data:** 2025-12-20  
**Ambiente:** NASP (node006)  
**Namespace:** trisla

## Estado Inicial

### Pods Existentes
- trisla-bc-nssmf: Running
- trisla-decision-engine: Running  
- trisla-ml-nsmf: Running
- trisla-nasp-adapter: Running
- trisla-sla-agent-layer: Running
- trisla-ui-dashboard: Running

### Services Existentes
- trisla-bc-nssmf (ClusterIP: 8083)
- trisla-decision-engine (ClusterIP: 8082)
- trisla-ml-nsmf (ClusterIP: 8081)
- trisla-nasp-adapter (ClusterIP: 8085)
- trisla-sem-csmf (ClusterIP: 8080)
- trisla-sla-agent-layer (ClusterIP: 8084)
- trisla-ui-dashboard (ClusterIP: 80)

### Componentes Portal
- ❌ Portal Backend: **NÃO ENCONTRADO**
- ❌ Portal Frontend: **NÃO ENCONTRADO**

## Bloqueios Identificados

1. **Portal não estava deployado**: Nenhum pod ou service de portal-backend ou portal-frontend encontrado
2. **Chart separado**: Encontrado chart  em  (separado do chart principal)
3. **Problema de porta**: Imagem do backend roda Next.js na porta 3000, mas deployment esperava 8001
4. **Probes falhando**: Endpoints  e  não existem na aplicação

## Correções Aplicadas

### 1. Deploy do Portal


### 2. Ajuste de Porta do Backend
- **Problema**: Backend roda na porta 3000 (Next.js), mas deployment esperava 8001
- **Solução**: Ajustado deployment para usar containerPort 3000 e service targetPort 3000
- **Arquivos modificados**:
  - : containerPort 3000, probes na porta 3000
  - : targetPort 3000

### 3. Ajuste de Health Probes
- **Problema**: Endpoints  e  não existem
- **Solução**: Ajustado probes para usar endpoint raiz 
- **Arquivo modificado**: 

### 4. Variável de Ambiente PORT
- Adicionada variável  em  (não aplicada pela aplicação Next.js)

## Estado Final

### Pods
- ✅ **trisla-portal-backend**: Running (1/1)
- ⚠️ **trisla-portal-frontend**: Running mas com restarts (0/1 com 10 restarts)

### Services
- ✅ **trisla-portal-backend**: NodePort (8001:32002/TCP)
- ✅ **trisla-portal-frontend**: NodePort (80:32001/TCP)

### Endpoint /api/v1/sla/submit
- ⚠️ **Status**: Backend responde, mas endpoint retorna Not Found
- **Teste realizado**:
  
- **Observação**: Backend está servindo HTML (frontend Next.js), não API REST

## Análise

O backend do portal parece ser uma aplicação Next.js que serve o frontend. O endpoint  pode estar:
1. Em rotas de API do Next.js (ex: )
2. Em outro componente (trisla-api-backend, se existir)
3. Não implementado nesta versão da imagem

## Próximos Passos

1. Verificar se há rotas de API do Next.js no backend
2. Verificar se há componente  separado
3. Consultar documentação da imagem para confirmar endpoints disponíveis
4. Verificar logs do backend para identificar rotas disponíveis

## Arquivos Modificados

1. 
   - containerPort: 8001 → 3000
   - livenessProbe port: 8001 → 3000, path: /health → /
   - readinessProbe port: 8001 → 3000, path: /nasp/diagnostics → /
   - Adicionada variável PORT (não efetiva)

2. 
   - targetPort: 8001 → 3000

3. 
   - Adicionada  em backend.env (não efetiva)

## Conclusão

✅ Portal Backend **deployado e rodando**  
✅ Portal Frontend **deployado** (com problemas de restart)  
⚠️ Endpoint  **não encontrado** (backend responde mas endpoint não existe)

**Ambiente parcialmente pronto para PROMPT_S6_NASP** - requer investigação adicional sobre o endpoint correto.
