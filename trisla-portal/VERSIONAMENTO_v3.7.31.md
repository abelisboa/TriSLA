# Versionamento v3.7.31 - Portal TriSLA

## Data: $(date)

## Versão Anterior
- Frontend: v4.0.0
- Helm Chart: 1.0.9 / appVersion: 1.0.0
- Helm Values: v3.7.11

## Versão Atual
- **Frontend: v3.7.31**
- **Helm Chart: 3.7.31 / appVersion: 3.7.31**
- **Helm Values: v3.7.31**

## Arquivos Atualizados

### 1. package.json
```json
"version": "3.7.31"
```

### 2. helm/trisla-portal/Chart.yaml
```yaml
version: 3.7.31
appVersion: "3.7.31"
```

### 3. helm/trisla-portal/values.yaml
```yaml
frontend:
  image:
    tag: v3.7.31
```

### 4. src/lib/version.ts (NOVO)
```typescript
export const PORTAL_VERSION = '3.7.31'
export const PORTAL_VERSION_DISPLAY = `Portal TriSLA — v${PORTAL_VERSION}`
```

### 5. Exibição no Portal
- Página inicial (`/`): Versão exibida no rodapé
- Área Admin (`/modules`): Versão exibida em "Versões e Links Técnicos"

## Mudanças Implementadas

### FASE 2 - Melhorias de Clareza Conceitual
- ✅ Página PLN com fluxo em duas etapas (interpretar → submeter)
- ✅ Página Template com atributos GST explicitamente marcados
- ✅ Página de resultado após submissão (`/slas/result`)
- ✅ Página de monitoramento (`/slas/monitoring`)
- ✅ Área Admin reorganizada

## Próximos Passos

### FASE 3.2 - Testes Locais
- [ ] Testar criação de SLA via PLN
- [ ] Testar criação de SLA via Template
- [ ] Validar tela de resultado
- [ ] Validar monitoramento
- [ ] Validar área Admin

### FASE 4 - Commit e Push
- [ ] `git status` - verificar arquivos
- [ ] `git commit -am "feat(portal): consolidate GST-based SLA flow and monitoring (v3.7.31)"`
- [ ] `git tag v3.7.31`
- [ ] `git push origin v3.7.31`
- [ ] `git push origin main`

### FASE 5 - Build e Deploy
- [ ] `npm run build`
- [ ] `docker build -t ghcr.io/abelisboa/trisla-portal:v3.7.31 .`
- [ ] `docker push ghcr.io/abelisboa/trisla-portal:v3.7.31`
- [ ] Deploy no NASP via node006

## Observações

- ❌ Nunca usar `latest` como tag
- ❌ Nunca sobrescrever versão anterior
- ✅ Sempre incrementar PATCH antes de build/commit/deploy
- ✅ Versão visível no portal (página inicial e admin)

