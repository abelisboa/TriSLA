# 🚀 Portal TriSLA - Implantação Completa no NASP

## ✅ Status: Implementação Completa

Todos os arquivos foram gerados conforme especificado. O Portal TriSLA está pronto para ser buildado, publicado e implantado no cluster NASP.

---

## 📁 Arquivos Gerados

### FASE 1: Dockerfiles

#### Backend
- **`backend/Dockerfile`**
  - Base: Python 3.10-slim
  - Uvicorn exposto em 0.0.0.0:8001
  - OTLP desabilitado (OTEL_SDK_DISABLED=true)
  - Variáveis de ambiente NASP configuradas

#### Frontend
- **`frontend/Dockerfile`**
  - Base: Node 20 (build) + nginx:alpine (runtime)
  - Build com `npm install && npm run build`
  - Servir estático com nginx
  - Suporte a env.js para configuração em runtime
- **`frontend/next.config.js`** (atualizado)
  - Habilitado output: 'standalone' para Docker

### FASE 2: Helm Chart

#### Estrutura do Chart
```
helm/trisla-portal/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

#### Configurações Principais
- **Frontend NodePort**: 32001
- **Backend NodePort**: 32002
- **Health Checks**:
  - Backend liveness: `/health`
  - Backend readiness: `/nasp/diagnostics`
  - Frontend: `/`

### FASE 3: Scripts de Build e Push

- **`scripts/build_backend.sh`** - Build da imagem Docker do backend
- **`scripts/build_frontend.sh`** - Build da imagem Docker do frontend
- **`scripts/push_backend.sh`** - Push para ghcr.io/abelisboa/trisla-portal-backend
- **`scripts/push_frontend.sh`** - Push para ghcr.io/abelisboa/trisla-portal-frontend

### FASE 4: Script de Deploy

- **`scripts/deploy_portal_nasp.sh`** - Deploy no cluster NASP usando Helm

### FASE 5: Script de Túnel SSH

- **`scripts/create_tunnel.sh`** - Cria túnel SSH para acesso local

### FASE 6: Script de Verificação

- **`scripts/verify_portal.sh`** - Verificação pós-instalação completa

### FASE 7: Configuração Backend

- **`backend/src/config.py`** (atualizado)
  - Suporte para variáveis de ambiente conforme especificação:
    - `SEM_CSMF_URL`, `ML_NSMF_URL`, `DECISION_ENGINE_URL`, `BC_NSSMF_URL`, `SLA_AGENT_URL`
  - Compatibilidade com formato legado (`NASP_*`)

---

## 🛠️ Comandos para Build

### 1. Build das Imagens Docker

```bash
# Build do backend
cd trisla-portal
./scripts/build_backend.sh

# Build do frontend
./scripts/build_frontend.sh
```

### 2. Push para GitHub Container Registry

**Pré-requisito**: Fazer login no ghcr.io

```bash
# Login no GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u abelisboa --password-stdin

# Push do backend
./scripts/push_backend.sh

# Push do frontend
./scripts/push_frontend.sh
```

---

## 🚀 Comandos de Deploy

### Deploy no Cluster NASP

```bash
cd trisla-portal
./scripts/deploy_portal_nasp.sh
```

Este script:
- Cria o namespace `trisla` (se não existir)
- Instala/atualiza o Helm chart `trisla-portal`
- Aguarda os pods ficarem prontos (`--wait`)

### Verificar Status do Deploy

```bash
# Ver pods do backend
kubectl get pods -n trisla -l app=trisla-portal-backend

# Ver pods do frontend
kubectl get pods -n trisla -l app=trisla-portal-frontend

# Ver serviços NodePort
kubectl get svc -n trisla | grep trisla-portal
```

---

## 🔗 Comandos de Túnel SSH

### Criar Túnel SSH

```bash
cd trisla-portal
./scripts/create_tunnel.sh
```

Ou manualmente:

```bash
ssh -L 32001:localhost:32001 \
    -L 32002:localhost:32002 \
    porvir5g@node1
