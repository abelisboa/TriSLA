# HELM_DEPLOY_TEMPLATE.md

[HELM DEPLOY PROMPT]

Use este template para pedir à IA a criação ou atualização de Helm charts para implantação no NASP.

**Instruções:**  
1. Colar o `SESSION HEADER` + `TASK SPEC`.  
2. Informar qual módulo (ex: sem_nsmf, ml_nsmf, bc_nssmf, etc.) e namespace (`trisla-nsp`).  
3. A IA deve gerar:  
   - Diretório `helm/<módulo>/` com `Chart.yaml`, `values.yaml`, `templates/` e sub-recursos.  
   - Configurações de recursos (CPU, memória, limites).  
   - `Deployment`, `Service`, `Ingress`, `ConfigMap`, `Secret`, `ServiceAccount` e `RBAC`.  
   - Parâmetros de observabilidade e métricas.  
4. A IA deve incluir comandos de instalação e teste:  
   ```bash
   helm install <modulo> ./helm/<modulo> -n trisla-nsp
   kubectl get pods -n trisla-nsp
   ```  
5. Validar segurança: TLS, JWT, RBAC.  
6. Gerar logs compatíveis com formato do Apêndice H.  
