# Changelog v3.7.32

## Correções Cirúrgicas

### Remoção de Hardcode NodePort/IP
- **Removido**: Hardcode de `192.168.10.16:32002` no Dockerfile
- **Removido**: Referências diretas a NodePort `:32002` no código
- **Implementado**: Configuração centralizada via `NEXT_PUBLIC_TRISLA_API_BASE_URL`
- **Fallback**: `http://localhost:8001/api/v1` (compatível com túnel SSH)

### Correção de React Error #418
- **Corrigido**: Hooks instáveis em todas as páginas que fazem polling
- **Implementado**: `useCallback` para funções usadas em `useEffect`
- **Implementado**: `useRef` para rastrear estado de montagem e evitar setState após unmount
- **Corrigido**: Cleanup adequado de timers e intervalos
- **Páginas corrigidas**:
  - `/slas/metrics` - Auto-refresh com cleanup adequado
  - `/slas/monitoring` - Polling a cada 30s com proteção contra unmount
  - `/modules` - Fetch de módulos com função estável
  - `/modules/[module]` - Fetch de dados do módulo com proteção
  - `/` (home) - Health check com timeout

### Cliente HTTP Robusto
- **Implementado**: Timeout de 25 segundos em todas as requisições
- **Implementado**: Tratamento de erro com mensagens claras
- **Implementado**: AbortController para cancelamento de requisições
- **Melhorado**: Mensagens de erro específicas para timeout e falha de conexão

### Resiliência a Backend Indisponível
- **Implementado**: Timeout de 5 segundos para health check
- **Implementado**: Fallback de UI que não trava nem crasha
- **Melhorado**: Mensagens de erro informativas sobre túnel SSH

## Versionamento
- **Frontend**: `package.json` → `3.7.32`
- **Helm Chart**: `Chart.yaml` → `version: 3.7.32`, `appVersion: "3.7.32"`
- **Helm Values**: `values.yaml` → `frontend.tag: v3.7.32`
- **Código**: `src/lib/version.ts` → `PORTAL_VERSION = '3.7.32'`

## Compatibilidade
- ✅ Mantém 100% do fluxo atual (PLN → Template → Submit → Result)
- ✅ Mantém todas as páginas criadas na FASE 2
- ✅ Compatível com túnel SSH (localhost:8001)
- ✅ Compatível com NodePort via variável de ambiente

## Notas Técnicas
- Backend não foi alterado (mantém tag v3.7.11)
- Frontend requer rebuild completo devido a mudanças em hooks
- Variável de ambiente: `NEXT_PUBLIC_TRISLA_API_BASE_URL` (substitui `NEXT_PUBLIC_API_URL`)

