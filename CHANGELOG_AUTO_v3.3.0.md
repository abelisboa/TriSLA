# 🛰️ TriSLA v3.3.0 — Padronização de Nomenclatura

## ✳️ Alterações Principais

- Renomeação global: **trisla-portal → trisla**

- Padronização de nomes em Helm, Ansible, e documentação

- Atualização de variáveis: `trisla-portal.name` → `trisla.name`

- Atualização de paths: `helm/trisla-portal` → `helm/trisla`

- Atualização de labels e selectors nos templates

- Ajustes no README e valores NASP (`docs/config-examples/values-nasp.yaml`)

## 🧩 Estrutura Validada

- `helm/trisla/`

- `ansible/`

- `apps/`

- `monitoring/`

- `docs/`

- `fabric-network/`

- `grafana-dashboards/`

## ✅ Resultado Final

- 632 ocorrências substituídas

- Nenhum conflito restante nos arquivos críticos

- Charts e playbooks validados

- Repositório pronto para uso (v3.3.0)

