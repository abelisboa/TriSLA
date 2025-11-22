# 03 – ESTRATÉGIA DE EXECUÇÃO

Guia completo sobre onde e como executar cada prompt do TriSLA.

# ESTRATÉGIA DE EXECUÇÃO DOS PROMPTS TRI-SLA

Este documento define claramente **onde** e **como** executar cada prompt da sequência oficial, seguindo o fluxo: **Local → GitHub → NASP**.

---

## 🔄 FLUXO GERAL DE TRABALHO

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│  AMBIENTE LOCAL  │ ───> │    GITHUB    │ ───> │  NASP (node1/2) │
│  (Desenvolvimento)│      │ (Repositório) │      │   (Produção)    │
└─────────────────┘      └──────────────┘      └─────────────────┘
      │                          │                        │
      │                          │                        │
      ▼                          ▼                        ▼
 1. Executar prompts        2. Commit/Push           3. Deploy via
    (gerar código)             código público          Ansible/Helm
    configurações)             (apenas público)        (instruções)
```

### **Princípio Fundamental:**
- ✅ **TODOS os prompts são executados LOCALMENTE**
- ✅ **Código gerado é publicado no GitHub**: https://github.com/abelisboa/TriSLA
- ✅ **Deploy no NASP é feito a partir do GitHub** usando Ansible playbooks ou instruções manuais

---

## 🖥️ AMBIENTES DE EXECUÇÃO

### **1. Ambiente Local (Máquina de Desenvolvimento)**
- **Onde**: Máquina local onde estamos trabalhando (Windows/Linux/Mac)
- **Função**: Executar TODOS os prompts, gerar código, configs, playbooks
- **Ferramentas necessárias**: 
  - Git (para versionamento)
  - IDE/Editor
  - Docker (opcional, para testes locais)
  - Ansible (para criar playbooks, não executar ainda)

### **2. GitHub (Repositório Público)**
- **URL**: https://github.com/abelisboa/TriSLA
- **Função**: Armazenar código-fonte, configs, playbooks Ansible, Helm charts
- **Conteúdo**: Apenas código público (sem secrets, sem dados sensíveis)
- **Estrutura esperada**:
  - `/apps` - Código dos módulos TriSLA
  - `/ansible` - Playbooks para deploy no NASP
  - `/helm` - Helm charts
  - `/configs` - Configurações
  - `/scripts` - Scripts de instalação/configuração

### **3. Ambiente NASP (Servidores de Produção)**
- **Onde**: Servidores NASP (node1 e node2)
- **IP node1**: `192.168.10.16` (conforme auto-configuração)
- **Interface**: `my5g`
- **Função**: Executar playbooks Ansible ou seguir instruções manuais para deploy
- **Acesso**: Via SSH (para execução de playbooks/instruções)
- **Ferramentas necessárias no NASP**: 
  - kubectl (configurado para o cluster)
  - helm
  - git (para clonar/pull do repositório)
  - Ansible (se playbooks serão executados localmente no NASP)

---

## 📋 CLASSIFICAÇÃO DOS PROMPTS

### ✅ **TODOS OS PROMPTS SÃO EXECUTADOS LOCALMENTE**

**IMPORTANTE**: Todos os 27 prompts da sequência são executados na máquina local. Eles geram código, configurações, playbooks Ansible e instruções que serão publicados no GitHub e posteriormente usados para deploy no NASP.

| # | Prompt | O que gera | Onde vai |
|---|--------|------------|----------|
| 1 | `00_PROMPT_MASTER_PLANEJAMENTO` | Documentação, planejamento | GitHub `/docs` |
| 2 | `10_INFRA_NASP` | Scripts de auto-config, validação | GitHub `/scripts` |
| 3 | `11_ANSIBLE_INVENTORY` | Inventory Ansible, playbooks | GitHub `/ansible` |
| 4 | `12_PRE_FLIGHT` | Scripts de validação pré-deploy | GitHub `/scripts` |
| 5-11 | `20_SEM_CSMF` até `26_ADAPTER_NASP` | Código dos módulos TriSLA | GitHub `/apps` |
| 12-14 | `30_OBSERVABILITY_OTLP` até `32_DASHBOARDS_GRAFANA` | Configs de observabilidade | GitHub `/monitoring` |
| 15-17 | `40_UNIT_TESTS` até `42_E2E_TESTS` | Testes automatizados | GitHub `/tests` |
| 18-21 | `50_*` até `53_*` | Workflows CI/CD, empacotamento | GitHub `/.github/workflows` |
| 22 | `60_HELM_CHART` | Helm charts completos | GitHub `/helm` |
| 23 | `61_HELM_VALIDATION` | Scripts de validação Helm | GitHub `/scripts` |
| 24-26 | `62_DEPLOY_*` até `64_DEPLOY_NASP` | **Playbooks Ansible + Instruções manuais** | GitHub `/ansible`, `/docs` |
| 27 | `65_ROLLBACK_STRATEGY` | Scripts de rollback | GitHub `/scripts` |

**Características:**
- ✅ Todos executados localmente
- ✅ Geram código, configs, playbooks
- ✅ Resultados são commitados no Git
- ✅ Publicados no GitHub (apenas conteúdo público)
- ✅ Playbooks/instruções são usados DEPOIS para deploy no NASP

---

### 🚀 **DEPLOY NO NASP (Execução dos Artefatos Gerados)**

Após os prompts serem executados e o código publicado no GitHub, o deploy no NASP é feito de duas formas:

#### **Opção 1: Via Ansible Playbooks** (Recomendado)
- Playbooks gerados pelos prompts são executados no NASP
- Execução pode ser feita:
  - **Localmente** (máquina local executa playbooks que conectam ao NASP via SSH)
  - **No NASP** (node1 executa playbooks que fazem pull do GitHub)

#### **Opção 2: Via Instruções Manuais**
- Documentação/scripts gerados pelos prompts são seguidos manualmente
- Execução feita diretamente no node1/node2 via SSH

**Exemplo de fluxo de deploy:**
```bash
# No NASP (node1), após código estar no GitHub:
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA/ansible
ansible-playbook -i inventory.ini deploy-trisla.yml
```

---

## 🔌 CONEXÃO COM O SERVIDOR NASP

### **Pré-requisitos para Acesso Remoto**

1. **Acesso SSH ao node1:**
   ```bash
   ssh usuario@192.168.10.16
   # ou
   ssh usuario@node1.nasp.local
   ```

2. **Configuração do kubectl para o cluster NASP:**
   - Arquivo `kubeconfig` do cluster NASP
   - Contexto configurado: `kubectl config use-context nasp-cluster`

3. **Ansible configurado (para prompts que usam):**
   - Inventory atualizado com IPs reais
   - Chaves SSH configuradas
   - Variáveis de ambiente do NASP

4. **Helm configurado:**
   - Repositórios adicionados
   - Autenticação GHCR configurada

### **Script de Conexão Rápida**

Criar script `connect_nasp.sh`:
```bash
#!/bin/bash
# Conecta ao node1 do NASP e configura ambiente

