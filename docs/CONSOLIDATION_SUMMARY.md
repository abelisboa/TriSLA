# Resumo da Consolidação do Fluxo de Deploy NASP

**Data:** 2025-01-22  
**Versão:** TriSLA v3.4.0

---

## Objetivo

Consolidar o fluxo oficial de deploy do TriSLA no ambiente NASP, garantindo:
- Um único arquivo canônico de valores para NASP: `helm/trisla/values-nasp.yaml`
- Scripts de automação coerentes
- Playbooks Ansible alinhados
- Documentação consistente

---

## Arquivos Modificados

### FASE 1 — Consolidar values-nasp.yaml

1. **`helm/trisla/values-nasp.yaml`** (CRIADO)
   - Arquivo canônico para deploy NASP
   - Baseado em `nasp/values-nasp.yaml` existente
   - Estrutura completa com todos os módulos

2. **`docs/nasp/values-nasp.yaml`** (CRIADO)
   - Template/exemplo oficial
   - Comentários claros indicando que é exemplo
   - Referência ao arquivo canônico

### FASE 2 — Alinhar Scripts Shell

3. **`scripts/deploy-trisla-nasp-auto.sh`**
   - Caminhos relativos ao repositório
   - Usa `helm/trisla/values-nasp.yaml` por padrão
   - Variável `TRISLA_VALUES_FILE` para override

4. **`scripts/deploy-trisla-nasp.sh`**
   - Default alterado para `helm/trisla/values-nasp.yaml`
   - Comentário explicando diferença NASP vs produção genérica

5. **`scripts/deploy-completo-nasp.sh`**
   - Atualizado para usar `helm/trisla/values-nasp.yaml`
   - Namespace corrigido: `trisla` (era `trisla-nsp`)
   - Release name: `trisla-portal`

6. **`scripts/prepare-nasp-deploy.sh`**
   - Verifica `helm/trisla/values-nasp.yaml` em vez de `values-production.yaml`
   - Mensagens atualizadas

7. **`scripts/configure-nasp-values.sh`**
   - Escreve em `helm/trisla/values-nasp.yaml`
   - Cria arquivo a partir de template se não existir

8. **`scripts/pre-check-nasp.sh`**
   - Caminho corrigido para `helm/trisla/values-nasp.yaml`

9. **`scripts/discover_nasp_endpoints.sh`**
   - Referência atualizada para `helm/trisla/values-nasp.yaml`

10. **`scripts/discover-nasp-endpoints.sh`**
    - Referência atualizada para `helm/trisla/values-nasp.yaml`

11. **`scripts/discover-nasp-services.sh`**
    - Referência atualizada para `helm/trisla/values-nasp.yaml`

12. **`scripts/update-nasp-config.sh`**
    - Escreve em `helm/trisla/values-nasp.yaml`

13. **`scripts/update-endpoints-discovered.sh`**
    - Referência atualizada para `helm/trisla/values-nasp.yaml`

14. **`scripts/fill_values_production.sh`**
    - Suporta NASP via `TRISLA_ENV=nasp`
    - Para NASP: preenche `helm/trisla/values-nasp.yaml`
    - Para produção genérica: preenche `helm/trisla/values-production.yaml`

### FASE 3 — Alinhar Playbooks Ansible

15. **`ansible/playbooks/deploy-trisla-nasp.yml`**
    - Variável `values_file` aponta para `values-nasp.yaml` por padrão
    - Release name configurável: `trisla-portal` (padrão)
    - Mensagens de erro atualizadas

### FASE 4 — Alinhar Documentação NASP

16. **`docs/nasp/NASP_DEPLOY_RUNBOOK.md`**
    - Todas as referências atualizadas para `helm/trisla/values-nasp.yaml`
    - Instruções claras sobre arquivo canônico vs template

17. **`docs/nasp/NASP_DEPLOY_GUIDE.md`**
    - Seção 7.1 atualizada com instruções claras
    - Comandos helm atualizados para usar `values-nasp.yaml`

18. **`docs/nasp/NASP_PREDEPLOY_CHECKLIST_v2.md`**
    - Seção 3.1 renomeada para "helm/trisla/values-nasp.yaml"
    - Todas as referências atualizadas

19. **`docs/nasp/NASP_PREDEPLOY_CHECKLIST_v3.4.md`**
    - Caminhos corrigidos para `helm/trisla/values-nasp.yaml`
    - Release name: `trisla-portal`

20. **`docs/nasp/NASP_CONTEXT_REPORT.md`**
    - Comandos atualizados para usar `values-nasp.yaml`

### FASE 5 — Alinhar Documentação Geral

21. **`docs/deployment/README_OPERATIONS_PROD.md`**
    - Seção 7.3 expandida explicando os 3 arquivos values
    - Clarificação: values.yaml (base), values-production.yaml (produção genérica), values-nasp.yaml (NASP)

