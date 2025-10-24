#!/bin/bash
################################################################################
# WU-002 — Comandos Rápidos para Deploy TriSLA@NASP
# Use este arquivo para copiar e colar comandos no terminal
################################################################################

# ═══════════════════════════════════════════════════════════════════════════
# 1. CONECTAR AO SERVIDOR NASP
# ═══════════════════════════════════════════════════════════════════════════

ssh porvir5g@node1


# ═══════════════════════════════════════════════════════════════════════════
# 2. CRIAR ESTRUTURA DE DIRETÓRIOS
# ═══════════════════════════════════════════════════════════════════════════

cd /home/porvir5g/gtp5g
mkdir -p trisla-nsp/{helm/deployments,scripts,docs/evidencias/WU-002_deploy_core,logs}
cd trisla-nsp


# ═══════════════════════════════════════════════════════════════════════════
# 3. TRANSFERIR ARQUIVOS (execute no seu computador local)
# ═══════════════════════════════════════════════════════════════════════════

# No Windows PowerShell ou Git Bash:
scp -r C:\Users\USER\Documents\trisla-deploy\helm\deployments\*.yaml porvir5g@node1:/home/porvir5g/gtp5g/trisla-nsp/helm/deployments/
scp C:\Users\USER\Documents\trisla-deploy\scripts\deploy_core.sh porvir5g@node1:/home/porvir5g/gtp5g/trisla-nsp/scripts/


# ═══════════════════════════════════════════════════════════════════════════
# 4. CONFIGURAR PERMISSÕES (no servidor NASP)
# ═══════════════════════════════════════════════════════════════════════════

cd /home/porvir5g/gtp5g/trisla-nsp
chmod +x scripts/deploy_core.sh


# ═══════════════════════════════════════════════════════════════════════════
# 5. VERIFICAR PRÉ-REQUISITOS
# ═══════════════════════════════════════════════════════════════════════════

# Verificar kubectl
kubectl version --client

# Verificar cluster
kubectl cluster-info

# Verificar nodes
kubectl get nodes

# Verificar/criar namespace
kubectl get namespace trisla-nsp || kubectl create namespace trisla-nsp


# ═══════════════════════════════════════════════════════════════════════════
# 6. EXECUTAR DEPLOY AUTOMATIZADO
# ═══════════════════════════════════════════════════════════════════════════

cd /home/porvir5g/gtp5g/trisla-nsp
./scripts/deploy_core.sh


# ═══════════════════════════════════════════════════════════════════════════
# 7. VERIFICAÇÃO PÓS-DEPLOY
# ═══════════════════════════════════════════════════════════════════════════

# Ver todos os pods
kubectl get pods -n trisla-nsp -o wide

# Ver serviços
kubectl get svc -n trisla-nsp

# Ver deployments
kubectl get deployments -n trisla-nsp

# Ver status detalhado
kubectl get all -n trisla-nsp


# ═══════════════════════════════════════════════════════════════════════════
# 8. TESTES DE COMUNICAÇÃO
# ═══════════════════════════════════════════════════════════════════════════

# Health check do SEM-NSMF
kubectl exec -n trisla-nsp deploy/trisla-semantic-layer -- curl -s http://localhost:8080/health

# Health check do ML-NSMF
kubectl exec -n trisla-nsp deploy/trisla-ai-layer -- curl -s http://localhost:8080/health

# Health check do BC-NSSMF
kubectl exec -n trisla-nsp deploy/trisla-blockchain-layer -- curl -s http://localhost:7070/health

# Teste de comunicação entre módulos
kubectl exec -n trisla-nsp deploy/trisla-integration-layer -- curl -s http://trisla-semantic:8080/health


# ═══════════════════════════════════════════════════════════════════════════
# 9. MONITORAMENTO E LOGS
# ═══════════════════════════════════════════════════════════════════════════

# Ver logs do SEM-NSMF
kubectl logs -n trisla-nsp deployment/trisla-semantic-layer --tail=50

# Ver logs do ML-NSMF
kubectl logs -n trisla-nsp deployment/trisla-ai-layer --tail=50

