# Instruções FASE 3, 4 e 5 - Portal TriSLA v3.7.31

## ✅ FASE 3.1 - Versionamento COMPLETO

### Arquivos Atualizados:
- ✅ `frontend/package.json`: `"version": "3.7.31"`
- ✅ `helm/trisla-portal/Chart.yaml`: `version: 3.7.31` / `appVersion: "3.7.31"`
- ✅ `helm/trisla-portal/values.yaml`: `tag: v3.7.31`
- ✅ `frontend/src/lib/version.ts`: Criado com versão centralizada
- ✅ Versão exibida no portal (página inicial e admin)

## 🔄 FASE 3.2 - Testes Locais (OBRIGATÓRIO)

### Pré-requisitos:
```bash
cd trisla-portal/frontend
npm install
```

### Executar Portal Localmente:
```bash
npm run dev
```

### Checklist de Testes:

#### A) Criação de SLA via PLN (`/slas/create/pln`)
- [ ] Acessar `/slas/create/pln`
- [ ] Verificar texto explicativo: "PLN → Ontologia → Template GST"
- [ ] Preencher intent em linguagem natural
- [ ] Clicar em "Interpretar (PLN → Ontologia → Template GST)"
- [ ] Verificar template GST exibido antes da submissão
- [ ] Clicar em "Submeter SLA ao NASP"
- [ ] Verificar redirecionamento para `/slas/result`
- [ ] Verificar exibição de SLA ID, Timestamp, Status

#### B) Criação de SLA via Template (`/slas/create/template`)
- [ ] Acessar `/slas/create/template`
- [ ] Verificar texto explicativo sobre atributos GST
- [ ] Selecionar template (URLLC, eMBB ou mMTC)
- [ ] Verificar campos marcados com [GST]
- [ ] Preencher atributos GST (Latência, Confiabilidade, etc.)
- [ ] Clicar em "Criar SLA"
- [ ] Verificar redirecionamento para `/slas/result`
- [ ] Verificar exibição de Status: ACCEPT / RENEG / REJECT

#### C) Tela de Resultado (`/slas/result`)
- [ ] Verificar exibição de SLA ID
- [ ] Verificar exibição de Timestamp
- [ ] Verificar exibição de Status com ícone correto:
  - ACCEPT → Ícone verde (CheckCircle)
  - RENEG → Ícone amarelo (Clock)
  - REJECT → Ícone vermelho (XCircle)
- [ ] Verificar mensagem do backend
- [ ] Verificar indicação sobre Smart Contract para ACCEPT
- [ ] Verificar links funcionais (Métricas, Status Detalhado)

#### D) Monitoramento (`/slas/monitoring`)
- [ ] Acessar `/slas/monitoring`
- [ ] Verificar número de SLAs ativos
- [ ] Verificar status geral do sistema
- [ ] Verificar link para Grafana funcional
- [ ] Verificar botão de atualização
- [ ] Verificar nota sobre não duplicar Grafana

#### E) Área Admin (`/modules`)
- [ ] Acessar `/modules`
- [ ] Verificar seção "Integrações Ativas"
- [ ] Verificar seção "Estado dos Módulos"
- [ ] Verificar seção "Versões e Links Técnicos"
- [ ] Verificar versão exibida: "Portal TriSLA — v3.7.31"
- [ ] Verificar links técnicos (API Docs, Health Check, Grafana)

#### F) Página Inicial (`/`)
- [ ] Verificar versão exibida no rodapé: "Portal TriSLA — v3.7.31"
- [ ] Verificar links funcionais

### Validações Obrigatórias:
- ✅ Nenhum erro de console no navegador
- ✅ Nenhuma alteração de endpoint (verificar Network tab)
- ✅ Todos os redirecionamentos funcionando
- ✅ Versão v3.7.31 visível no portal

## 📝 FASE 4 - Commit, Tag e Push (VERSIONADO)

### 4.1 Verificação Pré-Commit

```bash
cd trisla-portal
git status
```

**Confirmar:**
- ✅ Somente arquivos esperados (frontend, helm, documentação)
- ✅ Nenhum secret (verificar .env.production não commitado)
- ✅ Nenhum build artifact indevido (.next/, node_modules/)

### 4.2 Adicionar Arquivos

