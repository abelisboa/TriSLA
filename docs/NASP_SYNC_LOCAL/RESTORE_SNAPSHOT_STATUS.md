# Status da Restauração do Snapshot NASP

**Data:** 2025-01-27  
**Script:** `restore_snapshot_nasp.sh`

## Execução do Script

O script de restauração foi criado e está pronto para execução. O script realiza as seguintes operações:

1. **Localização do Snapshot:**
   - Procura por arquivos `TriSLA_NASP_SNAPSHOT_*.tar.gz` em `/mnt/c/Users/USER/Documents`
   - Seleciona o snapshot mais recente (último na ordenação)

2. **Backup da Versão Atual:**
   - Se `TriSLA-clean` existir, faz backup para `TriSLA-clean_BACKUP_${TS}`

3. **Extração do Snapshot:**
   - Cria novo diretório `TriSLA-clean`
   - Extrai o snapshot usando `tar -xzf`

4. **Integração de Documentação:**
   - Copia `docs/NASP_SYNC/*` para `docs/NASP_SYNC_LOCAL/`

5. **Preparação do Ambiente Python:**
   - Cria/recria `.venv`
   - Atualiza pip
   - Instala dependências de `requirements.txt`

## Status Atual

**⚠️ ATENÇÃO:** O script foi criado, mas a execução completa requer que:
1. O arquivo de snapshot esteja presente em `/mnt/c/Users/USER/Documents/`
2. O usuário execute o script manualmente ou confirme a execução

## Próximos Passos

Para executar o script de restauração:

```bash
cd /mnt/c/Users/USER/Documents
bash restore_snapshot_nasp.sh
```

Ou execute diretamente:

```bash
cd /mnt/c/Users/USER/Documents
BASE_DIR="/mnt/c/Users/USER/Documents"
cd "$BASE_DIR"
TARBALL=$(ls -1 TriSLA_NASP_SNAPSHOT_*.tar.gz 2>/dev/null | sort | tail -1)
if [[ -z "$TARBALL" ]]; then
  echo "[ERRO] Nenhum arquivo de snapshot encontrado."
  exit 1
fi
echo "[OK] Snapshot encontrado: $TARBALL"
TS=$(date +%Y%m%d_%H%M%S)
if [[ -d TriSLA-clean ]]; then
  mv TriSLA-clean "TriSLA-clean_BACKUP_${TS}"
fi
mkdir -p TriSLA-clean
tar -xzf "$TARBALL" -C TriSLA-clean
cd TriSLA-clean
mkdir -p docs/NASP_SYNC_LOCAL
if [[ -d docs/NASP_SYNC ]]; then
  cp -r docs/NASP_SYNC/* docs/NASP_SYNC_LOCAL/
fi
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || true
echo "=== [LOCAL-RESTORE] Snapshot restaurado com sucesso ==="
```

## Verificação

Após a execução, verifique:

1. **Diretório restaurado:**
   ```bash
   ls -la /mnt/c/Users/USER/Documents/TriSLA-clean
   ```

2. **Documentação integrada:**
   ```bash
   ls -la /mnt/c/Users/USER/Documents/TriSLA-clean/docs/NASP_SYNC_LOCAL
   ```

3. **Ambiente Python:**
   ```bash
   cd /mnt/c/Users/USER/Documents/TriSLA-clean
   source .venv/bin/activate
   python --version
   ```

---

**Última atualização:** 2025-01-27