22. **`docs/deployment/DEVELOPER_GUIDE.md`**
    - Seção 13.2 atualizada com distinção NASP vs produção genérica

23. **`docs/deployment/VALUES_PRODUCTION_GUIDE.md`**
    - Nota no topo sobre NASP usar `values-nasp.yaml`

---

## Convenções Estabelecidas

### Arquivos Values

1. **`helm/trisla/values.yaml`**
   - Base genérica/default
   - Para desenvolvimento e testes locais

2. **`helm/trisla/values-production.yaml`**
   - Produção genérica (fora NASP)
   - Para ambientes de produção que não sejam NASP-UNISINOS

3. **`helm/trisla/values-nasp.yaml`** ⭐
   - **Arquivo canônico para deploy NASP**
   - Template em: `docs/nasp/values-nasp.yaml`

### Release Name

- **Padrão para NASP:** `trisla-portal`
- Configurável via variável `trisla_helm_release` (Ansible) ou `TRISLA_HELM_RELEASE` (scripts)

### Namespace

- **Padrão:** `trisla`
- Configurável via variável `trisla_namespace` (Ansible) ou `TRISLA_NAMESPACE` (scripts)

---

## Fluxo Oficial de Deploy NASP

### Passo 1: Preparar valores

```bash
# Opção 1: Usar script guiado
export TRISLA_ENV=nasp
./scripts/fill_values_production.sh

# Opção 2: Copiar template e editar manualmente
cp docs/nasp/values-nasp.yaml helm/trisla/values-nasp.yaml
vim helm/trisla/values-nasp.yaml
```

### Passo 2: Validar configuração

```bash
# Validar Helm chart
helm lint ./helm/trisla

# Dry-run
helm template trisla-portal ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug
```

### Passo 3: Deploy

```bash
# Opção 1: Script automatizado (recomendado)
./scripts/deploy-trisla-nasp-auto.sh

# Opção 2: Script manual
./scripts/deploy-trisla-nasp.sh --all

# Opção 3: Helm direto
helm upgrade --install trisla-portal ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m

# Opção 4: Ansible
ansible-playbook -i ansible/inventory.yaml \
  ansible/playbooks/deploy-trisla-nasp.yml
```

---

## Arquivos que o Operador Deve Editar

**ANTES do deploy, o operador deve editar:**

1. **`helm/trisla/values-nasp.yaml`** (obrigatório)
   - Substituir todos os placeholders `<...>` por valores reais
   - Endpoints NASP
   - IPs de nodes
   - Secrets (JWT, PostgreSQL, etc.)

**NÃO editar:**
- `docs/nasp/values-nasp.yaml` (é apenas template)
- `helm/trisla/values.yaml` (base genérica)
- `helm/trisla/values-production.yaml` (produção genérica, não NASP)

---

## Comandos de Validação

```bash
# 1. Validar estrutura do repositório
./scripts/validate-helm.sh

# 2. Validar Helm chart
helm lint ./helm/trisla

# 3. Validar values-nasp.yaml
helm template trisla-portal ./helm/trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --debug

# 4. Verificar pré-requisitos NASP
./scripts/pre-check-nasp.sh
```

---

## Comandos de Instalação/Atualização

```bash
# Instalação inicial
helm upgrade --install trisla-portal ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --create-namespace \
  --wait \
  --timeout 15m

# Atualização
helm upgrade trisla-portal ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

---

## Checklist de Pré-Deploy

Consulte: `docs/nasp/NASP_PREDEPLOY_CHECKLIST_v3.4.md`

Principais itens:
- [ ] `helm/trisla/values-nasp.yaml` preenchido
- [ ] Todos os placeholders substituídos
- [ ] Helm chart validado
- [ ] Dry-run executado com sucesso
- [ ] Secret GHCR criado no namespace `trisla`
- [ ] StorageClass configurado
- [ ] Namespace `trisla` existe ou será criado

---

## Notas Importantes

1. **Nunca commitar `helm/trisla/values-nasp.yaml` com valores reais** (deve estar no `.gitignore`)

2. **Sempre usar `helm/trisla/values-nasp.yaml` para deploy NASP**, não `values-production.yaml`

3. **O arquivo `docs/nasp/values-nasp.yaml` é apenas template** — não usar diretamente em comandos helm

4. **Release name padrão:** `trisla-portal` (não `trisla` ou `trisla-prod`)

5. **Namespace padrão:** `trisla` (não `trisla-nsp`)

---

## Próximos Passos Recomendados

1. Revisar `helm/trisla/values-nasp.yaml` e preencher com valores reais do NASP
2. Executar `./scripts/pre-check-nasp.sh` no node1 do NASP
3. Validar com `helm template` antes do deploy
4. Executar deploy usando script automatizado ou Helm direto
5. Verificar status dos pods após deploy

---

**Consolidação concluída em:** 2025-01-22  
**Status:** ✅ Completo

