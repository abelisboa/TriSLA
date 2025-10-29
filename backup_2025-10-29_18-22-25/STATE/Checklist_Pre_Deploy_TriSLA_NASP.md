# 🧾 Checklist de Pré-Implantação — TriSLA@NASP
## Diagnóstico, Limpeza e Preparação Segura do Ambiente

---

## 🎯 Objetivo

Garantir que o **ambiente NASP** esteja limpo, estável e pronto para receber a implantação oficial da **TriSLA**, evitando conflitos com versões ou testes antigos.

---

## 🧩 1️⃣ Diagnóstico Geral do Cluster

> 📍 Execute no terminal do NASP (`root@node1` ou via SSH).

### 🔹 Verificar estado do cluster e nós
```bash
kubectl get nodes -o wide
kubectl get pods -A -o wide
```

### 🔹 Listar todos os namespaces
```bash
kubectl get ns
```

Procure namespaces suspeitos ou antigos como:
```
trisla
test
demo
old-trisla
```
✅ Mantenha apenas:
```
default
kube-system
nasp-core
nasp-oran
monitoring
```
⚠️ Avaliar: `trisla`, `test`, `demo` → candidatos à limpeza.

---

## 🧩 2️⃣ Diagnóstico Focado em Recursos TriSLA Antigos

```bash
kubectl get all -A | grep -i trisla
kubectl get pods -A | grep -i trisla
kubectl get deployments -A | grep -i trisla
kubectl get svc -A | grep -i trisla
kubectl get ingress -A | grep -i trisla
kubectl get cm -A | grep -i trisla
kubectl get secret -A | grep -i trisla
kubectl get pvc -A | grep -i trisla
kubectl get pv | grep -i trisla
```

Se encontrar qualquer vestígio, planeje a limpeza conforme as próximas seções.

---

## 🧹 3️⃣ Limpeza Controlada (Safe Reset)

### 🔹 Remover namespaces antigos da TriSLA
```bash
kubectl delete ns trisla
kubectl delete ns test-trisla
```

> ⚠️ **Atenção:** só execute após confirmar que não há dados necessários nesses namespaces.

### 🔹 Remover módulos TriSLA antigos
```bash
kubectl delete deployment -n <namespace> <deployment_name>
kubectl delete svc -n <namespace> <service_name>
kubectl delete pod -n <namespace> <pod_name>
kubectl delete cm -n <namespace> <configmap_name>
kubectl delete pvc -n <namespace> <pvc_name>
```

### 🔹 Limpar Helm releases antigas
```bash
helm list -A | grep -i trisla
helm uninstall trisla-core -n trisla-nsp
helm uninstall trisla-semantic -n trisla-nsp
```

---

## 📦 4️⃣ Volumes, ConfigMaps e Secrets

### 🔹 Persistent Volumes e Claims
```bash
kubectl get pv
kubectl get pvc -A
```
Remover volumes antigos:
```bash
kubectl delete pvc <nome> -n <namespace>
kubectl delete pv <nome>
```

### 🔹 ConfigMaps e Secrets
```bash
kubectl get cm -A | grep -i trisla
kubectl get secrets -A | grep -i trisla
kubectl delete cm <nome> -n <namespace>
kubectl delete secret <nome> -n <namespace>
```

---

## 🔄 5️⃣ Verificação do NASP Ativo

### 🔹 Conferir Helm releases e pods principais
```bash
helm list -A
kubectl get pods -n nasp-core
kubectl get pods -n nasp-oran
```
✅ Mantenha:
```
nasp-core
nasp-oran
monitoring
kube-system
default
```
🚫 Remova:
```
trisla
test
demo
old-trisla
```

---

## 🧱 6️⃣ Preparação para Nova Implantação TriSLA

### 🔹 Criar novo namespace limpo
```bash
kubectl create namespace trisla-nsp
```

### 🔹 Verificar contexto Kubernetes
```bash
kubectl config current-context
kubectl config get-contexts
kubectl config set-context --current --namespace=trisla-nsp
```

### 🔹 Atualizar Helm e repositórios
```bash
helm repo list
helm repo update
```

---

## 📊 7️⃣ Gerar Snapshot do Estado Atual (Pré-TriSLA)

Antes da instalação, gere um relatório completo para registro em `docs/evidencias/WU-000_pre_check/`.

```bash
kubectl get all -A > nasp_state_before_trisla.txt
kubectl get pvc -A >> nasp_state_before_trisla.txt
kubectl get pv >> nasp_state_before_trisla.txt
kubectl get secrets -A >> nasp_state_before_trisla.txt
kubectl get cm -A >> nasp_state_before_trisla.txt
kubectl get ingress -A >> nasp_state_before_trisla.txt
```

💾 **Salvar arquivo:**  
`/home/porvir5g/trisla-nasp/docs/evidencias/WU-000_pre_check/nasp_state_before_trisla.txt`

---

## 🧠 8️⃣ Recomendações Gerais

| Etapa | Ação |
|--------|------|
| Diagnóstico | Executar todos os comandos de listagem antes de apagar. |
| Limpeza | Remover apenas recursos antigos da TriSLA. |
| Segurança | Nunca apagar namespaces `nasp-*` ou `kube-system`. |
| Backup | Sempre salvar o snapshot antes da instalação. |
| Preparação | Criar namespace `trisla-nsp` limpo e configurado. |

---

## 🚀 9️⃣ Sequência Final Resumida

```bash
kubectl get ns
kubectl get all -A | grep -i trisla
helm list -A | grep -i trisla

# Revisar e limpar
kubectl delete ns trisla
kubectl delete ns test-trisla

# Preparar ambiente
kubectl create namespace trisla-nsp
kubectl get pods -n trisla-nsp
```

---

📅 **Data:** 2025‑10‑16  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
