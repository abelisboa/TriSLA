# Monitoring View - SLA Dashboard

## Overview

The Monitoring View provides real-time visibility into SLA operations, including decision statistics, service type distribution, and detailed SLA history with XAI explanations.

## Components

### SLAListPanel

Located at: `src/components/SLAList/SLAListPanel.tsx`

Features:

- **Statistics Cards**: Total SLAs, Accepted, Rejected, Renegotiation
- **Pie Chart**: SLA distribution by decision (ACCEPT/REJECT/RENEG)
- **Bar Chart**: SLA distribution by service type (eMBB/URLLC/mMTC)
- **SLA History Table**: Expandable rows with XAI details

### Real-time Monitoring

Located at: `src/components/Monitoring/Monitoring.tsx`

Displays real-time metrics:

- Latency (ms)
- Throughput (Mbps)
- Packet Loss (%)
- SLA Compliance (%)

## Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/sla-dashboard` | SLAListPanel | SLA overview and history |
| `/monitoring` | Monitoring | Real-time metrics |

## Navigation

Access via sidebar menu:
- **SLA Dashboard**: Shows SLA statistics and history
- **Monitoramento**: Shows real-time network metrics

## Data Sources

### SLA History

```
GET /api/v1/sla/history
```

Returns:
```json
{
  "slas": [
    {
      "sla_id": "sla-123",
      "service_type": "eMBB",
      "decision": "ACCEPT",
      "timestamp": "2026-01-31T00:00:00Z",
      "tx_hash": "0x...",
      "block_number": 101,
      "xai": { ... }
    }
  ]
}
```

### Real-time Metrics

```
GET /api/v1/metrics/realtime
WebSocket: ws://localhost:8080/ws/metrics
```

## Charts Library

Uses [Recharts](https://recharts.org/) for data visualization:

- `PieChart`: Decision distribution
- `BarChart`: Service type distribution
- `LineChart`: Latency over time
- `AreaChart`: Throughput and compliance

## Scientific Requirement

Graphs and visualizations are **fundamental for the Results Chapter** of the TriSLA research project. They provide:

1. **Visual evidence** of system behavior
2. **Quantitative metrics** for evaluation
3. **Comparative analysis** capabilities