```

**Nota**: Mantenha este terminal aberto enquanto usar o túnel.

---

## ✅ Verificação Pós-Instalação

### Executar Verificação Completa

```bash
cd trisla-portal
./scripts/verify_portal.sh
```

Este script testa:
1. ✅ Backend Health Check (`/health`)
2. ✅ Frontend (`/`)
3. ✅ Backend NASP Diagnostics (`/nasp/diagnostics`)
4. ✅ Acesso aos módulos NASP (com timeout de 1s)
5. ✅ Fluxo completo (`POST /api/v1/sla/submit`)

---

## 🌐 URLs de Acesso

Após criar o túnel SSH, acesse:

- **Frontend**: http://localhost:32001
- **Backend**: http://localhost:32002

### Endpoints Principais

- **Backend Health**: http://localhost:32002/health
- **NASP Diagnostics**: http://localhost:32002/nasp/diagnostics
- **SLA Submit**: http://localhost:32002/api/v1/sla/submit

---

## 📋 Configurações do Helm Chart

### Valores Padrão (values.yaml)

```yaml
frontend:
  nodePort: 32001
  image:
    repository: ghcr.io/abelisboa/trisla-portal-frontend
    tag: latest

backend:
  nodePort: 32002
  image:
    repository: ghcr.io/abelisboa/trisla-portal-backend
    tag: latest
  env:
    SEM_CSMF_URL: "http://trisla-sem-csmf:8080"
    ML_NSMF_URL: "http://trisla-ml-nsmf:8081"
    DECISION_ENGINE_URL: "http://trisla-decision-engine:8082"
    BC_NSSMF_URL: "http://trisla-bc-nssmf:8083"
    SLA_AGENT_URL: "http://trisla-sla-agent-layer:8084"
```

### Personalizar Valores

Crie um arquivo `custom-values.yaml` e use:

```bash
helm upgrade --install trisla-portal ./helm/trisla-portal \
  -n trisla \
  --create-namespace \
  --wait \
  -f custom-values.yaml
```

---

## 🔧 Troubleshooting

### Backend não inicia

```bash
# Ver logs do backend
kubectl logs -n trisla -l app=trisla-portal-backend --tail=50

# Verificar eventos
kubectl describe pod -n trisla -l app=trisla-portal-backend
```

### Frontend não acessível

```bash
# Ver logs do frontend
kubectl logs -n trisla -l app=trisla-portal-frontend --tail=50

# Verificar se o serviço NodePort está correto
kubectl get svc -n trisla trisla-portal-frontend
```

### Módulos NASP não acessíveis

Verifique se os serviços NASP estão rodando:

```bash
# Verificar serviços NASP
kubectl get svc -n trisla | grep -E "sem-csmf|ml-nsmf|decision|bc-nssmf|sla-agent"
```

### Túnel SSH não funciona

1. Verifique se você tem acesso ao `node1`
2. Verifique se as portas 32001 e 32002 não estão em uso localmente
3. Teste a conexão SSH: `ssh porvir5g@node1`

---

## 📝 Notas Importantes

1. **Variáveis de Ambiente**: O backend suporta ambos os formatos:
   - Formato especificado: `SEM_CSMF_URL`, `ML_NSMF_URL`, etc.
   - Formato legado: `NASP_SEM_CSMF_URL`, `NASP_ML_NSMF_URL`, etc.
   - Prioridade: formato especificado > formato legado

2. **Health Checks**: 
   - Liveness: `/health` (verifica se o backend está vivo)
   - Readiness: `/nasp/diagnostics` (verifica conectividade com NASP)

3. **OTLP Desabilitado**: Por padrão, telemetria OTLP está desabilitada (`OTEL_SDK_DISABLED=true`)

4. **Segurança**: Os scripts não executam comandos destrutivos automaticamente. Sempre verifique antes de executar.

---

## ✅ Checklist Final

- [x] Dockerfiles criados (backend e frontend)
- [x] Helm Chart completo gerado
- [x] Scripts de build e push criados
- [x] Script de deploy criado
- [x] Script de túnel SSH criado
- [x] Script de verificação criado
- [x] Configuração backend atualizada para suportar variáveis especificadas
- [x] Next.js config atualizado para standalone output

---

## 🎯 Próximos Passos

1. **Build das imagens**: Execute `./scripts/build_backend.sh` e `./scripts/build_frontend.sh`
2. **Push para registry**: Execute `./scripts/push_backend.sh` e `./scripts/push_frontend.sh`
3. **Deploy no NASP**: Execute `./scripts/deploy_portal_nasp.sh`
4. **Criar túnel SSH**: Execute `./scripts/create_tunnel.sh`
5. **Verificar instalação**: Execute `./scripts/verify_portal.sh`
6. **Acessar Portal**: Abra http://localhost:32001 no navegador

---

**Data de Criação**: $(date)
**Versão**: 1.0.0

