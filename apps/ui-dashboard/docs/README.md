# TriSLA UI Dashboard

**Version:** 3.10.0-baseline

## Overview

The TriSLA UI Dashboard provides a web interface for managing and monitoring SLA (Service Level Agreement) operations in 5G network slicing environments.

## Features

### 1. Tenant Portal (`/tenant`)
- Create new SLA requests
- Select service type (eMBB, URLLC, mMTC)
- Define SLA requirements (latency, throughput, reliability)
- View request history

### 2. SLA Dashboard (`/sla-dashboard`)
- View SLA statistics (total, accepted, rejected, renegotiation)
- Pie chart: SLAs by decision
- Bar chart: SLAs by service type
- Detailed SLA history with expandable XAI explanations

### 3. XAI Visualization
- Decision indicator (ACCEPT/REJECT/RENEG)
- Risk score and level
- Confidence and viability scores
- Natural language justification
- Domain evaluation status
- Blockchain transaction confirmation

### 4. Real-time Monitoring (`/monitoring`)
- Latency metrics
- Throughput metrics
- Packet loss
- SLA compliance

### 5. Administration (`/administration`)
- System configuration

### 6. Slices State (`/slices`)
- Network slice status

## Technology Stack

- **React** 18.2
- **TypeScript** 5.2
- **Material-UI** 5.14
- **Recharts** 2.10 (charts)
- **React Router** 6.20
- **Axios** 1.6 (HTTP client)
- **Socket.io Client** 4.6 (WebSocket)
- **Vite** 5.0 (build tool)

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8080
```

## Project Structure

```
src/
├── App.tsx                 # Main application
├── main.tsx                # Entry point
├── services/
│   └── api.ts              # API client
└── components/
    ├── Layout.tsx          # Main layout with navigation
    ├── TenantPortal/       # SLA creation
    ├── SLAList/            # SLA dashboard
    │   └── SLAListPanel.tsx
    ├── XAI/                # Explainability
    │   └── XAIResultPanel.tsx
    ├── Monitoring/         # Real-time metrics
    ├── Administration/     # System config
    └── SlicesState/        # Slice status
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sla/history` | Get SLA history |
| GET | `/api/v1/metrics/realtime` | Get real-time metrics |
| POST | `/api/v1/intents` | Create SLA request |
| GET | `/api/v1/tenant/requests` | Get tenant requests |

## Screenshots

### SLA Dashboard
- Statistics cards showing total, accepted, rejected SLAs
- Charts for decision and service type distribution
- Expandable table with XAI details

### XAI Panel
- Decision with color-coded indicator
- Progress bars for risk, confidence, viability
- Domain badges
- Justification text
- Blockchain confirmation

## License

Apache 2.0
