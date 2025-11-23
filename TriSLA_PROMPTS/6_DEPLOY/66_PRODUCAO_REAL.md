# 66 – Produção Real no NASP

Prompt para garantir que o TriSLA opere em produção real com dados e serviços reais do NASP.

# PROMPT — CONFIGURAÇÃO PARA PRODUÇÃO REAL NO NASP

**⚠️ OBJETIVO FUNDAMENTAL**: O TriSLA deve operar em **PRODUÇÃO REAL** no ambiente NASP, processando dados reais, interagindo com serviços reais e garantindo SLAs em tempo real. **NÃO é simulação, NÃO é ambiente de teste, NÃO usa dados sintéticos.**

---

## 1. PRINCÍPIOS DE PRODUÇÃO REAL

### **Definição de Produção Real:**

1) **Dados Reais:**
   - Métricas coletadas de dispositivos reais (RAN, Transport, Core)
   - Intents recebidos de tenants reais
   - SLAs de serviços reais em operação
   - Network slices reais sendo gerenciados

2) **Serviços Reais:**
   - Integração com serviços NASP reais via I-07
   - Comunicação com controladores reais (RAN, Transport, Core)
   - Execução de ações corretivas em infraestrutura real
   - Smart contracts executados em blockchain real (se aplicável)

3) **Tempo Real:**
   - Processamento em tempo real (não batch)
   - Decisões tomadas em tempo real
   - Ações executadas imediatamente
   - Métricas atualizadas continuamente

4) **Impacto Real:**
   - Mudanças afetam serviços reais
   - Ações corretivas modificam configurações reais
   - SLAs garantidos para usuários reais
   - Consequências reais de falhas ou sucessos

---

## 2. CONFIGURAÇÃO PARA PRODUÇÃO REAL

### **Passo 1: Desabilitar Modos de Simulação/Teste**

**Verificar e remover flags de simulação:**

```python
# ❌ NÃO PERMITIR em produção:
SIMULATION_MODE = False  # OBRIGATÓRIO: False
MOCK_SERVICES = False    # OBRIGATÓRIO: False
USE_SYNTHETIC_DATA = False  # OBRIGATÓRIO: False
TEST_MODE = False        # OBRIGATÓRIO: False
DRY_RUN = False          # OBRIGATÓRIO: False (exceto validações específicas)
```

**Configuração obrigatória:**
```yaml
# values.yaml - PRODUÇÃO REAL
environment: production
simulation:
  enabled: false
mock:
  enabled: false
real:
  services: true
  data: true
  actions: true
```

### **Passo 2: Configurar Endpoints Reais do NASP**

**Interface I-07 - Adapter NASP deve conectar a serviços REAIS:**

```python
# Configuração REAL do NASP
NASP_ENDPOINTS = {
    "ran_controller": "http://<REAL_RAN_CONTROLLER_IP>:<PORT>",
    "transport_controller": "http://<REAL_TRANSPORT_CONTROLLER_IP>:<PORT>",
    "core_controller": "http://<REAL_CORE_CONTROLLER_IP>:<PORT>",
    "slice_manager": "http://<REAL_SLICE_MANAGER_IP>:<PORT>",
    "metrics_collector": "http://<REAL_METRICS_COLLECTOR_IP>:<PORT>"
}

# ⚠️ VALORES OBRIGATÓRIOS - Substituir pelos IPs/URLs REAIS do NASP
# NÃO usar localhost, NÃO usar mocks, NÃO usar simulações
```

**Validação de conectividade:**
```python
def validate_real_connectivity():
    """Valida que todos os endpoints reais estão acessíveis"""
    for service, endpoint in NASP_ENDPOINTS.items():
        response = requests.get(f"{endpoint}/health", timeout=5)
        if response.status_code != 200:
            raise ConnectionError(f"Cannot connect to real {service} at {endpoint}")
    return True
```

### **Passo 3: Configurar Coleta de Métricas Reais**

**SLA-Agent Layer deve coletar métricas REAIS:**

```python
# Configuração de coleta REAL
METRICS_SOURCES = {
    "ran": {
        "type": "real",  # OBRIGATÓRIO: "real"
        "endpoint": "<REAL_RAN_METRICS_ENDPOINT>",
        "polling_interval": 5,  # segundos - tempo real
        "synthetic": False  # OBRIGATÓRIO: False
    },
    "transport": {
        "type": "real",
        "endpoint": "<REAL_TRANSPORT_METRICS_ENDPOINT>",
        "polling_interval": 5,
        "synthetic": False
    },
    "core": {
        "type": "real",
        "endpoint": "<REAL_CORE_METRICS_ENDPOINT>",
        "polling_interval": 5,
        "synthetic": False
    }
}
```

