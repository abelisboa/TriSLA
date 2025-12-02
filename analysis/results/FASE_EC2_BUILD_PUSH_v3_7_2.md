# FASE EC.2.5 — Build e Push das Imagens v3.7.2-nasp

**Data:** 2025-01-27  
**Versão:** v3.7.2-nasp

---

## ✅ Preparações Concluídas

### Script de Build
**Arquivo:** `scripts/build_and_push_all.sh`

**Status:** ✅ Script atualizado e pronto

**Características:**
- Aceita tag como parâmetro: `bash scripts/build_and_push_all.sh v3.7.2-nasp`
- Mapeamento de diretórios correto (`ml-nsmf` → `ml_nsmf`)
- Validação de GHCR_TOKEN
- Logging em `logs/build_and_push_*.log`

### Serviços que Serão Buildados

1. `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.2-nasp`
2. `ghcr.io/abelisboa/trisla-ml-nsmf:v3.7.2-nasp`
3. `ghcr.io/abelisboa/trisla-sem-csmf:v3.7.2-nasp` ⭐ **ATUALIZADO**
4. `ghcr.io/abelisboa/trisla-decision-engine:v3.7.2-nasp`
5. `ghcr.io/abelisboa/trisla-sla-agent-layer:v3.7.2-nasp`
6. `ghcr.io/abelisboa/trisla-ui-dashboard:v3.7.2-nasp`
7. `ghcr.io/abelisboa/trisla-nasp-adapter:v3.7.2-nasp`

---

## ⚠️ Execução Pendente

### Status Atual
**Build e Push:** ⚠️ **AGUARDANDO GHCR_TOKEN**

O script foi testado e está pronto, mas requer `GHCR_TOKEN` para autenticação no GitHub Container Registry.

### Comando para Executar

```bash
# 1. Exportar token do GHCR
export GHCR_TOKEN='seu_token_github_aqui'

# 2. Executar build e push
bash scripts/build_and_push_all.sh v3.7.2-nasp
```

### Como Obter o Token

1. Acesse: https://github.com/settings/tokens
2. Crie um token com permissões:
   - `write:packages` (para push)
   - `read:packages` (para pull)
3. Copie o token e exporte no ambiente bash

---

## ✅ Validações que Serão Realizadas

### Durante o Build
- [ ] Dockerfile do SEM-CSMF contém código atualizado
- [ ] Cliente HTTP (`decision_engine_client.py`) incluído na imagem
- [ ] `requirements.txt` contém `requests`
- [ ] Todos os diretórios de serviços existem
- [ ] Build de cada imagem sem erros

### Durante o Push
- [ ] Login no GHCR bem-sucedido
- [ ] Push de todas as imagens com tag `v3.7.2-nasp`
- [ ] Validação de que imagens foram publicadas

### Pós-Push
- [ ] Verificar que SEM-CSMF contém `decision_engine_client.py`
- [ ] Verificar que todas as 7 imagens foram publicadas
- [ ] Verificar que imagens estão acessíveis no GHCR

---

## 📋 Checklist de Build

### Pré-Build
- [x] Código do SEM-CSMF atualizado
- [x] Cliente HTTP implementado
- [x] `requirements.txt` validado
- [x] Teste local executado com sucesso
- [x] Script de build preparado

### Build (a executar)
- [ ] GHCR_TOKEN configurado
- [ ] Build de todas as imagens concluído
- [ ] Push de todas as imagens concluído
- [ ] Logs de build sem erros críticos

### Pós-Build
- [ ] Validação de imagens no GHCR
- [ ] Verificação de tags corretas
- [ ] Teste de pull das imagens

---

## 📝 Notas

1. **SEM-CSMF Atualizado:** A imagem `trisla-sem-csmf:v3.7.2-nasp` contém:
   - Cliente HTTP (`decision_engine_client.py`)
   - Código atualizado em `main.py`
   - Dependência `requests` no `requirements.txt`

2. **Compatibilidade:** As outras imagens são rebuildadas para manter consistência de versão, mas não contêm mudanças funcionais.

3. **Logs:** Os logs do build serão salvos em `logs/build_and_push_YYYYMMDD_HHMMSS.log`.

---

## 🚀 Próximos Passos

1. ⚠️ Configurar `GHCR_TOKEN` e executar build/push
2. ✅ Validação de imagens publicadas
3. ✅ Controle de versão Git (commit e tag)
4. ✅ Preparação para deploy NASP

---

**Status:** ⚠️ Script pronto — aguardando execução com GHCR_TOKEN

