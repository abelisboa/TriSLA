# 09 — MASTER-HEARTBEAT-ORCHESTRATOR v1.0

**TriSLA — Mecanismo de HEARTBEAT contínuo + READY REPORT em snapshot**

---

## 1. Finalidade

Este documento define o mecanismo padronizado de **monitoramento de saúde (HEARTBEAT)** e de **relatório de prontidão (READY REPORT)** do projeto TriSLA, alinhado ao fluxo DevOps consolidado (v6.0) e à arquitetura experimental TriSLA–NASP.

Os objetivos principais são:

- Monitorar continuamente a saúde dos módulos críticos do TriSLA.
- Gerar relatórios de prontidão (snapshot) antes de operações importantes (deploy, testes E2E, demonstrações).
- Padronizar a forma como a equipe consulta o estado atual da plataforma, tanto **localmente** quanto no **NASP**.

---

## 2. Escopo de monitoramento

Módulos e componentes verificados pelo HEARTBEAT/READY REPORT:

1. **SEM-CSMF**  
   - Endpoint: `http://127.0.0.1:8080/health`

2. **ML-NSMF**  
   - Endpoint: `http://127.0.0.1:8081/health`

3. **Decision Engine**  
   - Endpoint: `http://127.0.0.1:8082/health`

4. **Blockchain (Besu)**  
   - Endpoint RPC: `http://127.0.0.1:8545`  
   - Método: `eth_blockNumber` (JSON-RPC)

5. **Kafka Broker**  
   - Endpoint TCP: `127.0.0.1:9092`

6. **OTLP Collector**  
   - Endpoint TCP: `127.0.0.1:4317` (gRPC)  
   - Endpoint HTTP opcional: `127.0.0.1:4318`

7. **Prometheus (monitoramento)**  
   - Endpoint: `http://127.0.0.1:9090/-/healthy`

---

## 3. Arquivos criados nesta FASE G

### 3.1. Documentação (Prompts)

- `TriSLA_PROMPTS/0_MASTER/09_MASTER_HEARTBEAT_ORCHESTRATOR.md`  
  → Este documento.

### 3.2. Scripts Python

- `scripts/heartbeat.py`  
  → Executa todas as verificações, imprime um resumo no console, retorna código de saída (0 = saudável, 1 = degradado/erro) e pode ser importado por outros scripts.

- `scripts/ready-report.py`  
  → Usa o módulo de heartbeat para gerar **relatórios snapshot**:
  - `docs/READY_STATUS_TRI-SLA_v1.md`
  - `docs/READY_STATUS_TRI-SLA_v1.json`

### 3.3. Scripts Shell

- `scripts/heartbeat.sh`  
  → Loop contínuo de heartbeat.  
  → Usa `scripts/heartbeat.py`, grava em `logs/heartbeat.log` e mantém um semáforo em tempo real.

- `scripts/ready-report.sh`  
  → Wrapper simplificado para gerar o READY REPORT via `scripts/ready-report.py`.

---

## 4. Integração com o pipeline TriSLA

O arquivo `TRISLA_AUTO_RUN.sh` será atualizado para a versão **v7.0**, incorporando:

1. **Chamada inicial:**
   - Iniciar `scripts/heartbeat.sh` em **background** logo no começo do pipeline (modo Dev Sandbox).

2. **Chamada final:**
   - Executar `scripts/ready-report.sh` após a conclusão dos testes (unit/integration/E2E), gerando o snapshot de prontidão.

3. **Mensagens de log:**
   - O pipeline deve registrar no console:
     - Quando o HEARTBEAT é iniciado.
     - Onde está o arquivo `logs/heartbeat.log`.
     - Onde foi gerado o `READY_STATUS_TRI-SLA_v1.md`.

---

## 5. Modos de execução

### 5.1. HEARTBEAT (contínuo)

**Uso recomendado:**

```bash
chmod +x scripts/heartbeat.sh
./scripts/heartbeat.sh
```

**Características:**

- Executa em loop com intervalo configurável (padrão: 30 segundos).
- Registra uma linha por ciclo em `logs/heartbeat.log`.
- Pode rodar em background via pipeline ou systemd/cron.

### 5.2. READY REPORT (snapshot)

**Uso recomendado:**

```bash
chmod +x scripts/ready-report.sh
./scripts/ready-report.sh
```

**Resultados esperados:**

- `docs/READY_STATUS_TRI-SLA_v1.md` → relatório humano (Markdown).
- `docs/READY_STATUS_TRI-SLA_v1.json` → relatório estruturado (JSON).

---

## 6. Estrutura do relatório de prontidão

### 6.1. Formato JSON

Chave principal: `overall_status` (`HEALTHY`, `DEGRADED`, `ERROR`)

Exemplo de estrutura:

```json
{
  "timestamp": "2025-11-21T09:14:55Z",
  "overall_status": "DEGRADED",
  "checks": [
    {
      "name": "sem-csmf",
      "type": "http",
      "target": "http://127.0.0.1:8080/health",
      "status": "OK",
      "detail": "HTTP 200"
    },
    {
      "name": "ml-nsmf",
      "type": "http",
      "target": "http://127.0.0.1:8081/health",
      "status": "ERROR",
      "detail": "Timeout"
    }
  ]
}
```

### 6.2. Formato Markdown

Estrutura mínima:

- Cabeçalho com data/hora
- Status geral
- Tabela com os módulos e seus estados
- Seção de observações

---

## 7. Uso local vs NASP

### Ambiente Local (Dev Sandbox)

- **Foco:** validar se os módulos TriSLA estão saudáveis no ambiente de desenvolvimento.
- **HEARTBEAT** roda na máquina local.
- **READY REPORT** é usado antes de:
  - Confirmação de correções
  - Push para GitHub
  - Execução de testes E2E

### Ambiente NASP (Node1/Node2)

- **Foco:** saúde da instância real do TriSLA em Kubernetes.
- Scripts podem ser:
  - Adaptados para endpoints internos do cluster.
  - Executados via cron, systemd ou Jobs em K8s.
- **READY REPORT** pode ser usado como parte do checklist de Go/No-Go.

---

## 8. Checklist rápido de uso

- [ ] `scripts/heartbeat.py` criado e executável.
- [ ] `scripts/ready-report.py` criado e executável.
- [ ] `scripts/heartbeat.sh` criado, com `chmod +x`.
- [ ] `scripts/ready-report.sh` criado, com `chmod +x`.
- [ ] `TRISLA_AUTO_RUN.sh` atualizado para v7.0:
  - Chamada de `heartbeat.sh` no início.
  - Chamada de `ready-report.sh` no final.
- [ ] `docs/` e `logs/` usados para saída dos relatórios.

---

## 9. Versão e manutenção

**Versão inicial:** v1.0 (FASE G)

**Alinhado ao:** MASTER_DEVOPS_CONSOLIDATOR_v6.0

**Evoluções futuras:**

- Suporte a parâmetros (ambiente: local/nasp).
- Integração com sistemas de alerta (Alertmanager, e-mail).
- Exposição de endpoint `/health/tri-sla` consolidado.

---

**Versão:** 1.0  
**Última atualização:** 2025-11-21  
**Alinhado com:** MASTER-DEVOPS-CONSOLIDATOR v6.0

