# ✅ Correção: React is not defined

## ❌ Problema

```
Uncaught ReferenceError: React is not defined
at App (App.tsx:8:3)
```

## ✅ Solução Aplicada

Adicionado `import React from 'react'` nos arquivos que usam JSX mas não importam React.

### Arquivos Corrigidos:

1. **`frontend/src/App.tsx`**
   - ✅ Adicionado: `import React from 'react'`

2. **`frontend/src/components/Layout.tsx`**
   - ✅ Adicionado: `import React from 'react'`

---

## 🔧 Aplicar no WSL

### Opção 1: Copiar Arquivos Corrigidos do Windows

```bash
cd ~/trisla-dashboard-local
./scripts-wsl/copy-from-windows.sh
```

### Opção 2: Corrigir Manualmente no WSL

```bash
cd ~/trisla-dashboard-local/frontend

# Corrigir App.tsx
sed -i '1i import React from '\''react'\''' src/App.tsx

# Corrigir Layout.tsx
sed -i '1i import React from '\''react'\''' src/components/Layout.tsx

# OU editar manualmente e adicionar no topo:
# import React from 'react'
```

### Opção 3: Reiniciar Vite (Hot Reload)

Se o Vite está rodando com hot reload, pode ser que já detecte a mudança. **Apenas recarregue a página no navegador (F5)**.

Se não funcionar:

```bash
cd ~/trisla-dashboard-local/frontend

# Parar Vite
pkill -f vite

# Reiniciar
npm run dev
```

---

## ✅ Verificação

Após aplicar as correções:

1. **Recarregue a página** (F5 no navegador)
2. **Verifique o console** (F12) - não deve mais ter o erro "React is not defined"
3. **A página deve renderizar** o dashboard corretamente

---

## 📝 Nota Técnica

Com React 17+ e `"jsx": "react-jsx"` no tsconfig.json, tecnicamente não é necessário importar React para JSX. No entanto, quando há problemas de bundling ou configuração, adicionar o import explícito resolve o problema.

---

## 🎯 Status

✅ **Problema corrigido!**

Execute os passos acima no WSL para aplicar as correções.





