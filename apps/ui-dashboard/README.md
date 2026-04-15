# UI Dashboard - TriSLA

Complete, modern, and responsive web interface for TriSLA.

## Structure

```
apps/ui-dashboard/
├── src/
│   ├── App.tsx              # Main component
│   ├── components/
│   │   ├── TenantPortal/    # Tenant portal
│   │   ├── Monitoring/      # Monitoring
│   │   ├── Administration/  # Administration
│   │   └── SlicesState/     # Slice state
│   ├── services/
│   │   └── api.ts           # API client
│   ├── hooks/
│   └── utils/
├── public/
├── package.json
├── Dockerfile
└── README.md
```

## Features

### 1. Tenant Portal
- SLA requests
- Múltiplos tipos de slices simultâneos (eMBB, URLLC, mMTC)
- Request status
- History

### 2. Monitoring
- Real-time SLO charts
- Observabilidade completa
- Performance metrics
- Alertas

### 3. Administration
- Tenant/user management
- Module configuration
- Políticas e regras

### 4. Slices & State
- Slice visualization
- Module state
- Comportamento em tempo real
- Health checks

## Technologies

- React 18+ com TypeScript
- Material-UI v5
- WebSocket para tempo real
- Chart.js / Recharts for charts

