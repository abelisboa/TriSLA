# 🛰️ TriSLA v3.3.3  

### Uma Arquitetura SLA-Aware Baseada em IA, Ontologia e Contratos Inteligentes para Garantia de SLA em Redes 5G/O-RAN

---

##  **1. Visão Geral**

O **TriSLA (Trustworthy, Reasoned, and Intelligent SLA-Aware Architecture)** é uma arquitetura unificada voltada à **automação inteligente do ciclo de vida de SLAs** em redes **5G/O-RAN**, permitindo prever, aceitar, monitorar e auditar contratos de slice de rede.

É composta por três módulos principais:

- **SEM-NSMF (Ontologia e PLN)**  Interpreta pedidos de SLA em linguagem natural e converte para modelos técnicos (URLLC, eMBB, mMTC).  

- **ML-NSMF (IA Explicável)**  Prediz viabilidade de recursos e decisão de aceitação.  

- **BC-NSSMF (Blockchain)**  Valida e audita SLAs por meio de contratos inteligentes.

Pode ser executada em **modo local (Docker Compose)** ou **modo NASP (Kubernetes + Ansible + Helm)**.

---

##  **2. Requisitos e Dependências**

| Componente | Versão mínima | Descrição |
|-------------|---------------|------------|
| **Ubuntu** | 22.04 LTS+ | Sistema base recomendado |
| **Docker / BuildKit** | 27+ | Build local e GHCR |
| **Node.js / npm** | 18+ | Frontend (UI e Dashboard) |
| **Python** | 3.10+ | Backend AI, Semantic, Blockchain |
| **Helm** | 3.14+ | Orquestração Kubernetes |
| **kubectl** | 1.28+ | Gerenciamento de pods e namespaces |
| **Ansible** | 2.16+ | Automação multi-nó no NASP |
| **Prometheus / Grafana** | Latest | Monitoramento |
| **GitHub CLI / ghcr.io login** | 2.45+ | Publicação de imagens |
| **Kubernetes Cluster** |  2 nós | Implantação NASP (node1/node2) |

---

##  **3. Estrutura e Arquitetura do Projeto**

```
TriSLA/
 apps/                      # Módulos principais
    api/                   # API Gateway (FastAPI)
    ui/                    # Interface Web (React)
    semantic/              # SEM-NSMF (Ontologia + PLN)
    ai/                    # ML-NSMF (IA Explicável)
    blockchain/            # BC-NSSMF (Hyperledger Fabric)
    monitoring/            # NWDAF-like (Prometheus)
    dashboard/             # Visualização e métricas
        backend/
        frontend/

 ansible/                   # Automação NASP
    playbooks/
       deploy_trisla_portal.yaml
    inventory.yml
    roles/

 helm/                      # Helm Charts para Kubernetes
    trisla/
    trisla-dashboard/
    sla-agents/
    decision-engine/

 monitoring/                # Configuração Prometheus / Grafana
 fabric-network/            # Hyperledger Fabric (chaincode, config)
 docs/                      # Documentação técnica
 tools/                     # Scripts auxiliares (validação, logs)
 docker-compose.yaml        # Execução local completa
```

---

##  **4. Instalação e Configuração**

###  **Execução Local (Docker Compose)**

```bash
# Clonar o repositório
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA

# Build das imagens
./release/build.sh

# Subir stack completa
docker compose up -d
```

**Acesse:**

- UI  http://localhost:5173
- API  http://localhost:8000/docs
- Dashboard  http://localhost:5174
- Grafana  http://localhost:3000

###  **Execução NASP (Ansible + Helm)**

#### 4.1 Inventário (inventory.yml)

```yaml
all:
  hosts:
    node1:
      ansible_host: <NODE1_IP>
      ansible_user: <ANSIBLE_USER>
    node2:
      ansible_host: <NODE2_IP>
      ansible_user: <ANSIBLE_USER>
  children:
    trisla_nodes:
      hosts:
        node1:
        node2:
```

#### 4.2 Playbook de Deploy (deploy_trisla_portal.yaml)

