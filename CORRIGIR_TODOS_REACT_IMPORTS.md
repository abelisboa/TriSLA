# ✅ Corrigir Todos os Imports do React

## ❌ Problema

Múltiplos arquivos estão dando erro "React is not defined":
- ✅ App.tsx - CORRIGIDO
- ✅ Layout.tsx - CORRIGIDO  
- ❌ Dashboard.tsx - FALTANDO
- ❌ Metrics.tsx - FALTANDO
- ❌ SlicesManagement.tsx - FALTANDO
- ❌ MetricCard.tsx - FALTANDO

## ✅ Solução: Adicionar Import React em Todos

### Opção 1: Script Automático (WSL)

```bash
cd ~/trisla-dashboard-local/frontend

cat > fix-react.sh << 'EOF'
#!/bin/bash
FILES=(
    "src/pages/Dashboard.tsx"
    "src/pages/Metrics.tsx"
    "src/pages/SlicesManagement.tsx"
    "src/components/MetricCard.tsx"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ] && ! grep -q "^import React" "$file"; then
        sed -i '1i import React from '\''react'\''' "$file"
        echo "✅ Corrigido: $file"
    fi
done
EOF

chmod +x fix-react.sh
./fix-react.sh
```

### Opção 2: Manual (WSL)

Execute no **WSL**:

```bash
cd ~/trisla-dashboard-local/frontend

# Dashboard.tsx
sed -i '1i import React from '\''react'\''' src/pages/Dashboard.tsx

# Metrics.tsx
sed -i '1i import React from '\''react'\''' src/pages/Metrics.tsx

# SlicesManagement.tsx
sed -i '1i import React from '\''react'\''' src/pages/SlicesManagement.tsx

# MetricCard.tsx
sed -i '1i import React from '\''react'\''' src/components/MetricCard.tsx
```

### Opção 3: Copiar do Windows

```bash
cd ~/trisla-dashboard-local
./scripts-wsl/copy-from-windows.sh
```

## ✅ Verificação

Depois de corrigir, recarregue a página no navegador (F5).

O erro "React is not defined" não deve mais aparecer no console.

## 📝 Arquivos que Precisam de React

Qualquer arquivo `.tsx` que usa JSX precisa de `import React from 'react'`:

- ✅ `src/App.tsx`
- ✅ `src/components/Layout.tsx`
- ✅ `src/components/MetricCard.tsx`
- ✅ `src/pages/Dashboard.tsx`
- ✅ `src/pages/Metrics.tsx`
- ✅ `src/pages/SlicesManagement.tsx`

---

**Execute a Opção 2 no WSL para corrigir tudo de uma vez!**





