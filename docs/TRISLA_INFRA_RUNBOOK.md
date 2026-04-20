# TRISLA INFRASTRUCTURE RUNBOOK

## INCIDENTE: CNI / MULTUS — NODE1

### 1. CONTEXTO

Durante a operação do ambiente NASP + TriSLA, foi identificado um incidente
de infraestrutura relacionado à camada CNI (Multus), afetando a criação de pods.

### 2. SINTOMAS

- Pods em ContainerCreating
- Erro FailedCreatePodSandBox
- Eventos SandboxChanged em loop
- Backend/UI indisponíveis

### 3. EVIDÊNCIA

Erro observado:

Multus: error getting k8s client:
failed to get context for kubeconfig
/etc/cni/net.d/multus.d/multus.kubeconfig:
no such file or directory

### 4. CAUSA RAIZ

Arquivo crítico ausente:

/etc/cni/net.d/multus.d/multus.kubeconfig

Impacto:

- Falha de autenticação do Multus na API
- CNI não executa ADD
- kubelet não cria sandbox
- loop de SandboxChanged

### 5. DETECÇÃO

kubectl get events -A | grep -i multus

ssh node1
ls -l /etc/cni/net.d/multus.d/

### 6. CORREÇÃO

1. Gerar token:

kubectl create token multus -n kube-system --duration=8760h

2. Criar kubeconfig:

mkdir -p /etc/cni/net.d/multus.d

Criar arquivo multus.kubeconfig com:
- server: https://192.168.10.15:6443
- certificate-authority-data
- token gerado

3. Permissões:

chmod 600 multus.kubeconfig

4. Recriar pods:

kubectl delete pod -n trisla -l app=trisla-portal-backend
kubectl delete pod -n trisla -l app=trisla-ui-dashboard

### 7. VALIDAÇÃO

kubectl -n trisla get pods

kubectl -n trisla get endpoints trisla-portal-backend

kubectl exec -n trisla tmp-shell -- wget -qO- http://trisla-portal-backend:8001/health

### 8. PREVENÇÃO

- Não remover /etc/cni/net.d sem plano
- Validar multus.kubeconfig após qualquer intervenção
- Monitorar eventos CNI
- Renovar token periodicamente

### 9. LIÇÃO APRENDIDA

A instabilidade não foi causada pelo sistema operacional (Ubuntu 24.04),
mas por inconsistência na configuração do CNI (Multus).

### 10. CLASSIFICAÇÃO

INCIDENT_TYPE = CNI_MISCONFIGURATION  
ROOT_CAUSE = MISSING_MULTUS_KUBECONFIG  
STATUS = RESOLVED