export TRISLA_NODE_INTERFACE="my5g"
export TRISLA_NODE_IP="192.168.10.16"
export TRISLA_GATEWAY="192.168.10.1"

# Carregar variáveis do script de auto-configuração
source trisla_nasp_env.sh

# Conectar via SSH
ssh usuario@$TRISLA_NODE_IP
```

---

## 📝 WORKFLOW DE EXECUÇÃO COMPLETO

### **Fase 1: Planejamento (Prompt 1)**
1. ✅ **Local**: Executar `00_PROMPT_MASTER_PLANEJAMENTO`
2. ✅ **Local**: Revisar e validar planejamento
3. ✅ **GitHub**: Commit documentação em `/docs`

### **Fase 2: Infraestrutura e Configuração (Prompts 2-4)**
1. ✅ **Local**: Executar `10_INFRA_NASP` → gera scripts de auto-config
2. ✅ **Local**: Executar `11_ANSIBLE_INVENTORY` → gera inventory e playbooks base
3. ✅ **Local**: Executar `12_PRE_FLIGHT` → gera scripts de validação
4. ✅ **GitHub**: Commit scripts e playbooks em `/ansible`, `/scripts`

### **Fase 3: Desenvolvimento de Módulos (Prompts 5-11)**
1. ✅ **Local**: Executar prompts `20_SEM_CSMF` até `26_ADAPTER_NASP`
2. ✅ **Local**: Desenvolver código dos módulos TriSLA
3. ✅ **GitHub**: Commits incrementais em `/apps`

### **Fase 4: Observabilidade (Prompts 12-14)**
1. ✅ **Local**: Executar prompts `30_OBSERVABILITY_OTLP` até `32_DASHBOARDS_GRAFANA`
2. ✅ **GitHub**: Commit configs em `/monitoring`

### **Fase 5: Testes (Prompts 15-17)**
1. ✅ **Local**: Executar `40_UNIT_TESTS` → gera testes unitários
2. ✅ **Local**: Executar `41_INTEGRATION_TESTS` → gera testes de integração
3. ✅ **Local**: Executar `42_E2E_TESTS` → gera testes end-to-end
4. ✅ **GitHub**: Commit testes em `/tests`
5. ⚠️ **Nota**: Testes podem ser executados localmente (Docker/K3s) ou no NASP após deploy

### **Fase 6: CI/CD e Empacotamento (Prompts 18-23)**
1. ✅ **Local**: Executar prompts `50_*` até `53_*` → gera workflows CI/CD
2. ✅ **Local**: Executar `60_HELM_CHART` → gera Helm charts
3. ✅ **Local**: Executar `61_HELM_VALIDATION` → gera scripts de validação
4. ✅ **GitHub**: Commit workflows em `/.github/workflows`, charts em `/helm`
5. ✅ **GitHub Actions**: Execução automática (build, push para GHCR)

### **Fase 7: Deploy (Prompts 24-27) - GERAÇÃO DE INSTRUÇÕES**
1. ✅ **Local**: Executar `62_DEPLOY_STAGE` → gera playbooks/instruções para stage
2. ✅ **Local**: Executar `63_DEPLOY_QA` → gera playbooks/instruções para QA
3. ✅ **Local**: Executar `64_DEPLOY_NASP` → **gera playbooks Ansible e instruções manuais para deploy no NASP**
4. ✅ **Local**: Executar `65_ROLLBACK_STRATEGY` → gera scripts de rollback
5. ✅ **GitHub**: Commit playbooks em `/ansible`, instruções em `/docs`

### **Fase 8: DEPLOY REAL NO NASP** (Execução dos artefatos gerados)

**Agora sim, executar no NASP usando os artefatos do GitHub:**

1. 🖥️ **No NASP (node1 ou node2)**:
   ```bash
   # Clonar ou fazer pull do repositório
   git clone https://github.com/abelisboa/TriSLA.git
   cd TriSLA
   
   # Opção A: Executar playbook Ansible
   cd ansible
   ansible-playbook -i inventory.ini deploy-trisla-nasp.yml
   
   # Opção B: Seguir instruções manuais
   # (documentação gerada pelos prompts em /docs)
   ```

2. 🖥️ **Validação no NASP**:
   - Executar scripts de pré-flight gerados
   - Validar deploy com Helm
   - Testar interfaces I-01 a I-07
   - Importar dashboards Grafana

---

## 🎯 CHECKLIST PRÉ-EXECUÇÃO

Antes de iniciar a execução dos prompts, verificar:

### **Ambiente Local:**
- [ ] Git configurado e repositório clonado
- [ ] IDE/Editor configurado
- [ ] Docker instalado (opcional, para testes locais)
- [ ] Acesso ao repositório GitHub/GHCR

### **Ambiente NASP:**
- [ ] Acesso SSH ao node1 (`192.168.10.16`)
- [ ] `kubectl` configurado com kubeconfig do NASP
- [ ] `helm` instalado no node1
- [ ] Autenticação GHCR configurada no node1
- [ ] Ansible configurado (se necessário)
- [ ] Script `trisla_nasp_env.sh` disponível no node1

### **Conectividade:**
- [ ] Rede acessível ao NASP
- [ ] Porta 22 (SSH) acessível
- [ ] Porta 6443 (Kubernetes API) acessível (se necessário)

---

## 🔄 FLUXO LOCAL → GITHUB → NASP

### **1. Do Local para o GitHub:**

```bash
# No ambiente local, após executar prompts:

