# 🚀 TriSLA — Trustworthy, Reasoned, and Intelligent SLA-Aware Architecture for 5G/O-RAN

**Full AI-Driven, Ontology-Based, and Blockchain-Enabled SLA Orchestration Framework**

---

## 🧠 1️⃣ Overview

**TriSLA (Trustworthy, Reasoned, Intelligent SLA-Aware Architecture)** is a modular, SLA-aware system designed to ensure **semantic interpretation**, **intelligent decision-making**, and **automated contractual enforcement** of SLAs for **Network Slicing** in **5G/O-RAN** environments.

The proposal is validated on the **NASP (Network Automation and Slicing Platform)** infrastructure from **UNISINOS**.

---

## ⚙️ 2️⃣ Architecture and Components

| Pillar | Component | Module | Technology |
|--------|------------|---------|-------------|
| **Trustworthy** | Contract execution | **BC-NSSMF** | Hyperledger Fabric 2.5 |
| **Reasoned** | Semantic interpretation | **SEM-NSMF** | OWL + spaCy (pt_core_news_lg) |
| **Intelligent** | Predictive decision | **ML-NSMF** | Scikit-Learn + SHAP |
| **Aware** | Observability | **NWDAF-like** | Prometheus + FastAPI |
| **Interface** | Orchestration + UI | **TriSLA Portal** | FastAPI + React |

---

## 🧱 3️⃣ Repository Structure

```
trisla/
├── apps/
│   ├── ai/ → ML-NSMF (Predictive decision engine)
│   ├── semantic/ → SEM-NSMF (Ontology + NLP)
│   ├── blockchain/ → BC-NSSMF (Fabric SDK)
│   ├── monitoring/ → NWDAF-like (Observability)
│   └── integration/ → API Gateway / Decision Engine
│
├── fabric-network/ → Hyperledger Fabric network (CA, Peer, Orderer, Chaincode)
├── ansible/ → NASP automation (Playbooks, Inventory, Roles)
├── helm/ → Helm charts for deployment
├── automation/ → CI/CD + GHCR publishing scripts
├── scripts/ → Validation & metrics collection
└── docs/ → Technical evidence & reports
```

---

## 🧰 4️⃣ Infrastructure Requirements

### 🔹 Minimum 2-Node Cluster (NASP-Compatible Example)

| Node | Role | IP | OS | SSH User | Resources |
|------|------|----|----|-----------|-----------|
| **node1** | Control-Plane + SMO | `<node1_ip>` | Ubuntu 22.04 | `<user>` | 8 vCPU / 16 GB RAM / 100 GB SSD |
| **node2** | Worker + Data-Plane | `<node2_ip>` | Ubuntu 22.04 | `<user>` | 8 vCPU / 16 GB RAM / 100 GB SSD |

**Both nodes must have:**
- Docker ≥ 27 and containerd active  
- kubectl & helm configured with shared K8s context  
- Same CNI (Calico or Cilium)  
- NTP synchronization (critical for Fabric timestamps)

---

### 🔹 DNS / Hosts Configuration

`/etc/hosts` on each node:

```
<node1_ip> node1.cluster.local node1
<node2_ip> node2.cluster.local node2
```

### 🔹 SSH Access
```bash
ssh <user>@<node1_ip>
ssh <user>@<node2_ip>
```

Ansible automations use these credentials, defined in `ansible/group_vars/all.yml`.

---

## 🧩 5️⃣ Critical Configuration — values-nasp.yaml

⚠️ **This file defines internal pod communication.**  
Any wrong namespace, port, or URL will break TriSLA ↔ NASP interoperability.

```yaml
namespace: trisla
imagePullPolicy: IfNotPresent

environment:
  SEMANTIC_URL: "http://trisla-semantic.trisla.svc.cluster.local:8081"
  AI_URL: "http://trisla-ai.trisla.svc.cluster.local:8080"
  BLOCKCHAIN_URL: "http://trisla-blockchain.trisla.svc.cluster.local:8051"
  MONITORING_URL: "http://trisla-monitoring.trisla.svc.cluster.local:8090"

nodeSelectors:
  api: node1
  ui: node2

service:
  type: NodePort
  ports:
    api: 30800
    ui: 30173
```

