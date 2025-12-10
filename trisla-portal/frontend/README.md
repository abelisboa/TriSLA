# Frontend - TriSLA Observability Portal v4.0

Frontend desenvolvido com Next.js 15, Tailwind CSS e Shadcn/UI.

## 🚀 Instalação

```bash
cd frontend
npm install
```

## 🛠️ Desenvolvimento

```bash
npm run dev
```

Acesse [http://localhost:3000](http://localhost:3000)

## 📦 Build

```bash
npm run build
npm start
```

## 📁 Estrutura

```
src/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Overview
│   ├── modules/           # Módulos
│   ├── contracts/         # Contratos
│   ├── slas/              # Criação de SLAs
│   └── xai/               # XAI Viewer
├── components/
│   ├── ui/                # Componentes Shadcn/UI
│   └── layout/            # Layout components
├── lib/                    # Utilitários
│   ├── api.ts             # Cliente API
│   └── utils.ts            # Utilitários gerais
├── store/                  # Zustand stores
├── types/                  # TypeScript types
└── hooks/                  # React hooks
```

## 🎨 Tecnologias

- **Next.js 15** - Framework React
- **Tailwind CSS** - Estilização
- **Shadcn/UI** - Componentes UI
- **Zustand** - State management
- **Recharts** - Gráficos
- **TypeScript** - Tipagem

## 📱 Telas Implementadas

- ✅ Overview (`/`)
- ✅ Modules (`/modules`)
- ✅ Module Details (`/modules/[module]`)
- ✅ Contracts (`/contracts`)
- ✅ Contract Details (`/contracts/[id]`)
- ✅ SLA Creation - PLN (`/slas/create/pln`)
- ✅ XAI Viewer (`/xai`)

## 🔄 Próximas Telas

- [ ] Intents (`/intents`)
- [ ] Traces (`/traces`)
- [ ] SLOs (`/slos`)
- [ ] Logs (`/logs`)
- [ ] Contract Comparison (`/contracts/compare`)
- [ ] Contract Analytics (`/contracts/analytics`)
- [ ] SLA Creation - Template (`/slas/create/template`)
- [ ] SLA Batch Creation (`/slas/create/batch`)

## 🔌 API

O frontend consome a API em `http://localhost:8000` (configurável via `NEXT_PUBLIC_API_URL`).

## 📝 Notas

- Todas as telas incluem loading states e error handling
- Componentes reutilizáveis em `components/ui`
- Types compartilhados em `types/index.ts`
- API client centralizado em `lib/api.ts`