### **Passo 4: Configurar Execução de Ações Reais**

**Decision Engine e SLA-Agents devem executar ações REAIS:**

```python
# Configuração de execução REAL
ACTION_EXECUTION = {
    "mode": "real",  # OBRIGATÓRIO: "real"
    "dry_run": False,  # OBRIGATÓRIO: False em produção
    "confirm_before_execute": False,  # Auto-executar em produção
    "rollback_on_failure": True,
    "log_all_actions": True
}

# Exemplo de ação REAL
def execute_real_corrective_action(action_type, parameters):
    """Executa ação corretiva REAL no NASP"""
    if ACTION_EXECUTION["mode"] != "real":
        raise ValueError("Cannot execute in non-real mode")
    
    # Conectar ao controlador REAL
    controller = get_real_controller(action_type)
    
    # Executar ação REAL
    result = controller.execute_action(parameters)
    
    # Log da ação REAL
    log_real_action(action_type, parameters, result)
    
    return result
```

---

## 3. INTEGRAÇÃO REAL COM NASP

### **Interface I-07 - Adapter NASP Real**

**O adaptador deve:**

1) **Conectar a serviços NASP reais:**
   - APIs REST reais do NASP
   - WebSockets reais para métricas em tempo real
   - Event streams reais
   - NÃO usar mocks ou stubs

2) **Processar dados reais:**
   - Métricas reais de dispositivos
   - Eventos reais de rede
   - Status real de slices
   - NÃO gerar dados sintéticos

3) **Executar ações reais:**
   - Modificar configurações reais
   - Aplicar políticas reais
   - Atualizar slices reais
   - NÃO simular ações

**Código exemplo:**
```python
class RealNASPAdapter:
    """Adapter que conecta ao NASP REAL"""
    
    def __init__(self, real_endpoints):
        self.endpoints = real_endpoints
        self.verify_real_connectivity()
    
    def verify_real_connectivity(self):
        """Verifica conectividade com serviços REAIS"""
        for service, endpoint in self.endpoints.items():
            try:
                response = requests.get(f"{endpoint}/health", timeout=5)
                if response.status_code != 200:
                    raise ConnectionError(
                        f"Cannot connect to REAL {service} service. "
                        f"This is PRODUCTION - all services must be REAL."
                    )
            except Exception as e:
                raise ConnectionError(
                    f"CRITICAL: Cannot reach REAL NASP service {service}. "
                    f"Production requires REAL services. Error: {e}"
                )
    
    def get_real_metrics(self, domain):
        """Coleta métricas REAIS do NASP"""
        endpoint = self.endpoints[f"{domain}_metrics"]
        response = requests.get(f"{endpoint}/metrics/current")
        return response.json()  # Dados REAIS
    
    def execute_real_action(self, action):
        """Executa ação REAL no NASP"""
        endpoint = self.endpoints["action_executor"]
        response = requests.post(f"{endpoint}/execute", json=action)
        # Ação REAL foi executada - impacto real na infraestrutura
        return response.json()
```

---

## 4. VALIDAÇÃO DE PRODUÇÃO REAL

### **Checklist de Validação:**

**Antes de considerar em produção real, validar:**

1) **Conectividade Real:**
   ```bash
   # Testar conectividade com serviços REAIS
   curl http://<REAL_RAN_CONTROLLER>/health
   curl http://<REAL_TRANSPORT_CONTROLLER>/health
   curl http://<REAL_CORE_CONTROLLER>/health
   ```
   **Saída esperada:**
   ```
   {"status": "healthy", "service": "ran-controller", "version": "x.x.x"}
   ```

2) **Métricas Reais:**
   ```bash
   # Verificar se métricas são REAIS
   kubectl logs -n trisla deployment/trisla-sla-agent-ran | grep -i "real\|synthetic\|mock"
   ```
   **Saída esperada:**
   ```
   [INFO] Collecting REAL metrics from RAN controller
   [INFO] Received REAL metric: latency=12.5ms
   ```
   **NÃO deve aparecer:**
   - "synthetic"
   - "mock"
   - "simulated"
   - "fake"

3) **Ações Reais:**
   ```bash
   # Verificar logs de ações REAIS
   kubectl logs -n trisla deployment/trisla-decision-engine | grep "executing REAL action"
   ```
   **Saída esperada:**
   ```
   [INFO] Executing REAL corrective action: adjust_qos_profile
   [INFO] REAL action executed successfully on RAN controller
   ```