```yaml
- name: Deploy TriSLA Portal no NASP
  hosts: trisla_nodes
  become: yes
  tasks:
    - name: Copiar chart TriSLA
      copy:
        src: ./helm/trisla/
        dest: /home/<USER>/tri-charts/trisla
    - name: Aplicar helm install
      command: >
        helm upgrade --install trisla ./tri-charts/trisla
        -n trisla --create-namespace
        -f /home/<USER>/tri-charts/trisla/values-nasp.yaml
```

#### 4.3 Exemplo de values-nasp.yaml

```yaml
global:
  imagePullSecrets: 
    - name: ghcr-secret
  domain: nasp.example.com

image:
  repository: ghcr.io/abelisboa/trisla-api
  tag: "latest"

service:
  type: ClusterIP
  port: 8000

env:
  - name: SEMANTIC_ENDPOINT
    value: "http://trisla-semantic.trisla.svc.cluster.local:8001"
  - name: AI_ENDPOINT
    value: "http://trisla-ai.trisla.svc.cluster.local:8002"
  - name: ENABLE_BLOCKCHAIN
    value: "true"
```

#### 4.4 Execução via Ansible

```bash
cd ansible
ansible-playbook -i inventory.yml playbooks/deploy_trisla_portal.yaml
```

**Saída esperada:**

```
TASK [Copiar chart TriSLA] ************************************
ok: [node1]
ok: [node2]

TASK [Aplicar helm install] ***********************************
changed: [node1]
changed: [node2]

PLAY RECAP ****************************************************
node1 : ok=3 changed=1 failed=0
node2 : ok=3 changed=1 failed=0
```

---

##  **5. Dependências de Cada Módulo (requirements.txt)**

###  apps/api/requirements.txt

```
fastapi==0.111.0
uvicorn==0.29.0
pydantic==2.7.1
requests==2.32.0
```

###  apps/semantic/requirements.txt

```
spacy==3.7.4
rdflib==7.0.0
flask==3.0.2
```

###  apps/ai/requirements.txt

```
scikit-learn==1.5.1
pandas==2.2.2
joblib==1.4.2
numpy==1.26.4
```

###  apps/blockchain/requirements.txt

```
flask==3.0.2
requests==2.32.0
cryptography==42.0.7
```

---

##  **6. Observabilidade e Dashboard**

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

**Login:**

- Usuário: admin
- Senha: admin

**Métricas monitoradas:**

- SLA Aceitos / Rejeitados
- Latência / Throughput API
- Utilização CPU e RAM
- Blockchain Transactions

---

##  **7. Validação e Resultados Esperados**

```bash
./tools/validate_trisla.sh
```

**Saída esperada:**

```
 API online
 Semantic operacional
 AI conectado
 Blockchain validado
 Prometheus ativo
```

Os resultados experimentais utilizados estão documentados em:
`docs/evidencias/WU-005_Avaliacao_Experimental_TriSLA.md`

---

##  **8. Troubleshooting e Diagnóstico**

| Erro | Causa | Solução |
|------|-------|---------|
|  Namespace ausente | Deploy incompleto | `kubectl create ns trisla` |
|  API 502 | Variável VITE_API_URL incorreta | Corrigir `.env` |
|  Blockchain não conecta | peer inativo | `docker restart blockchain` |
|  Grafana vazio | CRDs ausentes | `kubectl apply -f monitoring/crds/` |

---

##  **9. Autor e Licença**

**Abel Lisboa**  
Mestrando em Computação Aplicada  UNISINOS  
 abelisboa@gmail.com

 https://github.com/abelisboa

---

**UNIVERSIDADE DO VALE DO RIO DOS SINOS  UNISINOS**  
**UNIDADE ACADÊMICA DE PESQUISA E PÓS-GRADUAÇÃO**  
**PROGRAMA DE PÓS-GRADUAÇÃO EM COMPUTAÇÃO APLICADA  PPGCA**  
São Leopoldo  Rio Grande do Sul  Brasil

**TriSLA: Uma Arquitetura SLA-Aware Baseada em IA, Ontologia e Contratos Inteligentes para Garantia de SLA em Redes 5G/O-RAN**

Dissertação apresentada como requisito parcial para obtenção do título de Mestre em Computação Aplicada.

---

**Licença:** MIT  veja LICENSE

**Repositório oficial:** https://github.com/abelisboa/TriSLA# README atualizado

