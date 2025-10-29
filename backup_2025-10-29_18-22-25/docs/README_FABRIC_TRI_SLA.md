# TriSLA – Hyperledger Fabric (Dev → Produção)

## O que foi gerado
- Rede mínima Fabric (1 org, 1 peer, 1 orderer, 1 CA, CouchDB, CLI)
- Chaincode SLA (Go) com RegisterSLA/QuerySLA
- Scripts de automação: start.sh, createChannel.sh, deployCC.sh
- Connection profile (YAML) para o SDK do BC-NSSMF
- Ansible (esqueleto) para executar no NASP

## Como usar (local para versionar / NÃO executar aqui)
1) Faça o commit e push para GitHub:

```bash
git add .
git commit -m "Fabric real para TriSLA + Ansible"
git push origin main
```

2) No NASP (futuro), com o repositório em mãos:

```bash
cd ~/trisla-portal/ansible
ansible-playbook -i hosts.ini deploy_trisla_fabric.yml
```

3) Depois, atualize o BC-NSSMF (FastAPI) para apontar para:
`./fabric-network/config/connection-profile.yaml`
e usar `Org1MSP/Admin` (já previsto no exemplo).

## Observações
- Este setup é dev-friendly. Em produção, recomenda-se:
- múltiplas orgs/peers, Fabric-CA para orderer + orgs,
- external chaincode service (CCaas),
- políticas/ACLs adequadas, backups do MSP,
- observabilidade (operations endpoints e Prometheus).