# 1. Adicionar arquivos gerados
git add .

# 2. Commit com mensagem descritiva
git commit -m "feat: adiciona módulo SEM-CSMF (prompt 20)"

# 3. Push para GitHub (apenas conteúdo público!)
git push origin main

# ⚠️ IMPORTANTE: Nunca commitar secrets, senhas, ou dados sensíveis
# Usar variáveis de ambiente ou secrets do GitHub
```

### **2. Do GitHub para o NASP:**

#### **Opção A: Via Ansible (Recomendado)**

**Executando playbook localmente (conecta ao NASP via SSH):**
```bash
# No ambiente local
cd TriSLA/ansible
ansible-playbook -i inventory.ini deploy-trisla-nasp.yml
```

**Executando playbook no NASP (após clonar repositório):**
```bash
# No NASP (node1), via SSH
ssh usuario@192.168.10.16

# Clonar repositório
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA/ansible

# Executar playbook
ansible-playbook -i inventory.ini deploy-trisla-nasp.yml
```

#### **Opção B: Via Instruções Manuais**

```bash
# No NASP (node1), via SSH
ssh usuario@192.168.10.16

# Clonar repositório
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA

# Seguir instruções em /docs/DEPLOY_NASP.md
# (gerado pelo prompt 64_DEPLOY_NASP)
cat docs/DEPLOY_NASP.md

