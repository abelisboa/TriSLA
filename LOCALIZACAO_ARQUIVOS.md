# 📁 Localização dos Arquivos - TriSLA Dashboard

## 📍 Diretório Raiz

```
C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local
```

---

## 📂 Estrutura Completa

### Backend
```
backend/
├── main.py              # API FastAPI (proxy Prometheus)
├── requirements.txt     # Dependências Python
└── venv/                # Virtual environment (criado após pip install)
```

### Frontend
```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.tsx      # Layout principal com navbar
│   │   └── MetricCard.tsx  # Card de métricas
│   ├── pages/
│   │   ├── Dashboard.tsx           # Dashboard principal
│   │   ├── Metrics.tsx             # Métricas detalhadas
│   │   └── SlicesManagement.tsx    # Gestão de slices
│   ├── services/
│   │   └── api.ts          # Cliente API
│   ├── App.tsx             # Router principal
│   ├── main.tsx            # Entry point React
│   └── index.css           # Estilos TailwindCSS
├── node_modules/           # Dependências instaladas
├── package.json            # Configuração npm
├── package-lock.json
├── vite.config.ts         # Config Vite
├── tailwind.config.js     # Config TailwindCSS
├── postcss.config.js
├── tsconfig.json          # Config TypeScript
├── tsconfig.node.json
└── index.html             # HTML base
```

### Scripts
```
scripts/
├── start-all.ps1          # Iniciar tudo (Windows)
├── start-ssh-tunnel.ps1   # Túnel SSH (Windows)
└── start-ssh-tunnel.sh    # Túnel SSH (Linux/WSL)
```

### Documentação
```
Raiz/
├── README.md              # Visão geral
├── SETUP.md               # Guia de setup
├── GUIA_INICIO_RAPIDO.md  # Início rápido
├── PRONTO_PARA_USAR.md    # Status atual
└── LOCALIZACAO_ARQUIVOS.md (este arquivo)
```

---

## 🗂️ Localização por Categoria

### Arquivos de Código Frontend
- **Componentes**: `frontend/src/components/`
- **Páginas**: `frontend/src/pages/`
- **Serviços**: `frontend/src/services/`
- **Config**: `frontend/` (vite.config.ts, tailwind.config.js, etc.)

### Arquivos de Código Backend
- **API**: `backend/main.py`
- **Dependências**: `backend/requirements.txt`

### Scripts de Automação
- **Windows**: `scripts/*.ps1`
- **Linux/WSL**: `scripts/*.sh`

---

## 🔍 Como Verificar Arquivos

### Ver todos os arquivos Python
```powershell
Get-ChildItem backend\*.py -Recurse
```

### Ver todos os arquivos TypeScript/React
```powershell
Get-ChildItem frontend\src\*.tsx,frontend\src\*.ts -Recurse
```

### Ver estrutura completa
```powershell
tree /F frontend\src
tree /F backend
```

---

## 📍 Caminhos Absolutos

- **Raiz do projeto**: `C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local`
- **Backend**: `C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local\backend`
- **Frontend**: `C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local\frontend`
- **Scripts**: `C:\Users\USER\Documents\trisla-deploy\trisla-dashboard-local\scripts`

---

## ✅ Verificação Rápida

```powershell
# Verificar estrutura
Get-ChildItem -Directory | Select-Object Name

# Verificar arquivos principais
Test-Path backend\main.py
Test-Path frontend\package.json
Test-Path scripts\start-all.ps1
```




