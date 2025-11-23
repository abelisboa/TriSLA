#!/bin/bash
set -e

echo -e "\n========================="
echo -e "🔍 FASE 0 — PRÉ-CHECK NASP"
echo -e "=========================\n"

kubectl get nodes -o wide
echo ""

echo -e "\n==============================="
echo -e "🔧 FASE 1 — CRIAR STORAGECLASS"
echo -e "===============================\n"

echo "➡️ Verificando StorageClass existente..."
if kubectl get sc 2>/dev/null | grep -q .; then
    echo "✔️ StorageClass já existe, pulando instalação."
else
    echo "⚠️ Nenhum StorageClass encontrado — instalando NFS provisioner..."
    helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner || true
    helm repo update

    # ❗ ATENÇÃO: AJUSTAR IP DO NFS AQUI SE NECESSÁRIO
    NFS_SERVER="192.168.10.100"
    NFS_PATH="/export/k8s"

    echo "➡️ Instalando NFS provisioner no kube-system..."
    helm upgrade --install nfs-storage nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
        -n kube-system \
        --set nfs.server=${NFS_SERVER} \
        --set nfs.path=${NFS_PATH} \
        --set storageClass.name=nfs-storage \
        --set storageClass.defaultClass=true

    echo "✔️ StorageClass criado com sucesso."
fi

echo -e "\n==============================="
echo -e "🔧 FASE 2 — CORRIGIR COREDNS"
echo -e "===============================\n"

POD=$(kubectl get pod -n kube-system | grep coredns | grep Pending | awk '{print $1}')
if [ -n "$POD" ]; then
    echo "⚠️ CoreDNS pendente detectado → removendo pod: $POD"
    kubectl delete pod -n kube-system "$POD"
else
    echo "✔️ CoreDNS OK."
fi

echo -e "\n======================================"
echo -e "🔧 FASE 3 — HABILITAR NODE2 (UNCORDON)"
echo -e "======================================\n"

if kubectl get node node2 | grep -q SchedulingDisabled; then
    echo "⚠️ node2 está cordoned → habilitando..."
    kubectl uncordon node2
    echo "✔️ node2 habilitado para receber workloads."
else
    echo "✔️ node2 já está disponível."
fi

echo -e "\n====================================="
echo -e "🔧 FASE 4 — CRIAR NAMESPACE TRISLA"
echo -e "=====================================\n"

if kubectl get namespace trisla 2>/dev/null | grep -q trisla; then
    echo "✔️ Namespace trisla já existe."
else
    echo "➡️ Criando namespace trisla..."
    kubectl create namespace trisla
    echo "✔️ Namespace criado."
fi

echo -e "\n==========================================="
echo -e "🔧 FASE 5 — CRIAR SERVICEACCOUNT + RBAC"
echo -e "===========================================\n"

if kubectl get serviceaccount -n trisla trisla-sa 2>/dev/null | grep -q .; then
    echo "✔️ ServiceAccount trisla-sa já existe."
else
    echo "➡️ Criando SA trisla-sa..."
    kubectl create serviceaccount trisla-sa -n trisla
    echo "✔️ ServiceAccount criado."
fi

echo "➡️ Aplicando RBAC padrão..."
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: trisla-role
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: trisla-rolebinding
subjects:
  - kind: ServiceAccount
    name: trisla-sa
    namespace: trisla
roleRef:
  kind: ClusterRole
  name: trisla-role
  apiGroup: rbac.authorization.k8s.io
EOF

echo "✔️ RBAC aplicado."

echo -e "\n============================================"
echo -e "🔧 FASE 6 — VALIDAR PROMETHEUS/GRAFANA"
echo -e "============================================\n"

if kubectl get pods -n monitoring 2>/dev/null | grep -q "CrashLoopBackOff"; then
    echo "⚠️ Prometheus/Grafana com falhas detectadas."
    echo "➡️ Reinstalando kube-prometheus-stack…"

    helm uninstall monitoring -n monitoring || true
    sleep 3
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
    helm repo update

    helm upgrade --install monitoring \
        prometheus-community/kube-prometheus-stack \
        -n monitoring \
        --create-namespace

    echo "✔️ Prometheus stack reinstalado."
else
    echo "✔️ Monitoring stack está saudável."
fi

echo -e "\n==========================================="
echo -e "🔍 FASE 7 — VALIDAÇÃO FINAL DO CLUSTER"
echo -e "===========================================\n"

kubectl get sc
echo ""
kubectl get pods -A | grep -E "trisla|monitoring|coredns|kube|calico" || echo "Nenhum pod encontrado com esses filtros."
echo ""
kubectl top nodes || echo "⚠️ metrics-server ainda inicializando."
echo ""

echo -e "\n================================================="
echo -e "🎉 AMBIENTE NASP PRONTO PARA INSTALAÇÃO DO TRISLA"
echo -e "=================================================\n"

echo "➡️ Agora você pode rodar:"
echo "helm upgrade --install trisla-portal ./helm/trisla \\"
echo "  -n trisla -f ./helm/trisla/values-nasp.yaml \\"
echo "  --atomic --cleanup-on-fail"
echo ""