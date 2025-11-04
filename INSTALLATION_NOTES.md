# TriSLA-Portal — Deployment (NASP)

## 1) Pré-requisitos (local)
- Docker + Docker Buildx
- Login no GHCR:
  ```bash
  export GHCR_USER=<seu_user>
  export GHCR_TOKEN=<seu_token_pat_com_scope_package>
  ./scripts/build_push.sh
  ```

## 2) Deploy no NASP
- Ajustar `ansible/hosts.ini` com IPs/usuários dos nodes
- Rodar:
  ```bash
  export GHCR_USER=<seu_user>
  export GHCR_TOKEN=<seu_token>
  ansible-playbook -i ansible/hosts.ini ansible/deploy_trisla_portal.yml
  ```

## 3) Verificação
- Ajustar `NODE_IP` em `scripts/verify.sh` e executar:
  ```bash
  ./scripts/verify.sh
  ```

## 4) Acesso
- API: `http://<NODE_IP>:30800/api/v1/health`
- UI: `http://<NODE_IP>:30173/`

---

**Nota:** Certifique-se de que o Helm está instalado no cluster e que os nós têm acesso ao GHCR (ou usar imagePullSecrets).