# Executar scripts de instalação
./scripts/deploy.sh
```

### **3. Coletar Informações do NASP (para análise local):**

```bash
# No ambiente local, coletar logs/configs do NASP
scp usuario@192.168.10.16:/var/log/trisla/* ./logs/

# Exportar estado do cluster
ssh usuario@192.168.10.16 "kubectl get all -n trisla -o yaml" > nasp-state.yaml
```

---

## 📌 NOTAS IMPORTANTES

1. **Nunca executar prompts fora de ordem** - A sequência garante dependências
2. **Sempre validar localmente antes de executar no NASP** - Reduz riscos
3. **Manter sincronização Git** - Todos os artefatos devem estar versionados
4. **Documentar mudanças no NASP** - Anotar configurações manuais necessárias
5. **Backup antes de deploy** - Sempre ter plano de rollback

---

## 🚀 INÍCIO RÁPIDO

### **Passo 1: Preparar Ambiente Local**

```bash
# 1. Clonar repositório (se ainda não tiver)
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA

# 2. Configurar Git (se necessário)
git config user.name "Seu Nome"
git config user.email "seu.email@exemplo.com"

# 3. Criar branch de desenvolvimento (opcional)
git checkout -b desenvolvimento
```

### **Passo 2: Executar Prompts Localmente**

```bash
# Todos os prompts são executados localmente
# Seguir ordem em 01_ORDEM_EXECUCAO.md

# Exemplo: Executar prompt 00
# (usar o conteúdo de 00_PROMPT_MASTER_PLANEJAMENTO.md)

# Após gerar código/configs:
git add .
git commit -m "feat: resultado do prompt 00"
git push origin desenvolvimento
```

### **Passo 3: Deploy no NASP (após todos os prompts)**

```bash
# No NASP (node1), via SSH
ssh usuario@192.168.10.16

# Clonar repositório (ou fazer pull se já existir)
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA

# Executar playbook Ansible ou seguir instruções manuais
cd ansible
ansible-playbook -i inventory.ini deploy-trisla-nasp.yml
```

### **Estrutura Esperada no GitHub:**

```
TriSLA/
├── .github/
│   └── workflows/          # CI/CD (prompts 50-53)
├── ansible/                # Playbooks (prompts 11, 24-26)
│   ├── inventory.ini
│   └── deploy-trisla-nasp.yml
├── apps/                   # Módulos TriSLA (prompts 20-26)
│   ├── sem-csmf/
│   ├── ml-nsmf/
│   └── ...
├── configs/                # Configurações
├── docs/                   # Documentação (prompt 00, 24-26)
│   └── DEPLOY_NASP.md
├── helm/                   # Helm charts (prompt 60)
├── monitoring/             # Observabilidade (prompts 30-32)
├── scripts/                # Scripts diversos (prompts 10, 12, 23, 27)
└── tests/                  # Testes (prompts 40-42)
```

---

---

## 📌 RESUMO EXECUTIVO

### **Princípio Fundamental:**
✅ **TODOS os 27 prompts são executados LOCALMENTE**  
✅ **Código gerado é publicado no GitHub** (https://github.com/abelisboa/TriSLA)  
✅ **Deploy no NASP é feito a partir do GitHub** usando Ansible ou instruções manuais

### **Não fazer:**
❌ Executar prompts diretamente no NASP  
❌ Commitar secrets ou dados sensíveis no GitHub  
❌ Fazer deploy sem ter código versionado no GitHub

### **Fazer:**
✅ Executar todos os prompts localmente  
✅ Commitar código público no GitHub  
✅ Usar playbooks Ansible ou instruções manuais para deploy  
✅ Manter documentação atualizada

---

**Última atualização**: Fluxo Local → GitHub → NASP  
**Repositório**: https://github.com/abelisboa/TriSLA  
**Ambiente NASP**: node1 - 192.168.10.16, node2 (interface my5g)