# Ver logs em tempo real
kubectl logs -n trisla-nsp -f deployment/trisla-ai-layer

# Ver eventos do namespace
kubectl get events -n trisla-nsp --sort-by='.lastTimestamp'

# Ver uso de recursos
kubectl top pods -n trisla-nsp


# ═══════════════════════════════════════════════════════════════════════════
# 10. COLETAR EVIDÊNCIAS MANUALMENTE (se necessário)
# ═══════════════════════════════════════════════════════════════════════════

cd /home/porvir5g/gtp5g/trisla-nsp/docs/evidencias/WU-002_deploy_core

# Salvar lista de pods
kubectl get pods -n trisla-nsp -o wide > pods_list.txt

# Salvar lista de serviços
kubectl get svc -n trisla-nsp -o wide > services_list.txt

# Salvar lista de deployments
kubectl get deployments -n trisla-nsp -o wide > deployments_list.txt

# Salvar todos os recursos
kubectl get all -n trisla-nsp > all_resources.txt


# ═══════════════════════════════════════════════════════════════════════════
# 11. TROUBLESHOOTING
# ═══════════════════════════════════════════════════════════════════════════

# Descrever um pod específico (substitua {pod-name})
kubectl describe pod -n trisla-nsp {pod-name}

# Ver logs de um pod com erro
kubectl logs -n trisla-nsp {pod-name} --previous

# Executar shell dentro de um pod
kubectl exec -it -n trisla-nsp {pod-name} -- /bin/sh

# Reiniciar um deployment
kubectl rollout restart deployment/trisla-semantic-layer -n trisla-nsp

# Ver status do rollout
kubectl rollout status deployment/trisla-semantic-layer -n trisla-nsp


# ═══════════════════════════════════════════════════════════════════════════
# 12. DEPLOY MANUAL (alternativa ao script)
# ═══════════════════════════════════════════════════════════════════════════

cd /home/porvir5g/gtp5g/trisla-nsp

# Deploy módulo por módulo
kubectl apply -f helm/deployments/trisla-semantic.yaml -n trisla-nsp
kubectl apply -f helm/deployments/trisla-ai.yaml -n trisla-nsp
kubectl apply -f helm/deployments/trisla-blockchain.yaml -n trisla-nsp
kubectl apply -f helm/deployments/trisla-integration.yaml -n trisla-nsp
kubectl apply -f helm/deployments/trisla-monitoring.yaml -n trisla-nsp

# Ou deploy de todos de uma vez
kubectl apply -f helm/deployments/ -n trisla-nsp


# ═══════════════════════════════════════════════════════════════════════════
# 13. CLEANUP / ROLLBACK (use com cuidado!)
# ═══════════════════════════════════════════════════════════════════════════

# Deletar todos os deployments
kubectl delete -f helm/deployments/ -n trisla-nsp

# Ou deletar recursos individuais
kubectl delete deployment trisla-semantic-layer -n trisla-nsp
kubectl delete deployment trisla-ai-layer -n trisla-nsp
kubectl delete deployment trisla-blockchain-layer -n trisla-nsp
kubectl delete deployment trisla-integration-layer -n trisla-nsp
kubectl delete deployment trisla-monitoring-layer -n trisla-nsp

# Deletar todo o namespace (CUIDADO: remove tudo!)
# kubectl delete namespace trisla-nsp


# ═══════════════════════════════════════════════════════════════════════════
# 14. VERIFICAÇÃO FINAL
# ═══════════════════════════════════════════════════════════════════════════

# Checklist visual
echo "=== CHECKLIST DE VALIDAÇÃO ==="
echo ""
echo "Pods em Running:"
kubectl get pods -n trisla-nsp | grep Running | wc -l
echo ""
echo "Total de pods:"
kubectl get pods -n trisla-nsp --no-headers | wc -l
echo ""
echo "Serviços criados:"
kubectl get svc -n trisla-nsp --no-headers | wc -l
echo ""
echo "Deployments ativos:"
kubectl get deployments -n trisla-nsp --no-headers | wc -l
echo ""

# Status completo
kubectl get all -n trisla-nsp


################################################################################
# FIM DOS COMANDOS RÁPIDOS
################################################################################




