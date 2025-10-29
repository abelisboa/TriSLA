# WU-002 — Deploy dos Módulos Centrais TriSLA@NASP
## Implantação Local dos Componentes SEM‑NSMF, ML‑NSMF e BC‑NSSMF

---

| Campo | Informação |
|--------|-------------|
| Data | 16/10/2025 |
| Responsável | Abel José Rodrigues Lisboa |
| Cluster | NASP – UNISINOS |
| Namespace | trisla-nsp |
| Objetivo | Realizar o deploy modular dos três componentes centrais da arquitetura TriSLA no NASP, validando a execução, comunicação interna e registro de evidências. |

---

## 🧩 1️⃣ Contexto

A arquitetura TriSLA é composta por três módulos principais que atuam de forma integrada:
1. **SEM‑NSMF (Semantic Network Slice Management Function)** — interpretação semântica e geração de NESTs.  
2. **ML‑NSMF (Machine Learning‑based NSMF)** — predição e decisão inteligente via IA explicável.  
3. **BC‑NSSMF (Blockchain‑enabled NSSMF)** — orquestração contratual e monitoramento descentralizado.

Nesta WU, os módulos serão implantados individualmente via **Helm Charts**, garantindo isolamento e validação independente antes da integração (WU‑003).

---

## ⚙️ 2️⃣ Pré‑Requisitos

| Item | Status |
|------|---------|
| WU‑000 — Pré‑Check do NASP | ✅ Concluído |
| WU‑001 — Bootstrap GitOps | ✅ Concluído |
| Namespace `trisla-nsp` ativo | ✅ Confirmado |
| Helm instalado e configurado | ✅ Validado |
| Acesso GitHub (repositório TriSLA@NASP) | ✅ Confirmado |

---

## 🧱 3️⃣ Estrutura dos Helm Charts

Os módulos estão organizados em sub‑charts dentro do repositório local:

```
helm/
 ├── trisla/
 │   ├── Chart.yaml
 │   ├── values.yaml
 │   └── charts/
 │        ├── sem-nsmf/
 │        ├── ml-nsmf/
 │        └── bc-nssmf/
```

> 💡 Cada subchart possui seu `deployment.yaml`, `service.yaml` e `configmap.yaml` específicos.

---

## 🚀 4️⃣ Deploy dos Módulos

### 🔹 4.1 SEM‑NSMF
```bash
helm install sem-nsmf ./helm/trisla/charts/sem-nsmf -n trisla-nsp
kubectl get pods -n trisla-nsp | grep sem
kubectl logs -n trisla-nsp deployment/sem-nsmf
```

### 🔹 4.2 ML‑NSMF
```bash
helm install ml-nsmf ./helm/trisla/charts/ml-nsmf -n trisla-nsp
kubectl get pods -n trisla-nsp | grep ml
kubectl logs -n trisla-nsp deployment/ml-nsmf
```

### 🔹 4.3 BC‑NSSMF
```bash
helm install bc-nssmf ./helm/trisla/charts/bc-nssmf -n trisla-nsp
kubectl get pods -n trisla-nsp | grep bc
kubectl logs -n trisla-nsp deployment/bc-nssmf
```

---

## 🔍 5️⃣ Verificação Pós‑Deploy

### 🔹 Checar status dos pods
```bash
kubectl get pods -n trisla-nsp -o wide
```

### 🔹 Validar serviços criados
```bash
kubectl get svc -n trisla-nsp
```

### 🔹 Confirmar comunicação interna
```bash
kubectl exec -n trisla-nsp <pod_sem-nsmf> -- ping -c 3 ml-nsmf
kubectl exec -n trisla-nsp <pod_ml-nsmf> -- curl http://bc-nssmf:8080/health
```

### 🔹 Registrar logs e métricas iniciais
```bash
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=sem-nsmf > docs/evidencias/WU-002_deploy_core/sem-nsmf.log
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=ml-nsmf > docs/evidencias/WU-002_deploy_core/ml-nsmf.log
kubectl logs -n trisla-nsp -l app.kubernetes.io/name=bc-nssmf > docs/evidencias/WU-002_deploy_core/bc-nssmf.log
```

---

## 📊 6️⃣ Estrutura de Evidências

Os resultados devem ser armazenados em:

```
docs/evidencias/WU-002_deploy_core/
 ├── sem-nsmf.log
 ├── ml-nsmf.log
 ├── bc-nssmf.log
 ├── kubectl_get_pods.txt
 ├── kubectl_get_svc.txt
 └── connectivity_test.txt
```

---

## ✅ 7️⃣ Critérios de Aceitação

| Critério | Status Esperado |
|-----------|------------------|
| Todos os pods `Running` e `Ready` | ✅ |
| Serviços internos (`ClusterIP`) acessíveis | ✅ |
| Comunicação interna entre módulos | ✅ |
| Logs gravados e sem erros críticos | ✅ |
| Evidências armazenadas em `docs/evidencias/WU-002_deploy_core/` | ✅ |

---

## 🧾 8️⃣ Conclusão

A execução da WU‑002 implanta e valida com sucesso os três módulos centrais da arquitetura TriSLA no NASP.  
Os componentes SEM‑NSMF, ML‑NSMF e BC‑NSSMF estão ativos e em comunicação interna dentro do namespace `trisla-nsp`.  
O ambiente está pronto para a **WU‑003 — Integração e Interoperabilidade com o NASP Core (O1, A1, E2, NWDAF)**.

📅 **Data:** 16/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
