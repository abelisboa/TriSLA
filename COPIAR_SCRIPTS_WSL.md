# 📋 Copiar Novos Scripts para WSL

Os novos scripts foram criados no Windows e precisam ser copiados para o WSL.

## 🔧 Solução Rápida

Execute no **WSL**:

```bash
cd ~/trisla-dashboard-local

# Copiar scripts do Windows para WSL
cp /mnt/c/Users/USER/Documents/trisla-deploy/trisla-dashboard-local/scripts-wsl/*.sh scripts-wsl/

# OU copiar tudo novamente
./scripts-wsl/copy-from-windows.sh
```

Depois:

```bash
chmod +x scripts-wsl/*.sh
./scripts-wsl/fix-404.sh
```

---

## 🔧 Solução Alternativa: Criar Script Diretamente no WSL

Execute este comando no WSL para criar o script diretamente:

```bash
cd ~/trisla-dashboard-local

cat > scripts-wsl/fix-404.sh << 'SCRIPT_EOF'
#!/bin/bash
# Script para corrigir erro 404 no frontend
set -e

cd ~/trisla-dashboard-local/frontend

echo "🔬 Corrigindo erro 404..."
echo ""

# Criar index.html se não existir
if [ ! -f "index.html" ]; then
    echo "📄 Criando index.html..."
    cat > index.html << 'EOF'
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TriSLA Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
    echo "✅ index.html criado"
else
    echo "✅ index.html já existe"
fi

# Parar processos antigos
echo ""
echo "🛑 Parando processos antigos..."
pkill -f vite 2>/dev/null || true
sleep 2

# Limpar cache
echo "🧹 Limpando cache..."
rm -rf node_modules/.vite dist 2>/dev/null || true

echo ""
echo "✅ Correções aplicadas!"
echo ""
echo "🚀 Execute: cd ~/trisla-dashboard-local/frontend && npm run dev"
SCRIPT_EOF

chmod +x scripts-wsl/fix-404.sh
```

Depois execute:

```bash
./scripts-wsl/fix-404.sh
```

---

## ✅ Verificação Rápida Manual

Ou execute diretamente no WSL:

```bash
cd ~/trisla-dashboard-local/frontend

# Verificar se index.html existe
ls -la index.html

# Se não existir, criar:
cat > index.html << 'EOF'
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TriSLA Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# Parar processos antigos
pkill -f vite

# Iniciar
npm run dev
```

---

## 🎯 Causa do Problema

O `index.html` não existe na raiz do `frontend/` no WSL. O Vite precisa deste arquivo para funcionar.

Após criar o `index.html`, o frontend deve funcionar corretamente.





