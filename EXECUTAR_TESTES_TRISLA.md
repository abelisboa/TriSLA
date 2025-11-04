# 🚀 Guia Rápido - Executar Testes do TriSLA

## ⚡ Comandos Prontos para Copiar e Colar

### 1. Preparar Ambiente (WSL)

```bash
# Entrar no WSL
wsl

# Navegar para o diretório do projeto
cd ~/trisla-dashboard-local

# Dar permissão de execução aos scripts
chmod +x scripts-wsl/*.sh

# Instalar dependências (se necessário)
sudo apt-get update && sudo apt-get install -y curl jq bc
```

---

## 2. Executar Todos os Testes (Uma Vez Só)

```bash
# Executar sequência completa: criar slices, testes de estresse, coletar métricas e analisar
API_URL=http://localhost:5000 \
PROMETHEUS_URL=http://localhost:9090 \
NAMESPACE=trisla-nsp \
bash scripts-wsl/run-complete-tests.sh
```

**⏱️ Tempo estimado:** 15-30 minutos

---

## 3. Executar Testes Individuais

### 3.1 Apenas Criar Slices

```bash
API_URL=http://localhost:5000 bash scripts-wsl/test-create-slices.sh
```

### 3.2 Apenas Testes de Estresse

```bash
API_URL=http://localhost:5000 \
CONCURRENT_REQUESTS=30 \
TOTAL_REQUESTS=150 \
bash scripts-wsl/test-stress.sh
```

### 3.3 Apenas Coletar Métricas

```bash
# Se Prometheus está local (via túnel SSH já ativo)
PROMETHEUS_URL=http://localhost:9090 \
NAMESPACE=trisla-nsp \
bash scripts-wsl/collect-prometheus-metrics.sh

# Ou se está diretamente no node1
PROMETHEUS_URL=http://prometheus.monitoring.svc.cluster.local:9090 \
NAMESPACE=trisla-nsp \
bash scripts-wsl/collect-prometheus-metrics.sh
```

### 3.4 Apenas Analisar Resultados

```bash
bash scripts-wsl/analyze-results.sh
```

---

## 4. Atualizar Documento de Resultados

Após executar os testes:

```bash
# Atualizar documento com resultados
bash scripts-wsl/update-dissertation-results.sh
```

Isso criará um arquivo atualizado em:
- `docs/evidencias/WU-005_avaliacao/resumo_resultados_updated_*.txt`

---

## 5. Verificar Resultados

```bash
# Ver último relatório de análise
cat docs/evidencias/WU-005_avaliacao/analise_resultados_*.md | head -50

# Ver resumo
cat docs/evidencias/WU-005_avaliacao/resumo_analise_*.txt

# Listar todos os arquivos gerados
ls -lh docs/evidencias/WU-005_avaliacao/
```

---

## 6. Testar no Node1 (via SSH)

Se precisar executar no `node1`:

```bash
# 1. Conectar ao node1
ssh porvir5g@ppgca.unisinos.br
ssh node006

# 2. Configurar variáveis para o cluster Kubernetes
export API_URL=http://trisla-portal-api.trisla-nsp.svc.cluster.local:8000
export PROMETHEUS_URL=http://prometheus.monitoring.svc.cluster.local:9090
export NAMESPACE=trisla-nsp

# 3. Copiar scripts (do seu PC local) ou criar no node1
# (usar scp ou criar diretamente)

# 4. Executar testes
cd ~/trisla-deploy
bash scripts-wsl/run-complete-tests.sh
```

---

## 7. Configurações Avançadas

### Aumentar carga de testes:

```bash
CONCURRENT_REQUESTS=100 \
TOTAL_REQUESTS=500 \
API_URL=http://localhost:5000 \
bash scripts-wsl/test-stress.sh
```

### Especificar diretório de saída customizado:

```bash
OUTPUT_DIR=/tmp/trisla-tests \
bash scripts-wsl/run-complete-tests.sh
```

### Testar com diferentes endpoints:

```bash
# API em outro servidor
API_URL=http://192.168.10.16:8000 \
PROMETHEUS_URL=http://192.168.10.16:9090 \
bash scripts-wsl/run-complete-tests.sh
```

---

## 📋 Checklist de Execução

- [ ] Backend TriSLA está rodando (`http://localhost:5000`)
- [ ] Prometheus está acessível (`http://localhost:9090` ou via túnel SSH)
- [ ] Dependências instaladas (`curl`, `jq`, `bc`)
- [ ] Scripts têm permissão de execução (`chmod +x scripts-wsl/*.sh`)
- [ ] Executar `run-complete-tests.sh`
- [ ] Verificar resultados em `docs/evidencias/WU-005_avaliacao/`
- [ ] Executar `update-dissertation-results.sh`
- [ ] Revisar relatório gerado

---

## ❓ Problemas Comuns

### Erro: "API não está acessível"
```bash
# Verificar se backend está rodando
curl http://localhost:5000/api/v1/health

# Se não, iniciar backend
cd ~/trisla-dashboard-local
bash scripts-wsl/start-backend.sh
```

### Erro: "Prometheus não está acessível"
```bash
# Ativar túnel SSH primeiro
bash scripts-wsl/start-ssh-tunnel.sh

# Ou verificar se Prometheus está rodando
curl http://localhost:9090/-/healthy
```

### Erro: "Permission denied"
```bash
chmod +x scripts-wsl/*.sh
```

### Erro: "jq: command not found"
```bash
sudo apt-get update && sudo apt-get install -y jq bc curl
```

---

## 📊 Estrutura de Saída

Após executar, você terá:

```
docs/evidencias/WU-005_avaliacao/
├── scenario_*_create_*.json          # Criação de slices
├── stress_test_*_results.json        # Resultados de estresse
├── prometheus_*_*.json               # Métricas do Prometheus
├── analise_resultados_*.md           # Relatório completo
├── resumo_analise_*.txt              # Resumo executivo
└── resumo_resultados_updated_*.txt   # Documento atualizado
```

---

**Última atualização:** $(date)  
**Versão:** 1.0