```bash
# Adicionar apenas arquivos do portal (frontend e helm)
git add frontend/package.json
git add frontend/src/lib/version.ts
git add frontend/src/app/slas/create/pln/page.tsx
git add frontend/src/app/slas/create/template/page.tsx
git add frontend/src/app/slas/result/
git add frontend/src/app/slas/monitoring/
git add frontend/src/app/modules/page.tsx
git add frontend/src/app/page.tsx
git add frontend/src/components/layout/Sidebar.tsx
git add helm/trisla-portal/Chart.yaml
git add helm/trisla-portal/values.yaml
git add RELATORIO_CONSOLIDACAO_FASE2.md
git add VERSIONAMENTO_v3.7.31.md
git add CHANGELOG_v3.7.31.md
git add INSTRUCOES_FASE3_4_5.md
```

### 4.3 Commit Semântico (OBRIGATÓRIO)

```bash
git commit -m "feat(portal): consolidate GST-based SLA flow and monitoring (v3.7.31)

- FASE 2: Melhorias de clareza conceitual
  - Página PLN com fluxo em duas etapas (interpretar → submeter)
  - Página Template com atributos GST explicitamente marcados
  - Nova página de resultado após submissão
  - Nova página de monitoramento simples
  - Área Admin reorganizada

- Versionamento: v4.0.0 → v3.7.31
  - package.json: 3.7.31
  - Helm Chart: 3.7.31 / appVersion: 3.7.31
  - Helm Values: v3.7.31
  - Versão visível no portal (página inicial e admin)

- Conformidade:
  - Nenhuma alteração de endpoints
  - Nenhuma refatoração de backend
  - Gate lógico mantido (ACCEPT/RENEG/REJECT)"
```

### 4.4 Tag da Versão (RECOMENDADO)

```bash
git tag v3.7.31
git tag -a v3.7.31 -m "Portal TriSLA v3.7.31 - Consolidação FASE 2"
```

### 4.5 Push

```bash
# Push da tag primeiro
git push origin v3.7.31

# Push do commit
git push origin main
```

## 🏗️ FASE 5 - Build Local e Deploy no NASP (VERSIONADO)

### 5.1 Build Local (OBRIGATÓRIO)

```bash
cd trisla-portal/frontend
npm run build
```

**Verificar:**
- ✅ Build sem erros
- ✅ Arquivos gerados em `.next/`

### 5.2 Build da Imagem Docker (TAG VERSIONADA)

```bash
cd trisla-portal/frontend

# Build com tag versionada
docker build -t ghcr.io/abelisboa/trisla-portal:v3.7.31 .

# ❌ NUNCA usar latest
# ✅ SEMPRE usar tag versionada
```

### 5.3 Push da Imagem Docker

```bash
# Login no GHCR (se necessário)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push da imagem
docker push ghcr.io/abelisboa/trisla-portal:v3.7.31
```

### 5.4 Deploy no NASP

```bash
# SSH no node006
ssh node006

# Navegar para diretório do portal
cd /home/porvir5g/gtp5g/trisla

# Atualizar valores do Helm (se necessário)
# Editar helm/trisla-portal/values.yaml para usar tag v3.7.31

# Deploy via Helm
helm upgrade trisla-portal ./helm/trisla-portal \
  --namespace trisla \
  --set frontend.image.tag=v3.7.31

# Verificar pods
kubectl get pods -n trisla | grep trisla-portal

# Validar portal acessível
# Verificar NodePort 32001 (frontend)
```

## ⚠️ REGRAS INVIOLÁVEIS

1. ❌ **NUNCA usar `latest` como tag**
2. ❌ **NUNCA sobrescrever versão anterior**
3. ✅ **SEMPRE incrementar PATCH antes de build/commit/deploy**
4. ✅ **SEMPRE usar tag versionada em Docker**
5. ✅ **SEMPRE incluir versão no commit message**

## 📋 Checklist Final

- [ ] FASE 3.1: Versionamento completo
- [ ] FASE 3.2: Testes locais executados
- [ ] FASE 4.1: Verificação pré-commit
- [ ] FASE 4.2: Arquivos adicionados
- [ ] FASE 4.3: Commit semântico
- [ ] FASE 4.4: Tag criada
- [ ] FASE 4.5: Push realizado
- [ ] FASE 5.1: Build local
- [ ] FASE 5.2: Build Docker com tag v3.7.31
- [ ] FASE 5.3: Push da imagem
- [ ] FASE 5.4: Deploy no NASP
- [ ] Validação: Portal acessível
- [ ] Validação: Versão v3.7.31 exibida
- [ ] Validação: Criação de SLA funcionando

