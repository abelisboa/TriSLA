# ✅ SOLUÇÃO DEFINITIVA - Terminações de Linha

## 🔧 Correção Aplicada

Os scripts foram corrigidos usando múltiplas abordagens para garantir conversão completa de CRLF para LF.

## 📋 Comandos de Teste

Execute estes comandos para verificar se está funcionando:

### 1. Verificar se o script pode ser executado

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
bash -n scripts/rebuild_venv.sh && echo "✅ Script válido"
```

### 2. Se ainda houver erro, execute a correção manual

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend

# Método 1: Usando Python
python3 -c "
with open('scripts/rebuild_venv.sh', 'rb') as f:
    content = f.read()
content = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
with open('scripts/rebuild_venv.sh', 'wb') as f:
    f.write(content)
print('✅ Corrigido')
"

# Método 2: Usando sed
sed -i 's/\r$//' scripts/rebuild_venv.sh scripts/validar_instalacao.sh

# Método 3: Usando tr
tr -d '\r' < scripts/rebuild_venv.sh > scripts/rebuild_venv.sh.tmp
mv scripts/rebuild_venv.sh.tmp scripts/rebuild_venv.sh

# Garantir permissões
chmod +x scripts/*.sh
```

### 3. Testar execução

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
bash scripts/rebuild_venv.sh
```

## 🛡️ Prevenção Futura

### Arquivo `.gitattributes` criado

O arquivo `.gitattributes` foi criado para garantir que todos os scripts `.sh` sempre usem LF, mesmo quando editados no Windows.

### Configurar Git globalmente

```bash
git config core.autocrlf input
```

Isso garante que:
- No checkout: CRLF → LF
- No commit: LF → LF (sem conversão)

## ✅ Status

- ✅ Scripts corrigidos
- ✅ `.gitattributes` criado
- ✅ Script Python de correção criado (`fix_all_line_endings.py`)

## 🚀 Próximo Passo

Execute o script de reconstrução:

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
bash scripts/rebuild_venv.sh
```

Se ainda houver problemas, execute a correção manual acima.

