# 🧪 Comandos para Executar Testes do TriSLA

## Pré-requisitos

1. **WSL ativo** com acesso ao ambiente Linux
2. **Backend TriSLA rodando** (se testar localmente: `http://localhost:5000`)
3. **Prometheus acessível** (via túnel SSH ou diretamente em `http://localhost:9090`)
4. **Dependências instaladas**: `curl`, `jq`, `bc`

---

## 📋 Opção 1: Executar Todos os Testes (Recomendado)

Execute o script completo que faz tudo automaticamente:

```bash
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/*.sh
API_URL=http://localhost:5000 PROMETHEUS_URL=http://localhost:9090 bash scripts-wsl/run-complete-tests.sh
```

---

## 📋 Opção 2: Executar Testes Individuais

### 1. Criar Slices (URLLC, eMBB, mMTC)

```bash
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/test-create-slices.sh
API_URL=http://localhost:5000 bash scripts-wsl/test-create-slices.sh
```

**Variáveis opcionais:**
- `API_URL`: URL da API (padrão: `http://localhost:5000`)
- `OUTPUT_DIR`: Diretório para salvar evidências (padrão: `docs/evidencias/WU-005_avaliacao`)

---

### 2. Testes de Estresse

```bash
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/test-stress.sh
API_URL=http://localhost:5000 CONCURRENT_REQUESTS=30 TOTAL_REQUESTS=150 bash scripts-wsl/test-stress.sh
```

**Variáveis opcionais:**
- `API_URL`: URL da API
- `CONCURRENT_REQUESTS`: Requisições simultâneas (padrão: 50)
- `TOTAL_REQUESTS`: Total de requisições (padrão: 200)
- `REQUEST_DELAY`: Delay entre requisições em segundos (padrão: 0.1)

---

### 3. Coletar Métricas do Prometheus

```bash
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/collect-prometheus-metrics.sh
PROMETHEUS_URL=http://localhost:9090 NAMESPACE=trisla-nsp bash scripts-wsl/collect-prometheus-metrics.sh
```

**Variáveis opcionais:**
- `PROMETHEUS_URL`: URL do Prometheus (padrão: `http://localhost:9090`)
- `NAMESPACE`: Namespace Kubernetes (padrão: `trisla-nsp`)

**⚠️ Importante:** Se o Prometheus estiver no `node1`, você precisa:
1. Ativar o túnel SSH primeiro:
   ```bash
   bash scripts-wsl/start-ssh-tunnel.sh
   ```
2. Ou configurar `PROMETHEUS_URL` para a URL via túnel

---

### 4. Analisar Resultados

```bash
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/analyze-results.sh
bash scripts-wsl/analyze-results.sh
```

Este script:
- Analisa os resultados dos testes anteriores
- Gera um relatório em Markdown (`analise_resultados_*.md`)
- Gera um resumo em texto (`resumo_analise_*.txt`)

---

## 🌐 Testar no Node1 (via SSH)

Se você quiser executar os testes diretamente no `node1`:

### 1. Conectar ao node1

```bash
ssh porvir5g@ppgca.unisinos.br
# Depois de conectar:
ssh node006
```

### 2. Configurar variáveis para o node1

```bash
export API_URL=http://localhost:8000  # Ou o IP do serviço no cluster
export PROMETHEUS_URL=http://prometheus.monitoring:9090  # Ajuste conforme necessário
export NAMESPACE=trisla-nsp

# Copiar scripts para o node1 (do seu PC local)
# (Usar scp ou criar os arquivos diretamente no node1)
```

### 3. Executar testes no node1

```bash
cd ~/trisla-deploy
bash scripts-wsl/run-complete-tests.sh
```

---

## 📊 Estrutura de Arquivos Gerados

Após executar os testes, os arquivos serão salvos em:

```
docs/evidencias/WU-005_avaliacao/
├── scenario_urllc_create_YYYYMMDD_HHMMSS.json
├── scenario_embb_create_YYYYMMDD_HHMMSS.json
├── scenario_mmtc_create_YYYYMMDD_HHMMSS.json
├── stress_test_urllc_YYYYMMDD_HHMMSS_results.json
├── stress_test_embb_YYYYMMDD_HHMMSS_results.json
├── stress_test_mmtc_YYYYMMDD_HHMMSS_results.json
├── prometheus_cpu_usage_YYYYMMDD_HHMMSS.json
├── prometheus_memory_usage_YYYYMMDD_HHMMSS.json
├── prometheus_latency_p99_YYYYMMDD_HHMMSS.json
├── analise_resultados_YYYYMMDD_HHMMSS.md
└── resumo_analise_YYYYMMDD_HHMMSS.txt
```

---

## 🔍 Verificar Resultados

### Ver resumo dos testes:

```bash
cat docs/evidencias/WU-005_avaliacao/resumo_analise_*.txt
```

### Ver relatório completo:

```bash
cat docs/evidencias/WU-005_avaliacao/analise_resultados_*.md
```

### Analisar métricas do Prometheus:

```bash
# Ver CPU usage
jq '.data.result[] | {pod: .metric.pod, value: .value[1]}' \
  docs/evidencias/WU-005_avaliacao/prometheus_cpu_usage_*.json

# Ver latência p99
jq '.data.result[] | {pod: .metric.pod, latency_p99: .value[1]}' \
  docs/evidencias/WU-005_avaliacao/prometheus_latency_p99_*.json
```

---

## ⚙️ Configurações Avançadas

### Ajustar número de requisições de estresse:

```bash
CONCURRENT_REQUESTS=100 TOTAL_REQUESTS=500 bash scripts-wsl/test-stress.sh
```

### Especificar diretório de saída:

```bash
OUTPUT_DIR=/path/to/output bash scripts-wsl/run-complete-tests.sh
```

### Testar com diferentes URLs:

```bash
API_URL=http://192.168.10.16:8000 \
PROMETHEUS_URL=http://192.168.10.16:9090 \
bash scripts-wsl/run-complete-tests.sh
```

---

## 📝 Próximos Passos

Após executar os testes:

1. ✅ Revisar os relatórios gerados
2. ✅ Analisar as métricas coletadas
3. ✅ Atualizar o documento de resultados da dissertação
4. ✅ Gerar gráficos e visualizações (opcional)

---

## ❓ Troubleshooting

### Erro: "API não está acessível"
- Verifique se o backend está rodando: `curl http://localhost:5000/api/v1/health`
- Confirme a URL da API: `echo $API_URL`

### Erro: "Prometheus não está acessível"
- Ative o túnel SSH: `bash scripts-wsl/start-ssh-tunnel.sh`
- Verifique a porta: `netstat -tuln | grep 9090`

### Erro: "jq: command not found"
- Instale: `sudo apt-get update && sudo apt-get install -y jq bc curl`

### Erro: "Permission denied"
- Dê permissão de execução: `chmod +x scripts-wsl/*.sh`

---

**Última atualização:** $(date)  
**Autor:** Abel José Rodrigues Lisboa





