# TriSLA Portal

## Overview

The TriSLA Portal provides a web-based interface for managing SLA requests and monitoring system status.

## Features

### Tenant Portal (/tenant)
- Create new SLA requests
- Select service type (eMBB, URLLC, mMTC)
- Define requirements (latency, throughput, reliability)
- View request history

### SLA Dashboard (/sla-dashboard)
- Statistics cards (Total, Accepted, Rejected)
- Decision distribution chart (pie)
- Service type distribution chart (bar)
- SLA history table with expandable XAI details

### Monitoring (/monitoring)
- Real-time latency metrics
- Throughput monitoring
- Packet loss tracking
- SLA compliance visualization

## XAI Visualization

Each SLA decision displays:

| Field | Description |
|-------|-------------|
| Decision | ACCEPT, REJECT, or RENEG |
| Risk Score | 0-100% probability of SLA violation |
| Risk Level | LOW, MEDIUM, or HIGH |
| Confidence | Model certainty |
| Viability Score | Overall feasibility |
| Justification | Human-readable explanation |
| Domains Evaluated | RAN, Transport, Core |
| TX Hash | Blockchain transaction |
| Block Number | Confirmation block |

## Technology

- React 18
- TypeScript 5
- Material-UI 5
- Recharts (visualization)
- React Router 6
- Axios (HTTP client)

## Configuration

Environment variables:

```env
VITE_API_BASE_URL=http://localhost:8080
```
