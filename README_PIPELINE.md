# 🚀 TriSLA Complete Build & Deploy Pipeline

**Author:** Abel Lisboa <abelisboa@gmail.com>  
**Date:** 2025-10-23  
**Location:** `/mnt/c/Users/USER/Documents/trisla-deploy/`

## 📦 Módulos Incluídos

### Core TriSLA Modules
- **apps/semantic** - Ontologia e Processamento Semântico
- **apps/ai** - Machine Learning e Inteligência Artificial  
- **apps/blockchain** - Smart Contracts e Blockchain
- **apps/integration** - Integração e APIs
- **apps/monitoring** - Observabilidade e Métricas

### Portal Modules
- **apps/api** - FastAPI Backend
- **apps/ui** - Frontend React + Nginx

## 🛠️ Scripts Disponíveis

### 1. `setup_docker_ghcr.sh`
Configuração inicial do ambiente Docker e autenticação com GitHub Container Registry.

```bash
./setup_docker_ghcr.sh
```

**Funcionalidades:**
- ✅ Verifica instalação do Docker
- ✅ Valida Docker daemon
- ✅ Configura autenticação GHCR
- ✅ Cria arquivos .dockerignore

### 2. `build_all.sh`
Constrói todas as imagens Docker dos módulos TriSLA.

```bash
# Build com versão padrão (latest)
./build_all.sh

# Build com versão específica
VERSION=v1.0.0 ./build_all.sh
```

**Módulos construídos:**
- `ghcr.io/abelisboa/trisla-semantic:latest`
- `ghcr.io/abelisboa/trisla-ai:latest`
- `ghcr.io/abelisboa/trisla-blockchain:latest`
- `ghcr.io/abelisboa/trisla-integration:latest`
- `ghcr.io/abelisboa/trisla-monitoring:latest`
- `ghcr.io/abelisboa/trisla-api:latest`
- `ghcr.io/abelisboa/trisla-ui:latest`

### 3. `test_images.sh`
Testa todas as imagens construídas localmente.

```bash
./test_images.sh
```

**Testes realizados:**
- ✅ Inicialização dos containers
- ✅ Health checks HTTP
- ✅ Validação de logs
- ✅ Cleanup automático

### 4. `push_all.sh`
Publica todas as imagens no GitHub Container Registry.

```bash
# Push com versão padrão
./push_all.sh

# Push com versão específica
VERSION=v1.0.0 ./push_all.sh
```

### 5. `run_complete_pipeline.sh`
Executa o pipeline completo em sequência.

```bash
./run_complete_pipeline.sh
```

**Etapas executadas:**
1. 🔧 Setup Docker & GHCR
2. 🔨 Build de todas as imagens
3. 🧪 Teste das imagens
4. 📤 Push para GHCR

## 🚀 Execução Rápida

### Opção 1: Pipeline Completo
```bash
./run_complete_pipeline.sh
```

### Opção 2: Execução Manual
```bash
# 1. Setup
./setup_docker_ghcr.sh

# 2. Build
./build_all.sh

# 3. Test
./test_images.sh

# 4. Push
./push_all.sh
```

## 🔧 Pré-requisitos

### Docker
- Docker Desktop (Windows/macOS) ou Docker Engine (Linux)
- Docker daemon rodando

### GitHub Container Registry
- Conta GitHub: `abelisboa`
- Token com permissões `write:packages` e `read:packages`

### Autenticação
```bash
# Opção 1: GitHub CLI
gh auth login
gh auth token | docker login ghcr.io -u abelisboa --password-stdin

# Opção 2: Token direto
docker login ghcr.io -u abelisboa
# Digite seu token como senha
```

## 📊 Portas dos Serviços

| Módulo | Porta | Health Check |
|--------|-------|--------------|
| semantic | 8080 | `/health` |
| ai | 8080 | `/health` |
| blockchain | 7051 | - |
| integration | 8080 | `/health` |
| monitoring | 9090 | `/-/healthy` |
| api | 8000 | `/health` |
| ui | 80 | `/` |

## 🧪 Teste Local

```bash
# Testar módulos individuais
docker run -p 8080:8080 ghcr.io/abelisboa/trisla-semantic:latest
docker run -p 8080:8080 ghcr.io/abelisboa/trisla-ai:latest
docker run -p 8000:8000 ghcr.io/abelisboa/trisla-api:latest
docker run -p 80:80 ghcr.io/abelisboa/trisla-ui:latest
```

## 📋 Estrutura de Arquivos

```
trisla-deploy/
├── src/                          # Core TriSLA modules
│   ├── semantic/
│   ├── ai/
│   ├── blockchain/
│   ├── integration/
│   └── monitoring/
├── trisla-portal/apps/           # Portal modules
│   ├── api/
│   └── ui/
├── build_all.sh                  # Build script
├── push_all.sh                   # Push script
├── test_images.sh                # Test script
├── setup_docker_ghcr.sh          # Setup script
├── run_complete_pipeline.sh      # Master pipeline
└── README_PIPELINE.md            # This file
```

## 🔍 Troubleshooting

### Docker não encontrado
```bash
# Windows: Instalar Docker Desktop
# Linux: sudo apt-get install docker.io
# macOS: brew install --cask docker
```

### Falha de autenticação GHCR
```bash
# Verificar token
gh auth status

# Re-autenticar
docker logout ghcr.io
docker login ghcr.io -u abelisboa
```

### Container não inicia
```bash
# Verificar logs
docker logs <container_name>

# Verificar recursos
docker system df
docker system prune
```

## 📈 Monitoramento

### Verificar imagens construídas
```bash
docker images | grep ghcr.io/abelisboa/trisla-
```

### Verificar containers rodando
```bash
docker ps | grep trisla
```

### Limpar recursos
```bash
docker system prune -a
```

## 🎯 Próximos Passos

1. **Deploy em Kubernetes** - Usar Helm charts em `helm/deployments/`
2. **CI/CD Pipeline** - Integrar com GitHub Actions
3. **Monitoramento** - Configurar Prometheus/Grafana
4. **Segurança** - Implementar scanning de vulnerabilidades

---

**Status:** ✅ Pipeline completo e funcional  
**Última atualização:** 2025-10-23  
**Versão:** 1.0.0









