# UI Dashboard - TriSLA

Interface web completa, moderna e responsiva para o TriSLA.

## Estrutura

```
apps/ui-dashboard/
├── src/
│   ├── App.tsx              # Componente principal
│   ├── components/
│   │   ├── TenantPortal/    # Portal do Tenant
│   │   ├── Monitoring/      # Monitoramento
│   │   ├── Administration/  # Administração
│   │   └── SlicesState/     # Estado dos Slices
│   ├── services/
│   │   └── api.ts           # Cliente API
│   ├── hooks/
│   └── utils/
├── public/
├── package.json
├── Dockerfile
└── README.md
```

## Funcionalidades

### 1. Tenant Portal
- Requisições de SLA
- Múltiplos tipos de slices simultâneos (eMBB, URLLC, mMTC)
- Status de requisições
- Histórico

### 2. Monitoramento
- Gráficos de SLOs em tempo real
- Observabilidade completa
- Métricas de performance
- Alertas

### 3. Administração
- Gestão de tenants/usuários
- Configuração de módulos
- Políticas e regras

### 4. Slices & Estado
- Visualização de slices
- Estado de módulos
- Comportamento em tempo real
- Health checks

## Tecnologias

- React 18+ com TypeScript
- Material-UI v5
- WebSocket para tempo real
- Chart.js / Recharts para gráficos