4) **Configuração de Produção:**
   ```bash
   # Verificar variáveis de ambiente
   kubectl get configmap trisla-config -n trisla -o yaml | grep -i "simulation\|mock\|real"
   ```
   **Saída esperada:**
   ```yaml
   SIMULATION_MODE: "false"
   USE_REAL_SERVICES: "true"
   PRODUCTION_MODE: "true"
   ```

---

## 5. MONITORAMENTO DE PRODUÇÃO REAL

### **Métricas a Monitorar:**

1) **Conectividade Real:**
   - Latência de conexão com serviços NASP reais
   - Taxa de sucesso de requisições a serviços reais
   - Timeout de serviços reais

2) **Processamento Real:**
   - Tempo de processamento de intents reais
   - Taxa de decisões tomadas em tempo real
   - Ações reais executadas por minuto

3) **Impacto Real:**
   - SLAs garantidos para serviços reais
   - Melhoria de performance após ações reais
   - Redução de violações de SLA após ações reais

4) **Alertas de Produção:**
   - Alertar se detectar modo simulação ativado
   - Alertar se detectar uso de dados sintéticos
   - Alertar se serviços reais não estiverem acessíveis

---

## 6. TRANSIÇÃO DE TESTE PARA PRODUÇÃO REAL

### **Processo de Transição:**

1) **Fase 1: Validação em Ambiente de Teste**
   - Testes com dados sintéticos (OK)
   - Validação de funcionalidades
   - Correção de bugs

2) **Fase 2: Validação com Serviços Reais (Staging)**
   - Conectar a serviços NASP reais
   - Usar dados reais (read-only)
   - NÃO executar ações reais (dry-run)

3) **Fase 3: Produção Real (Ativação)**
   - ✅ Conectar a serviços NASP reais
   - ✅ Usar dados reais
   - ✅ Executar ações reais
   - ✅ Impacto real na infraestrutura

**Script de transição:**
```bash
#!/bin/bash
# Script de transição para produção real

echo "⚠️  TRANSITIONING TO REAL PRODUCTION MODE"
echo "This will enable REAL actions on REAL infrastructure"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Desabilitar simulação
kubectl set env deployment/trisla-decision-engine -n trisla \
  SIMULATION_MODE=false \
  USE_REAL_SERVICES=true \
  PRODUCTION_MODE=true

# Desabilitar dry-run
kubectl set env deployment/trisla-sla-agent-ran -n trisla \
  DRY_RUN=false \
  EXECUTE_REAL_ACTIONS=true

# Validar configuração
./scripts/validate-production-real.sh

echo "✅ TriSLA is now in REAL PRODUCTION MODE"
echo "⚠️  All actions will have REAL impact on infrastructure"
```

---

## 7. SEGURANÇA EM PRODUÇÃO REAL

### **Proteções Necessárias:**

1) **Validação de Ações:**
   - Validar todas as ações antes de executar
   - Limites de segurança para ações destrutivas
   - Confirmação para ações críticas (opcional, configurável)

2) **Rollback Automático:**
   - Monitorar impacto de ações reais
   - Rollback automático se ação causar degradação
   - Logs detalhados de todas as ações reais

3) **Rate Limiting:**
   - Limitar número de ações por minuto
   - Prevenir ações em cascata
   - Circuit breaker para serviços reais

---

## 8. DOCUMENTAÇÃO DE PRODUÇÃO REAL

### **Entregar:**

1) **Configuração de Produção:**
   - Arquivo de configuração para produção real
   - Valores reais dos endpoints NASP
   - Flags de produção vs simulação

2) **Procedimentos:**
   - Como ativar produção real
   - Como validar que está em produção real
   - Como fazer rollback se necessário

3) **Monitoramento:**
   - Dashboards específicos para produção real
   - Alertas de produção real
   - Métricas de impacto real

---

## ⚠️ LEMBRETES CRÍTICOS

1) **NUNCA usar simulação em produção real**
2) **SEMPRE validar conectividade com serviços reais antes de ativar**
3) **MONITORAR continuamente que está operando em modo real**
4) **TER plano de rollback para ações reais**
5) **DOCUMENTAR todas as ações reais executadas**

---

**OBJETIVO FINAL**: TriSLA operando em **PRODUÇÃO REAL** no NASP, processando dados reais, executando ações reais e garantindo SLAs reais em tempo real.