### 🔍 Common Misconfigurations

| Issue | Impact | Fix |
|-------|--------|-----|
| Wrong namespace (default instead of trisla) | API cannot reach modules | Set `namespace: trisla` |
| Wrong port (8081 → 8080) | SEM-NSMF not responding | Check `SEMANTIC_URL` |
| Broken DNS | Pods unreachable | Run `kubectl exec curl <svc>` |
| NodePort outside range | UI inaccessible | Use 30000–32767 |
| Missing Fabric volume | Contracts not persisted | Mount `/var/hyperledger/production` |

---

## ☁️ 6️⃣ Ansible Playbooks — Automated NASP Deployment

| Playbook | Purpose |
|----------|---------|
| `01_install_dependencies.yml` | Installs Docker, Helm, dependencies |
| `02_clone_and_prepare.yml` | Clones repos, generates Fabric certs |
| `03_deploy_trisla.yml` | Deploys TriSLA modules via Helm |
| `04_verify_and_monitor.yml` | Health checks + metrics collection |

**Run example:**
```bash
ansible-playbook -i ansible/hosts.ini playbooks/03_deploy_trisla.yml
```

---

## 🧠 7️⃣ Hyperledger Fabric Initialization

```
fabric-network/
├── configtx.yaml
├── crypto-config.yaml
├── docker-compose.yaml
└── chaincode/sla_chaincode/
```

**Deploy sequence:**
```bash
cd fabric-network
./scripts/start.sh
./scripts/createChannel.sh
./scripts/deployCC.sh
docker ps | grep hyperledger
```

---

## 🧪 8️⃣ End-to-End Validation

### 1️⃣ Semantic Input
```bash
curl -X POST http://<NODE_IP>:30173/semantic/interpret \
-H "Content-Type: application/json" \
-d '{"descricao":"remote surgery 5G"}'
```

### 2️⃣ AI Decision
```bash
curl -X POST http://<NODE_IP>:30800/decision \
-H "Content-Type: application/json" \
-d '{"slice_type":"URLLC","qos":{"latency":5}}'
```

### 3️⃣ Blockchain Contract
```bash
curl -X POST http://<NODE_IP>:30800/contracts/new \
-H "Content-Type: application/json" \
-d '{"sla_id":"SLA001","decision":true}'
```

### 4️⃣ Metrics
```bash
curl http://<NODE_IP>:30800/metrics
```

---

## 📈 9️⃣ Expected Results

| Metric | Source | Expected Value | Validation |
|--------|--------|----------------|------------|
| URLLC Latency | NWDAF-like | 1 – 5 ms | `curl /metrics` |
| AI Decision | ML-NSMF | `true` | `POST /decision` |
| Fabric Contract | BC-NSSMF | `"registered"` | Fabric logs |
| Ontology Mapping | SEM-NSMF | `"critical latency"` | JSON output |

---

## ⚠️ 10️⃣ Common Issues

| Symptom | Cause | Solution |
|---------|------|----------|
| API OK but AI fails | Wrong AI_URL | Fix `values-nasp.yaml` |
| Contracts missing | Fabric CA not started | Restart Fabric stack |
| Metrics not updating | NWDAF CrashLoopBackOff | `kubectl logs` |
| Parse error | Bad JSON test data | Validate with `jq .` |

---

## 🧩 11️⃣ TriSLA Portal — Public Interface

**Public repository:**  
🔗 https://github.com/abelisboa/TriSLA-Portal

Contains UI + API + Helm chart.  
Communicates with core TriSLA modules via the NASP values configuration.

---

## 🪪 12️⃣ License & Usage

Restricted to academic research – PPGCA UNISINOS (2025).  
For public deployment, use the TriSLA Portal repository.

---

## ✅ Conclusion

This repository provides the complete, production-ready infrastructure to build, deploy, and validate TriSLA on any Kubernetes-compatible cluster, preserving full integration between AI, Ontology, Blockchain, and Automation via Ansible + Helm.
