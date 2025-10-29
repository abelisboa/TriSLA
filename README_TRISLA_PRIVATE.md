# 🚀 TriSLA — Trustworthy, Reasoned and Intelligent SLA-Aware Architecture for 5G/O-RAN

**Public Web Interface and Full Backend System for SLA-Aware Network Slicing Automation**

---

## 🧩 Overview

TriSLA (Trustworthy, Reasoned, Intelligent SLA-Aware Architecture) integrates Semantic Interpretation (SEM-NSMF), AI-based Decision (ML-NSMF), and Smart-Contract Enforcement (BC-NSSMF) to guarantee automated SLA validation, sustainability, and compliance in 5G/O-RAN environments.

The system is composed of modular microservices and can be deployed on any Kubernetes infrastructure — including NASP (Network Automation and Slicing Platform) clusters.

---

## ⚙️ Architecture Components

| Layer | Function | Module | Technologies |
|-------|-----------|---------|---------------|
| **Trustworthy** | Contract Execution | BC-NSSMF | Hyperledger Fabric 2.5 |
| **Reasoned** | Semantic Reasoning | SEM-NSMF | OWL + spaCy (pt_core_news_lg) |
| **Intelligent** | Predictive Decision | ML-NSMF | Scikit-Learn + SHAP |
| **Aware** | Observability | NWDAF-like | Prometheus + FastAPI |
| **Interface** | API + Web UI | TriSLA Portal | FastAPI + React |

---

## 🧱 Folder Structure

```
trisla/
├── apps/
│   ├── ai/ → ML-NSMF (Predictive Decision Engine)
│   ├── semantic/ → SEM-NSMF (Ontology + NLP)
│   ├── blockchain/ → BC-NSSMF (Hyperledger Fabric SDK)
│   ├── monitoring/ → NWDAF-like Metrics Collector
│   └── integration/ → Orchestration API (Decision Engine)
│
├── fabric-network/ → Hyperledger Fabric Network (CA, Peer, Orderer, Chaincode)
├── ansible/ → NASP Automation (Playbooks, Roles, Inventory)
├── helm/ → Helm Charts for Deployment
├── automation/ → CI/CD Pipelines for GHCR Publishing
├── scripts/ → Validation and Metrics Collection Tools
└── docs/ → Technical References and Evidences
```

---

## 🧰 Infrastructure Requirements

### Cluster Specification (2-Node Minimum)

| Node | Role | IP | OS | User | Resources |
|------|------|----|----|------|-----------|
| **node1** | Control-Plane + SMO | `<node1_ip>` | Ubuntu 22.04 | `<user>` | 8 vCPU / 16 GB RAM / 100 GB SSD |
| **node2** | Worker + Data-Plane | `<node2_ip>` | Ubuntu 22.04 | `<user>` | 8 vCPU / 16 GB RAM / 100 GB SSD |

**Requirements:**
- Docker ≥ 27.0, containerd active  
- kubectl, helm, and ansible installed  
- Calico or Cilium CNI  
- Synchronized NTP across nodes  

---

## 🗺️ Example Configuration Files

### 📄 `docs/config-examples/values-nasp.yaml`
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

### 📄 `docs/config-examples/hosts.ini`
```ini
[nodes]
node1 ansible_host=<node1_ip> ansible_user=<user>
node2 ansible_host=<node2_ip> ansible_user=<user>

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```

---

## ☁️ Deployment Workflow

### 1️⃣ Start the Fabric network
```bash
cd fabric-network
./scripts/start.sh
./scripts/createChannel.sh
./scripts/deployCC.sh
```

### 2️⃣ Build and push images
```bash
./automation/trisla_build_publish.py
```

### 3️⃣ Deploy on Kubernetes (NASP or other clusters)
```bash
helm upgrade --install trisla-portal ./helm/trisla-portal/ \
  -n trisla -f ./docs/config-examples/values-nasp.yaml \
  --atomic --cleanup-on-fail
```

### 4️⃣ Verify
```bash
kubectl get pods -n trisla
```

---

## 🧪 End-to-End Validation

### 1. Semantic Input
```bash
curl -X POST http://<node1_ip>:30173/semantic/interpret \
-H "Content-Type: application/json" \
-d '{"descricao":"remote surgery 5G"}'
```

### 2. AI Decision
```bash
curl -X POST http://<node1_ip>:30800/decision \
-H "Content-Type: application/json" \
-d '{"slice_type":"URLLC","qos":{"latency":5}}'
```

### 3. Blockchain Contract
```bash
curl -X POST http://<node1_ip>:30800/contracts/new \
-H "Content-Type: application/json" \
-d '{"sla_id":"SLA001","decision":true}'
```

### 4. Metrics
```bash
curl http://<node1_ip>:30800/metrics
```

---

## 🧠 Expected Results

| Component | Response | Example |
|-----------|----------|---------|
| SEM-NSMF | Slice type mapping | `{ "slice": "URLLC" }` |
| ML-NSMF | Decision output | `{ "viable": true }` |
| BC-NSSMF | Fabric registration | `{ "status": "registered in blockchain" }` |
| NWDAF-like | Observability | `{ "latency_ms": 5.2 }` |

---

## ⚠️ Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Parse error in tests | Invalid JSON | Validate using `jq .` |
| AI or Semantic timeout | Wrong URL in values-nasp.yaml | Verify module service DNS |
| Fabric not storing contracts | CA not started | Re-run start.sh |
| Metrics unavailable | Pod CrashLoopBackOff | Check logs via `kubectl logs` |

---

## 🧩 Integration Points

• **TriSLA Portal (Public Interface):**
→ https://github.com/abelisboa/TriSLA-Portal

• **GHCR Registry:**
→ ghcr.io/abelisboa/trisla-*

• **Ansible Automation:**
→ ansible/deploy_trisla_fabric.yml

---

## 📜 License

© 2025 — Research and Academic Use Only (PPGCA/UNISINOS)
Not for commercial deployment without written authorization.
